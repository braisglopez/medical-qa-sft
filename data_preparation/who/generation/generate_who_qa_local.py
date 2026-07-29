import argparse
import json
import time
from pathlib import Path

from generate_who_qa import (
    DEFAULT_INPUT_DIR,
    DEFAULT_SFT_OUTPUT,
    clean_text,
    dedupe_records,
    extract_json_payload,
    extract_topic_paragraphs,
    iter_text_chunks,
    iter_topic_files,
    load_existing_records,
    load_json,
    make_chunk_id,
    normalize_generated_items,
    progress_file_for,
    build_result_records,
    build_user_prompt,
    load_progress,
    save_json,
    save_progress,
    select_topic_files,
    write_sft_jsonl,
    SYSTEM_PROMPT,
)


PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_FILE = PROJECT_DIR / "outputs" / "who_qa_exhaustive_local.json"
DEFAULT_RAW_OUTPUT_DIR = PROJECT_DIR / "outputs" / "raw_local"
DEFAULT_LOCAL_MODEL = "unsloth/gemma-3-4b-it-unsloth-bnb-4bit"


def load_unsloth_model(model_name, max_seq_length, load_in_4bit):
    import unsloth
    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        dtype=None,
        load_in_4bit=load_in_4bit,
    )
    FastLanguageModel.for_inference(model)
    return model, tokenizer


def generate_local_text(model, tokenizer, args, messages, max_new_tokens):
    import torch

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    max_prompt_tokens = max(512, args.max_seq_length - max_new_tokens)
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=max_prompt_tokens,
    ).to(model.device)

    generation_kwargs = {
        "max_new_tokens": max_new_tokens,
        "do_sample": args.temperature > 0,
        "pad_token_id": tokenizer.eos_token_id,
    }
    if args.temperature > 0:
        generation_kwargs["temperature"] = args.temperature
        generation_kwargs["top_p"] = args.top_p

    with torch.inference_mode():
        output = model.generate(**inputs, **generation_kwargs)

    generated = tokenizer.decode(
        output[0][inputs["input_ids"].shape[-1] :],
        skip_special_tokens=True,
    )
    return generated.strip()


def generate_local_json(model, tokenizer, args, topic, chunk):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(topic, chunk)},
    ]
    return generate_local_text(model, tokenizer, args, messages, args.max_new_tokens)


def repair_json_response(model, tokenizer, args, raw_response, attempt, last_error=None):
    error_hint = f"\nParser error to fix: {last_error}" if last_error else ""
    messages = [
        {
            "role": "system",
            "content": (
                "You repair malformed JSON. Return valid JSON only. "
                "Do not add new facts. Do not add markdown. "
                "The output must be one JSON object with an items list. "
                "Keep only complete question-answer items. Remove incomplete, "
                "duplicated, or corrupted items if needed."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Repair attempt {attempt}. Repair this malformed JSON into "
                "valid JSON with this shape: "
                '{"items":[{"question":"...","answer_text":"...",'
                '"category":"other","evidence":"..."}]}\n\n'
                "Rules:\n"
                "- Return JSON only.\n"
                "- Keep every complete item you can recover.\n"
                "- Delete any item that cannot be made valid without guessing.\n"
                "- Escape quotes inside strings correctly.\n"
                "- If no complete item can be recovered, return {\"items\": []}.\n"
                f"{error_hint}\n\n"
                f"{raw_response[:args.max_repair_chars]}"
            ),
        },
    ]
    return generate_local_text(
        model,
        tokenizer,
        args,
        messages,
        args.repair_max_new_tokens,
    )


def save_raw_response(args, chunk_id, stage, text):
    raw_dir = Path(args.raw_output_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    safe_name = (
        chunk_id.replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace(" ", "_")
    )
    path = raw_dir / f"{safe_name}.{stage}.txt"
    path.write_text(text, encoding="utf-8")
    return path


def parse_generated_items(text, topic_title, keep_non_medical, source_text=""):
    payload = extract_json_payload(text)
    return normalize_generated_items(
        payload,
        topic_title,
        keep_non_medical,
        source_text,
    )


def generate_for_chunk_local(model, tokenizer, args, topic, chunk):
    raw_response = generate_local_json(model, tokenizer, args, topic, chunk)
    topic_title = topic.get("title", "")
    source_text = chunk.get("text", "")
    last_error = None

    try:
        return parse_generated_items(
            raw_response,
            topic_title,
            args.keep_non_medical,
            source_text,
        )
    except (json.JSONDecodeError, ValueError) as parse_error:
        last_error = parse_error
        raw_path = save_raw_response(args, args.current_chunk_id, "raw", raw_response)
        print(
            "[WHO-QA-LOCAL] Initial JSON parse failed; "
            f"raw response saved to {raw_path}. Error: {parse_error}",
            flush=True,
        )

    for attempt in range(1, args.repair_attempts + 1):
        repaired = repair_json_response(
            model,
            tokenizer,
            args,
            raw_response,
            attempt,
            last_error,
        )
        repair_path = save_raw_response(
            args,
            args.current_chunk_id,
            f"repair_attempt_{attempt}",
            repaired,
        )
        try:
            items = parse_generated_items(
                repaired,
                topic_title,
                args.keep_non_medical,
                source_text,
            )
            print(
                f"[WHO-QA-LOCAL] JSON repair succeeded on attempt {attempt}; "
                f"saved to {repair_path}",
                flush=True,
            )
            return items
        except (json.JSONDecodeError, ValueError) as repair_error:
            last_error = repair_error
            print(
                f"[WHO-QA-LOCAL] JSON repair attempt {attempt} failed; "
                f"saved to {repair_path}. Error: {repair_error}",
                flush=True,
            )

    raise ValueError(f"Could not parse or repair model JSON output: {last_error}")


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Generate WHO medical QA pairs with a local Hugging Face/Unsloth model "
            "inside the current Python process. No OpenAI API, Ollama or vLLM needed."
        )
    )
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_FILE))
    parser.add_argument("--sft-output", default=str(DEFAULT_SFT_OUTPUT))
    parser.add_argument("--raw-output-dir", default=str(DEFAULT_RAW_OUTPUT_DIR))
    parser.add_argument("--model", default=DEFAULT_LOCAL_MODEL)
    parser.add_argument("--max-seq-length", type=int, default=8192)
    parser.add_argument("--max-new-tokens", type=int, default=1800)
    parser.add_argument("--repair-max-new-tokens", type=int, default=2200)
    parser.add_argument("--repair-attempts", type=int, default=1)
    parser.add_argument("--max-repair-chars", type=int, default=12000)
    parser.add_argument("--max-chars-per-chunk", type=int, default=4500)
    parser.add_argument("--overlap-paragraphs", type=int, default=1)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--dedupe-threshold", type=float, default=0.96)
    parser.add_argument("--files", nargs="+", default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--keep-non-medical", action="store_true")
    parser.add_argument("--load-in-4bit", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Log failed chunks and continue instead of stopping the full run.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    all_files, topic_files = select_topic_files(args)
    source_page_by_name = {
        path.name: index for index, path in enumerate(all_files, start=1)
    }

    output_file = Path(args.output)
    progress_file = progress_file_for(output_file)

    if args.overwrite:
        records = []
        progress = {"processed_chunks": [], "errors": []}
    else:
        records = load_existing_records(output_file)
        progress = load_progress(progress_file)

    processed_chunks = set(progress.get("processed_chunks", []))

    print(f"[WHO-QA-LOCAL] Input dir: {args.input_dir}")
    print(f"[WHO-QA-LOCAL] Topic files selected: {len(topic_files)}")
    print(f"[WHO-QA-LOCAL] Output JSON: {output_file}")
    print(f"[WHO-QA-LOCAL] SFT JSONL: {args.sft_output or '(disabled)'}")
    print(f"[WHO-QA-LOCAL] Model: {args.model}")
    print(f"[WHO-QA-LOCAL] Existing records: {len(records)}")
    print(f"[WHO-QA-LOCAL] Processed chunks in progress file: {len(processed_chunks)}")

    planned = []
    total_paragraphs = 0
    total_chunks = 0

    for path in topic_files:
        topic = load_json(path)
        paragraphs = extract_topic_paragraphs(topic)
        chunks = list(
            iter_text_chunks(
                paragraphs,
                max_chars=args.max_chars_per_chunk,
                overlap_paragraphs=args.overlap_paragraphs,
            )
        )
        planned.append((path, topic, paragraphs, chunks))
        total_paragraphs += len(paragraphs)
        total_chunks += len(chunks)

        if args.dry_run:
            print(
                f"[WHO-QA-LOCAL] DRY {path.name}: "
                f"paragraphs={len(paragraphs)} chunks={len(chunks)}"
            )

    if args.dry_run:
        print("#" * 100)
        print(
            f"[WHO-QA-LOCAL] Dry run complete: "
            f"files={len(topic_files)} paragraphs={total_paragraphs} chunks={total_chunks}"
        )
        return

    print("[WHO-QA-LOCAL] Loading local model on GPU...")
    model, tokenizer = load_unsloth_model(
        args.model,
        max_seq_length=args.max_seq_length,
        load_in_4bit=args.load_in_4bit,
    )
    print(f"[WHO-QA-LOCAL] Model loaded on device: {model.device}")

    for path, topic, paragraphs, chunks in planned:
        title = clean_text(topic.get("title", path.stem))
        source_page = source_page_by_name[path.name]

        print("-" * 100)
        print(f"[WHO-QA-LOCAL] [{source_page}] {title}")
        print(f"[WHO-QA-LOCAL] File: {path.name} | paragraphs={len(paragraphs)} | chunks={len(chunks)}")
        file_start_count = sum(
            1 for record in records if record.get("source_page") == source_page
        )
        file_new_after_dedupe = 0
        file_generated_raw = 0

        for chunk in chunks:
            chunk_id = make_chunk_id(path, chunk)
            if chunk_id in processed_chunks:
                print(f"[WHO-QA-LOCAL] Skip processed chunk {chunk_id}")
                continue

            start = time.time()
            try:
                print(
                    f"[WHO-QA-LOCAL] Generating chunk {chunk['chunk_index']}/{len(chunks)}: "
                    f"chars={len(chunk['text'])}, paragraphs={chunk['paragraph_start']}-{chunk['paragraph_end']}",
                    flush=True,
                )
                args.current_chunk_id = chunk_id
                items = generate_for_chunk_local(model, tokenizer, args, topic, chunk)
                chunk_records = build_result_records(items, topic, path, source_page, chunk)
                before = len(records)
                records.extend(chunk_records)
                records = dedupe_records(records, args.dedupe_threshold)
                after = len(records)
                file_generated_raw += len(chunk_records)
                file_new_after_dedupe += max(0, after - before)

                processed_chunks.add(chunk_id)
                progress["processed_chunks"] = sorted(processed_chunks)

                save_json(records, output_file)
                save_progress(progress, progress_file)
                if args.sft_output:
                    write_sft_jsonl(records, args.sft_output)

                elapsed = time.time() - start
                print(
                    f"[WHO-QA-LOCAL] Chunk {chunk['chunk_index']}/{len(chunks)}: "
                    f"generated={len(chunk_records)} new_after_dedupe={after - before} "
                    f"total={after} elapsed={elapsed:.1f}s"
                )
            except Exception as e:
                error = {
                    "chunk_id": chunk_id,
                    "source_file": path.name,
                    "error": str(e),
                    "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                progress.setdefault("errors", []).append(error)
                save_progress(progress, progress_file)
                print(f"[WHO-QA-LOCAL] ERROR {chunk_id}: {e}")
                if args.continue_on_error:
                    print(
                        f"[WHO-QA-LOCAL] Continuing after failed chunk {chunk_id}. "
                        "The chunk remains unprocessed in the progress file.",
                        flush=True,
                    )
                    continue
                raise

        file_end_count = sum(
            1 for record in records if record.get("source_page") == source_page
        )
        print(
            f"[WHO-QA-LOCAL] File complete: {path.name} | "
            f"questions_for_file={file_end_count} "
            f"new_this_run={file_new_after_dedupe} "
            f"raw_generated_this_run={file_generated_raw} "
            f"previous_for_file={file_start_count} "
            f"total_records={len(records)}",
            flush=True,
        )

    records = dedupe_records(records, args.dedupe_threshold)
    save_json(records, output_file)
    if args.sft_output:
        write_sft_jsonl(records, args.sft_output)

    print("#" * 100)
    print("[WHO-QA-LOCAL] Finished")
    print(f"[WHO-QA-LOCAL] Total QA records: {len(records)}")
    print(f"[WHO-QA-LOCAL] Output JSON: {output_file}")
    if args.sft_output:
        print(f"[WHO-QA-LOCAL] SFT JSONL: {args.sft_output}")
    print(f"[WHO-QA-LOCAL] Progress file: {progress_file}")


if __name__ == "__main__":
    main()
