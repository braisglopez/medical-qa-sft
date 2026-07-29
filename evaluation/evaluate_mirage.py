import argparse
import json
import random
import re
from pathlib import Path

import unsloth
from unsloth import FastLanguageModel
import torch
from tqdm import tqdm


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def is_question_record(value):
    return (
        isinstance(value, dict)
        and isinstance(value.get("question"), str)
        and value.get("options") is not None
        and value.get("answer") is not None
    )


def normalize_options(options):
    if isinstance(options, dict):
        pairs = [(str(key).strip(), value) for key, value in options.items()]
        keys_are_letters = all(
            len(key) == 1 and key.upper() in LETTERS for key, _ in pairs
        )
        if keys_are_letters:
            return {key.upper(): str(value) for key, value in pairs}
        return {
            LETTERS[index]: str(value)
            for index, (_, value) in enumerate(pairs)
            if index < len(LETTERS)
        }

    if isinstance(options, list):
        return {
            LETTERS[index]: str(value)
            for index, value in enumerate(options)
            if index < len(LETTERS)
        }

    return {}


def normalize_answer(answer, options):
    if isinstance(answer, int):
        if 0 <= answer < len(options):
            return LETTERS[answer]
        if 1 <= answer <= len(options):
            return LETTERS[answer - 1]

    answer_text = str(answer).strip()
    answer_upper = answer_text.upper()
    if answer_upper in options:
        return answer_upper

    for key, value in options.items():
        if answer_text.lower() == str(value).strip().lower():
            return key

    return answer_upper


def normalize_item(item):
    options = normalize_options(item.get("options"))
    normalized = dict(item)
    normalized["options"] = options
    normalized["answer"] = normalize_answer(item.get("answer"), options)
    return normalized


def as_dataset(value):
    if isinstance(value, list):
        rows = [normalize_item(item) for item in value if is_question_record(item)]
        return rows if rows else None

    if isinstance(value, dict):
        if is_question_record(value):
            return [normalize_item(value)]

        for key in ("data", "test", "dev", "validation", "examples", "questions"):
            rows = as_dataset(value.get(key))
            if rows:
                return rows

        values = list(value.values())
        if values and all(is_question_record(item) for item in values):
            return [normalize_item(item) for item in values]

    return None


def collect_datasets(value, path, datasets):
    rows = as_dataset(value)
    if rows:
        dataset_name = ".".join(path) if path else "benchmark"
        datasets[dataset_name] = rows
        return

    if isinstance(value, dict):
        for key, child in value.items():
            collect_datasets(child, path + [str(key)], datasets)


def normalize_benchmark(raw):
    datasets = {}
    collect_datasets(raw, [], datasets)
    if not datasets:
        raise ValueError(
            "Could not find datasets in MIRAGE benchmark JSON. "
            "Expected records with question, options, and answer fields."
        )
    return datasets


def build_prompt(item):
    options = item.get("options") or {}
    options_text = "\n".join(
        f"{key}. {options[key]}"
        for key in sorted(options, key=lambda key: LETTERS.index(key))
    )
    return (
        "Answer this medical multiple-choice question. "
        "Return only the letter of the best option.\n\n"
        f"Question: {item['question']}\n"
        f"Options:\n{options_text}\n\n"
        "Answer:"
    )


def extract_answer(text, options):
    text = text.strip()
    if not text:
        return ""

    valid_letters = set(options)
    first_token = re.match(r"^\s*([A-Za-z])(?:[\.\)\]:,\s]|$)", text)
    if first_token and first_token.group(1).upper() in valid_letters:
        return first_token.group(1).upper()

    for key, value in options.items():
        if text.lower().startswith(str(value).strip().lower()):
            return key

    valid_pattern = "|".join(re.escape(letter) for letter in sorted(valid_letters))
    match = re.search(rf"\b({valid_pattern})\b", text, flags=re.IGNORECASE)
    return match.group(1).upper() if match else ""


def generate_answer(model, tokenizer, prompt, options, max_seq_length):
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=max_seq_length,
    ).to(model.device)

    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=8,
            do_sample=False,
            temperature=None,
            top_p=None,
        )
    decoded = tokenizer.decode(
        output[0][inputs["input_ids"].shape[-1] :],
        skip_special_tokens=True,
    )
    return extract_answer(decoded, options), decoded.strip()


def flatten_token_ids(value):
    if hasattr(value, "tolist"):
        value = value.tolist()

    while (
        isinstance(value, (list, tuple))
        and len(value) == 1
        and isinstance(value[0], (list, tuple))
    ):
        value = value[0]

    if not isinstance(value, (list, tuple)):
        return [int(value)]
    return [int(token_id) for token_id in value]


def candidate_token_ids(tokenizer, letter):
    for variant in (letter, f" {letter}"):
        ids = flatten_token_ids(
            tokenizer(
                variant,
                add_special_tokens=False,
            )["input_ids"]
        )
        if len(ids) == 1:
            return {ids[0]}

    ids = flatten_token_ids(
        tokenizer(letter, add_special_tokens=False)["input_ids"]
    )
    return {ids[0]} if ids else set()


def select_answer_constrained(model, tokenizer, prompt, options, max_seq_length):
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=max_seq_length,
    ).to(model.device)

    token_to_letters = {}
    for letter in options:
        for token_id in candidate_token_ids(tokenizer, letter):
            token_to_letters.setdefault(token_id, []).append(letter)

    allowed_token_ids = sorted(token_to_letters)
    if not allowed_token_ids:
        return "", "constrained: no valid candidate token ids"

    def allowed_tokens_fn(batch_id, input_ids):
        return allowed_token_ids

    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=1,
            do_sample=False,
            temperature=None,
            top_p=None,
            prefix_allowed_tokens_fn=allowed_tokens_fn,
            return_dict_in_generate=True,
            output_scores=True,
        )

    generated_token_id = int(output.sequences[0, -1])
    decoded = tokenizer.decode([generated_token_id], skip_special_tokens=True)
    candidate_letters = token_to_letters.get(generated_token_id, [])
    pred = extract_answer(decoded, options)
    if not pred and len(candidate_letters) == 1:
        pred = candidate_letters[0]

    scores = output.scores[0][0]
    allowed_scores = " ".join(
        f"{tokenizer.decode([token_id])!r}={float(scores[token_id]):.4f}[tok={token_id}]"
        for token_id in allowed_token_ids
    )
    return pred, (
        f"constrained token={decoded!r}[tok={generated_token_id}] "
        f"candidates={allowed_scores}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", required=True, help="Path to MIRAGE benchmark.json")
    parser.add_argument(
        "--model",
        default="unsloth/gemma-3-4b-it-unsloth-bnb-4bit",
        help="Base model or saved LoRA adapter directory.",
    )
    parser.add_argument("--output", default="tfm_llm/outputs/mirage_predictions.json")
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional deterministic random sample size per dataset.",
    )
    parser.add_argument("--sample-seed", type=int, default=3407)
    parser.add_argument(
        "--selection-mode",
        choices=("generate", "constrained"),
        default="generate",
        help="generate parses model text; constrained permits only valid option letters.",
    )
    args = parser.parse_args()

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )
    FastLanguageModel.for_inference(model)

    raw = json.loads(Path(args.benchmark).read_text(encoding="utf-8"))
    datasets = normalize_benchmark(raw)
    print(
        "Loaded datasets: "
        + ", ".join(f"{name}={len(rows)}" for name, rows in datasets.items())
    )

    all_predictions = {}
    total_correct = 0
    total_count = 0

    for dataset_name, rows in datasets.items():
        if args.limit and args.limit < len(rows):
            rows = random.Random(f"{args.sample_seed}:{dataset_name}").sample(
                rows,
                args.limit,
            )
        predictions = []
        correct = 0

        for item in tqdm(rows, desc=dataset_name):
            gold = str(item.get("answer", "")).strip().upper()
            prompt = build_prompt(item)
            options = item.get("options") or {}
            if args.selection_mode == "constrained":
                pred, raw_generation = select_answer_constrained(
                    model,
                    tokenizer,
                    prompt,
                    options,
                    args.max_seq_length,
                )
            else:
                pred, raw_generation = generate_answer(
                    model,
                    tokenizer,
                    prompt,
                    options,
                    args.max_seq_length,
                )
            is_correct = pred == gold
            correct += int(is_correct)
            predictions.append(
                {
                    "question": item.get("question"),
                    "options": item.get("options"),
                    "gold": gold,
                    "prediction": pred,
                    "raw_generation": raw_generation,
                    "selection_mode": args.selection_mode,
                    "correct": is_correct,
                }
            )

        accuracy = correct / len(rows) if rows else 0.0
        total_correct += correct
        total_count += len(rows)
        all_predictions[dataset_name] = {
            "accuracy": accuracy,
            "correct": correct,
            "total": len(rows),
            "predictions": predictions,
        }
        print(f"{dataset_name}: {accuracy:.3f} ({correct}/{len(rows)})")

    all_predictions["overall"] = {
        "accuracy": total_correct / total_count if total_count else 0.0,
        "correct": total_correct,
        "total": total_count,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(all_predictions, indent=2), encoding="utf-8")
    print(f"Saved predictions to {output}")


if __name__ == "__main__":
    main()
