import argparse
import inspect
import math
from pathlib import Path

import unsloth
from unsloth import FastLanguageModel, is_bfloat16_supported
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig


def format_chat_examples(examples, tokenizer):
    texts = []
    for messages in examples["messages"]:
        texts.append(
            tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=False,
            )
        )
    return {"text": texts}


def filter_supported_kwargs(cls, kwargs):
    signature = inspect.signature(cls.__init__)
    return {key: value for key, value in kwargs.items() if key in signature.parameters}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="data/drugs_sft.jsonl")
    parser.add_argument(
        "--model",
        default="unsloth/gemma-3-4b-it-unsloth-bnb-4bit",
        help="Hugging Face model id supported by Unsloth.",
    )
    parser.add_argument("--output-dir", default="outputs/gemma3_4b_drugs_lora")
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument("--epochs", type=float, default=2.0)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=16)
    parser.add_argument("--lora-dropout", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=3407)
    args = parser.parse_args()

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_r,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=args.seed,
    )

    dataset = load_dataset("json", data_files=args.dataset, split="train")
    dataset = dataset.map(
        lambda examples: format_chat_examples(examples, tokenizer),
        batched=True,
        remove_columns=dataset.column_names,
    )

    effective_batch_size = args.batch_size * args.grad_accum
    steps_per_epoch = math.ceil(len(dataset) / effective_batch_size)
    warmup_steps = max(1, int(steps_per_epoch * args.epochs * 0.03))

    sft_config_kwargs = {
        "output_dir": args.output_dir,
        "num_train_epochs": args.epochs,
        "per_device_train_batch_size": args.batch_size,
        "gradient_accumulation_steps": args.grad_accum,
        "learning_rate": args.learning_rate,
        "warmup_steps": warmup_steps,
        "logging_steps": 10,
        "save_strategy": "epoch",
        "optim": "adamw_8bit",
        "weight_decay": 0.01,
        "lr_scheduler_type": "linear",
        "seed": args.seed,
        "fp16": not is_bfloat16_supported(),
        "bf16": is_bfloat16_supported(),
        "report_to": "none",
        "dataset_text_field": "text",
        "packing": False,
    }

    sft_config_signature = inspect.signature(SFTConfig.__init__)
    if "max_length" in sft_config_signature.parameters:
        sft_config_kwargs["max_length"] = args.max_seq_length
    else:
        sft_config_kwargs["max_seq_length"] = args.max_seq_length

    sft_config = SFTConfig(**filter_supported_kwargs(SFTConfig, sft_config_kwargs))

    trainer_kwargs = {
        "model": model,
        "processing_class": tokenizer,
        "tokenizer": tokenizer,
        "train_dataset": dataset,
        "dataset_text_field": "text",
        "max_seq_length": args.max_seq_length,
        "packing": False,
        "args": sft_config,
    }

    trainer = SFTTrainer(
        **filter_supported_kwargs(SFTTrainer, trainer_kwargs),
    )

    trainer.train()

    output_dir = Path(args.output_dir)
    model.save_pretrained(output_dir / "adapter")
    tokenizer.save_pretrained(output_dir / "adapter")
    print(f"Saved LoRA adapter to {output_dir / 'adapter'}")


if __name__ == "__main__":
    main()
