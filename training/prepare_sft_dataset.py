import argparse
import glob
import json
from pathlib import Path


SYSTEM_PROMPT = (
    "You are a medical question-answering assistant. Answer clearly, "
    "accurately, and remind the user to consult a healthcare professional "
    "when the answer involves diagnosis or treatment decisions."
)


def fix_mojibake(text: str) -> str:
    markers = ("â€", "Ã", "Â")
    if not isinstance(text, str) or not any(marker in text for marker in markers):
        return text
    try:
        return text.encode("cp1252").decode("utf-8")
    except UnicodeError:
        return text


def iter_records(patterns):
    seen = set()
    for pattern in patterns:
        for file_name in glob.glob(pattern):
            path = Path(file_name)
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(data, dict):
                data = [data]

            for item in data:
                question = fix_mojibake((item.get("question") or "").strip())
                answer = fix_mojibake((item.get("answer_text") or "").strip())
                if not question or not answer:
                    continue

                key = (question.lower(), answer[:200].lower())
                if key in seen:
                    continue
                seen.add(key)

                yield {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": answer},
                    ],
                    "source_url": item.get("url"),
                }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        nargs="+",
        default=["Drugs/files/drugs_answers_all_pages.json"],
        help="Input JSON files or glob patterns with question/answer_text fields.",
    )
    parser.add_argument(
        "--output",
        default="tfm_llm/data/drugs_sft.jsonl",
        help="Output JSONL file in chat-message format.",
    )
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with output.open("w", encoding="utf-8") as f:
        for record in iter_records(args.input):
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    print(f"Wrote {count} examples to {output}")


if __name__ == "__main__":
    main()
