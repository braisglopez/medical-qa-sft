import argparse
import difflib
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

DEFAULT_INPUT_DIR = PROJECT_DIR / "data" / "input" / "who_topics"
DEFAULT_OUTPUT_FILE = PROJECT_DIR / "outputs" / "who_qa_exhaustive.json"
DEFAULT_SFT_OUTPUT = PROJECT_DIR / "data" / "sft" / "who_topics_sft.jsonl"

DEFAULT_API_BASE = os.environ.get("AI_API_BASE", "http://localhost:11434/v1")
DEFAULT_MODEL = os.environ.get("AI_MODEL", "qwen3:8b")
DEFAULT_API_KEY_ENV = "AI_API_KEY"

SYSTEM_PROMPT = """
You extract high-quality medical question-answer training examples from WHO source text.
Use only the provided source text. Do not add facts, numbers, dates, definitions,
recommendations, or clinical advice that are not supported by the source text.
Preserve the exact population, denominator, timeframe, comparison, and condition
from the source text. Never broaden a statistic or statement. If the source
refers to a specific group, condition, region, age range, or timeframe, keep
that same scope in the question and answer.

Return valid JSON only, with this exact shape:
{
  "items": [
    {
      "question": "A natural medical or public-health question in English",
      "answer_text": "A clear, standalone answer in English grounded in the source text",
      "category": "definition|symptoms|risk_factors|causes|transmission|diagnosis|treatment|prevention|complications|burden|public_health|other",
      "evidence": "A short phrase or sentence from the source text that supports the answer"
    }
  ]
}

Do not include markdown, bullets, numbering, citations, URLs, comments, or reasoning.
""".strip()

SFT_SYSTEM_PROMPT = (
    "You are a medical question-answering assistant. Answer clearly, "
    "accurately, and remind the user to consult a healthcare professional "
    "when the answer involves diagnosis or treatment decisions."
)

MEDICAL_KEYWORDS = {
    "abortion",
    "adolescent",
    "air pollution",
    "alcohol",
    "anaemia",
    "antibiotic",
    "antimicrobial",
    "asthma",
    "bacteria",
    "birth",
    "blood",
    "brain",
    "cancer",
    "cardiovascular",
    "care",
    "child",
    "clinical",
    "communicable",
    "complication",
    "condition",
    "contraception",
    "death",
    "diagnosis",
    "diabetes",
    "diet",
    "disease",
    "doctor",
    "drug",
    "epidemic",
    "exposure",
    "fever",
    "health",
    "health-care",
    "healthcare",
    "heart",
    "hospital",
    "hypertension",
    "immune",
    "immunization",
    "infection",
    "injury",
    "medicine",
    "mental",
    "mortality",
    "nutrition",
    "obesity",
    "outbreak",
    "overdose",
    "patient",
    "pregnancy",
    "prevention",
    "public health",
    "risk",
    "sanitation",
    "screening",
    "stroke",
    "symptom",
    "syndrome",
    "therapy",
    "tobacco",
    "transmission",
    "treatment",
    "vaccine",
    "virus",
    "violence",
    "water",
}

VALID_CATEGORIES = {
    "definition",
    "symptoms",
    "risk_factors",
    "causes",
    "transmission",
    "diagnosis",
    "treatment",
    "prevention",
    "complications",
    "burden",
    "public_health",
    "other",
}

SCOPE_SENSITIVE_QUESTION_PHRASES = (
    "world population",
    "world's population",
    "global population",
    "general population",
    "adult population",
    "children worldwide",
    "adults worldwide",
)


def fix_mojibake(text):
    if not isinstance(text, str):
        return ""

    markers = ("Ã", "â", "Â")
    if not any(marker in text for marker in markers):
        return text

    try:
        return text.encode("cp1252").decode("utf-8")
    except UnicodeError:
        return text


def clean_text(text):
    text = fix_mojibake(text)
    text = text.replace("\u200b", " ").replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def iter_topic_files(input_dir):
    input_dir = Path(input_dir)
    return sorted(input_dir.glob("*.json"), key=lambda path: path.name.lower())


def extract_topic_paragraphs(topic):
    raw_paragraphs = topic.get("all_paragraphs") or []
    if not raw_paragraphs:
        full_text = clean_text(topic.get("full_text", ""))
        raw_paragraphs = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", full_text)

    paragraphs = []
    for paragraph in raw_paragraphs:
        paragraph = clean_text(paragraph)
        if not paragraph:
            continue
        if re.match(r"^\d+\.\s+[A-Z].*(?:https?://|doi:)", paragraph):
            continue
        paragraphs.append(paragraph)

    return paragraphs


def split_long_paragraph(paragraph, max_chars):
    if len(paragraph) <= max_chars:
        return [paragraph]

    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    chunks = []
    current = []
    current_len = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(sentence) > max_chars:
            words = sentence.split()
            piece = []
            piece_len = 0
            for word in words:
                if piece and piece_len + len(word) + 1 > max_chars:
                    chunks.append(" ".join(piece))
                    piece = []
                    piece_len = 0
                piece.append(word)
                piece_len += len(word) + 1
            if piece:
                chunks.append(" ".join(piece))
            continue

        if current and current_len + len(sentence) + 1 > max_chars:
            chunks.append(" ".join(current))
            current = []
            current_len = 0

        current.append(sentence)
        current_len += len(sentence) + 1

    if current:
        chunks.append(" ".join(current))

    return chunks


def iter_text_chunks(paragraphs, max_chars, overlap_paragraphs):
    expanded = []
    for paragraph in paragraphs:
        expanded.extend(split_long_paragraph(paragraph, max_chars))

    start = 0
    chunk_index = 1
    total = len(expanded)

    while start < total:
        selected = []
        current_len = 0
        end = start

        while end < total:
            paragraph = expanded[end]
            extra = len(paragraph) + (2 if selected else 0)
            if selected and current_len + extra > max_chars:
                break
            selected.append(paragraph)
            current_len += extra
            end += 1

        if not selected:
            selected = [expanded[start]]
            end = start + 1

        yield {
            "chunk_index": chunk_index,
            "paragraph_start": start + 1,
            "paragraph_end": end,
            "text": "\n\n".join(selected),
        }

        if end >= total:
            break

        start = max(start + 1, end - max(0, overlap_paragraphs))
        chunk_index += 1


def build_user_prompt(topic, chunk):
    title = clean_text(topic.get("title", ""))
    url = clean_text(topic.get("url", ""))

    return f"""
/no_think

Generate all distinct medical or public-health question-answer pairs supported by this WHO topic chunk.
There is no fixed number of items. Return as many useful, non-duplicated items as the text supports.

Requirements:
- Questions must be useful for supervised fine-tuning of a medical QA model.
- Prefer clinically useful medical or public-health questions over isolated trivia.
- Each item must ask about a distinct fact, not a rewording of another question.
- Include only questions answerable from this chunk.
- Preserve the exact denominator, population, time period, comparison, and disease
  scope from the source text.
- Never broaden a statistic. If the source refers to a specific group, condition,
  region, age range, or timeframe, keep that same scope in the question and answer.
- Prefer definition, symptoms, risk factors, causes, transmission, diagnosis,
  treatment, prevention, complications, public-health burden, and WHO actions
  when the chunk supports them.
- Generate statistical questions only when the statistic is medically or
  public-health relevant, and preserve the exact denominator and year.
- If a question asks for a percentage, rate, proportion, count, or number, name
  the measured group explicitly in the question.
- Do not create questions from incomplete lead-in sentences ending with ":" unless
  the answer is fully present in the chunk.
- Avoid vague broad questions such as "What are some potential problems..." when
  the source supports one specific complication; ask the specific question instead.
- Skip purely administrative, navigation, copyright, citation, or webpage-related content.
- Answers must be clear, factual, standalone, and usually 1 to 3 sentences.
- Do not mention "the source text", "the chunk", or "the article".
- If the chunk has no medical or public-health facts, return {{"items": []}}.

Topic title: {title}
Topic URL: {url}
Chunk paragraphs: {chunk["paragraph_start"]}-{chunk["paragraph_end"]}

Source text:
{chunk["text"]}
""".strip()


def post_chat_completion(
    api_base,
    api_key,
    model,
    messages,
    temperature,
    max_tokens,
    timeout,
    json_mode,
    retries,
):
    url = api_base.rstrip("/") + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    body = json.dumps(payload).encode("utf-8")

    for attempt in range(1, retries + 2):
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                response_body = response.read().decode("utf-8")
            data = json.loads(response_body)
            return data["choices"][0]["message"]["content"]
        except TimeoutError as e:
            last_error = RuntimeError(
                f"The model did not finish within {timeout} seconds."
            )
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"HTTP {e.code} from {url}: {error_body}")
        except urllib.error.URLError as e:
            last_error = RuntimeError(f"Could not connect to {url}: {e}")
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
            last_error = RuntimeError(f"Unexpected API response: {e}")

        if attempt <= retries:
            wait_seconds = min(30, 2 ** attempt)
            print(f"[WHO-QA] Request failed, retrying in {wait_seconds}s: {last_error}")
            time.sleep(wait_seconds)

    raise last_error


def extract_json_payload(text):
    text = clean_text(text)

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    first = text.find("{")
    last = text.rfind("}")
    if first >= 0 and last > first:
        return json.loads(text[first:last + 1])

    first = text.find("[")
    last = text.rfind("]")
    if first >= 0 and last > first:
        return json.loads(text[first:last + 1])

    raise ValueError(f"Model did not return parseable JSON: {text[:500]}")


def is_medical_item(item, topic_title):
    combined = " ".join(
        [
            clean_text(topic_title),
            clean_text(item.get("question", "")),
            clean_text(item.get("answer_text", "")),
            clean_text(item.get("category", "")),
        ]
    ).lower()

    return any(keyword in combined for keyword in MEDICAL_KEYWORDS)


def violates_source_scope(question, source_text):
    question_lc = clean_text(question).lower()
    source_lc = clean_text(source_text).lower()

    return any(
        phrase in question_lc and phrase not in source_lc
        for phrase in SCOPE_SENSITIVE_QUESTION_PHRASES
    )


def normalize_generated_items(payload, topic_title, keep_non_medical, source_text=""):
    if isinstance(payload, list):
        raw_items = payload
    elif isinstance(payload, dict):
        if "question" in payload and ("answer_text" in payload or "answer" in payload):
            raw_items = [payload]
        else:
            raw_items = payload.get("items") or payload.get("questions") or payload.get("qas") or []
    else:
        raw_items = []

    items = []
    for raw in raw_items:
        if not isinstance(raw, dict):
            continue

        question = clean_text(raw.get("question", ""))
        answer_text = clean_text(raw.get("answer_text") or raw.get("answer") or "")
        evidence = clean_text(raw.get("evidence", ""))
        category = clean_text(raw.get("category", "other")).lower().replace("-", "_").replace(" ", "_")
        if category not in VALID_CATEGORIES:
            category = "other"

        if not question or not answer_text:
            continue
        if len(question.split()) < 4 or len(answer_text.split()) < 8:
            continue
        if not question.endswith("?"):
            question = question.rstrip(".") + "?"
        if source_text and violates_source_scope(question, source_text):
            continue

        item = {
            "question": question,
            "answer_text": answer_text,
            "category": category,
            "evidence": evidence,
        }

        if not keep_non_medical and not is_medical_item(item, topic_title):
            continue

        items.append(item)

    return items


def question_key(question):
    question = clean_text(question).lower()
    question = re.sub(r"\b(the|a|an)\b", " ", question)
    question = re.sub(r"[^a-z0-9]+", " ", question)
    question = re.sub(r"\s+", " ", question).strip()
    return question


def dedupe_records(records, threshold):
    seen_exact = set()
    seen_keys = []
    deduped = []

    for record in records:
        key = question_key(record.get("question", ""))
        if not key or key in seen_exact:
            continue

        duplicate = False
        if threshold and threshold < 1.0:
            for old_key in seen_keys:
                if abs(len(key) - len(old_key)) > max(len(key), len(old_key)) * 0.35:
                    continue
                if difflib.SequenceMatcher(None, key, old_key).ratio() >= threshold:
                    duplicate = True
                    break

        if duplicate:
            continue

        seen_exact.add(key)
        seen_keys.append(key)
        deduped.append(record)

    return deduped


def load_existing_records(output_file):
    output_file = Path(output_file)
    if not output_file.exists():
        return []

    data = load_json(output_file)
    if not isinstance(data, list):
        raise ValueError(f"Existing output must be a JSON list: {output_file}")

    return data


def progress_file_for(output_file):
    output_file = Path(output_file)
    return output_file.with_name(output_file.stem + ".progress.json")


def load_progress(progress_file):
    progress_file = Path(progress_file)
    if not progress_file.exists():
        return {"processed_chunks": [], "errors": []}

    data = load_json(progress_file)
    if not isinstance(data, dict):
        return {"processed_chunks": [], "errors": []}

    data.setdefault("processed_chunks", [])
    data.setdefault("errors", [])
    return data


def save_progress(progress, progress_file):
    save_json(progress, progress_file)


def make_chunk_id(path, chunk):
    return f"{path.name}:{chunk['chunk_index']}:{chunk['paragraph_start']}-{chunk['paragraph_end']}"


def build_result_records(items, topic, path, source_page, chunk):
    url = clean_text(topic.get("url", ""))

    records = []
    for item in items:
        records.append(
            {
                "question": item["question"],
                "url": url,
                "source_page": source_page,
                "answer_text": item["answer_text"],
            }
        )

    return records


def write_sft_jsonl(records, output_file):
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        for record in records:
            row = {
                "messages": [
                    {"role": "system", "content": SFT_SYSTEM_PROMPT},
                    {"role": "user", "content": record["question"]},
                    {"role": "assistant", "content": record["answer_text"]},
                ],
                "source_url": record.get("url", ""),
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def generate_for_chunk(args, topic, chunk):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(topic, chunk)},
    ]

    raw_response = post_chat_completion(
        api_base=args.api_base,
        api_key=os.environ.get(args.api_key_env, ""),
        model=args.model,
        messages=messages,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
        json_mode=not args.no_json_mode,
        retries=args.retries,
    )
    payload = extract_json_payload(raw_response)
    return normalize_generated_items(
        payload,
        topic.get("title", ""),
        args.keep_non_medical,
        chunk.get("text", ""),
    )


def select_topic_files(args):
    all_files = iter_topic_files(args.input_dir)
    if not all_files:
        raise SystemExit(f"No WHO topic JSON files found in {args.input_dir}")

    if not args.files:
        return all_files, all_files

    requested = {
        name if name.lower().endswith(".json") else f"{name}.json"
        for name in args.files
    }
    requested = {name.lower() for name in requested}
    selected = [path for path in all_files if path.name.lower() in requested]
    found = {path.name.lower() for path in selected}
    missing = sorted(requested - found)
    if missing:
        raise SystemExit(f"Requested topic files not found: {', '.join(missing)}")

    return all_files, selected


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Generate exhaustive medical QA pairs from WHO topic JSON files using "
            "an OpenAI-compatible chat completion API. The script processes every "
            "paragraph chunk in every selected file and does not impose a per-file QA limit."
        )
    )
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_FILE))
    parser.add_argument(
        "--sft-output",
        default=str(DEFAULT_SFT_OUTPUT),
        help="Optional JSONL output ready for train_gemma_unsloth.py. Use '' to disable.",
    )
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--api-key-env", default=DEFAULT_API_KEY_ENV)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--max-chars-per-chunk",
        type=int,
        default=6000,
        help="Maximum characters sent to the model per chunk. This is not a per-file QA limit.",
    )
    parser.add_argument(
        "--overlap-paragraphs",
        type=int,
        default=1,
        help="Paragraph overlap between chunks to avoid losing boundary facts.",
    )
    parser.add_argument("--max-tokens", type=int, default=5000)
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument(
        "--dedupe-threshold",
        type=float,
        default=0.96,
        help="Similarity threshold for removing near-duplicate questions. Use 1.0 for exact-only.",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        default=None,
        help="Optional subset by file name or stem, e.g. --files diabetes hypertension.json.",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--keep-non-medical", action="store_true")
    parser.add_argument("--no-json-mode", action="store_true")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only count files, paragraphs and chunks; do not call the LLM.",
    )
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

    print(f"[WHO-QA] Input dir: {args.input_dir}")
    print(f"[WHO-QA] Topic files selected: {len(topic_files)}")
    print(f"[WHO-QA] Output JSON: {output_file}")
    print(f"[WHO-QA] SFT JSONL: {args.sft_output or '(disabled)'}")
    print(f"[WHO-QA] API base: {args.api_base}")
    print(f"[WHO-QA] Model: {args.model}")
    print(f"[WHO-QA] Existing records: {len(records)}")
    print(f"[WHO-QA] Processed chunks in progress file: {len(processed_chunks)}")

    total_chunks = 0
    total_paragraphs = 0

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
        total_chunks += len(chunks)
        total_paragraphs += len(paragraphs)

        if args.dry_run:
            print(
                f"[WHO-QA] DRY {path.name}: paragraphs={len(paragraphs)} chunks={len(chunks)}"
            )
            continue

        title = clean_text(topic.get("title", path.stem))
        source_page = source_page_by_name[path.name]

        print("-" * 100)
        print(f"[WHO-QA] [{source_page}] {title}")
        print(f"[WHO-QA] File: {path.name} | paragraphs={len(paragraphs)} | chunks={len(chunks)}")
        file_start_count = sum(
            1 for record in records if record.get("source_page") == source_page
        )
        file_new_after_dedupe = 0
        file_generated_raw = 0

        for chunk in chunks:
            chunk_id = make_chunk_id(path, chunk)
            if chunk_id in processed_chunks:
                print(f"[WHO-QA] Skip processed chunk {chunk_id}")
                continue

            start = time.time()
            try:
                print(
                    f"[WHO-QA] Sending chunk {chunk['chunk_index']}/{len(chunks)} "
                    f"to LLM: chars={len(chunk['text'])}, "
                    f"paragraphs={chunk['paragraph_start']}-{chunk['paragraph_end']}",
                    flush=True,
                )
                items = generate_for_chunk(args, topic, chunk)
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
                    f"[WHO-QA] Chunk {chunk['chunk_index']}/{len(chunks)}: "
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
                print(f"[WHO-QA] ERROR {chunk_id}: {e}")
                raise

            if args.sleep:
                time.sleep(args.sleep)

        file_end_count = sum(
            1 for record in records if record.get("source_page") == source_page
        )
        print(
            f"[WHO-QA] File complete: {path.name} | "
            f"questions_for_file={file_end_count} "
            f"new_this_run={file_new_after_dedupe} "
            f"raw_generated_this_run={file_generated_raw} "
            f"previous_for_file={file_start_count} "
            f"total_records={len(records)}",
            flush=True,
        )

    if args.dry_run:
        print("#" * 100)
        print(f"[WHO-QA] Dry run complete: files={len(topic_files)} paragraphs={total_paragraphs} chunks={total_chunks}")
        return

    records = dedupe_records(records, args.dedupe_threshold)
    save_json(records, output_file)
    if args.sft_output:
        write_sft_jsonl(records, args.sft_output)

    print("#" * 100)
    print("[WHO-QA] Finished")
    print(f"[WHO-QA] Total QA records: {len(records)}")
    print(f"[WHO-QA] Output JSON: {output_file}")
    if args.sft_output:
        print(f"[WHO-QA] SFT JSONL: {args.sft_output}")
    print(f"[WHO-QA] Progress file: {progress_file}")


if __name__ == "__main__":
    main()
