# Published adapters

The final QLoRA adapters are published in the [CiTIUS Language Technologies Lab
organization](https://huggingface.co/citiusLTL) on Hugging Face. The model
repositories contain the final adapter weights, tokenizer files, a model card,
the training configuration, and MIRAGE evaluation results. They do not include
the base model weights.

| Base model | Training collection | Hugging Face repository | MIRAGE accuracy |
|---|---|---|---:|
| Gemma 3 4B-IT | Drugs-SFT | [gemma-3-4b-it-drugs-sft-qlora](https://huggingface.co/citiusLTL/gemma-3-4b-it-drugs-sft-qlora) | 49.05% |
| Gemma 3 4B-IT | WHO-SFT | [gemma-3-4b-it-who-sft-qlora](https://huggingface.co/citiusLTL/gemma-3-4b-it-who-sft-qlora) | 47.62% |
| Gemma 3 4B-IT | Drugs+WHO-SFT | [gemma-3-4b-it-drugs-who-sft-qlora](https://huggingface.co/citiusLTL/gemma-3-4b-it-drugs-who-sft-qlora) | 44.64% |
| Qwen2.5 0.5B-Instruct | Drugs-SFT | [qwen2.5-0.5b-instruct-drugs-sft-qlora](https://huggingface.co/citiusLTL/qwen2.5-0.5b-instruct-drugs-sft-qlora) | 33.43% |
| Qwen2.5 0.5B-Instruct | WHO-SFT | [qwen2.5-0.5b-instruct-who-sft-qlora](https://huggingface.co/citiusLTL/qwen2.5-0.5b-instruct-who-sft-qlora) | 33.84% |

All reported values use the complete MIRAGE benchmark (7,663 questions) with
constrained answer selection. See [experiments.md](experiments.md) for the
shared training configuration and [reproduction.md](reproduction.md) for the
execution workflow.

## Loading an adapter

Each repository is a PEFT/QLoRA adapter. Load the compatible 4-bit base model
declared in its `adapter_config.json` and then apply the adapter with PEFT. The
model cards include a minimal loading example.

## Intended use

These resources are research artifacts. They are not validated for clinical use
and must not be used for diagnosis, treatment, or medical decision-making.
