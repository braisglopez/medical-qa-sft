import argparse
import json
from pathlib import Path


def normalize_question(text):
    return " ".join(str(text or "").strip().lower().split())


def iter_jsonl(path):
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}: {e}") from e


def extract_user_question(row):
    for message in row.get("messages", []):
        if message.get("role") == "user":
            return message.get("content", "")
    return ""


def main():
    parser = argparse.ArgumentParser(
        description="Combine SFT JSONL files with the Drugs-compatible format."
    )
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--dedupe",
        action="store_true",
        help="Remove duplicated examples by normalized user question.",
    )
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    seen = set()
    written = 0
    skipped = 0

    with output.open("w", encoding="utf-8") as f:
        for input_file in args.inputs:
            for row in iter_jsonl(input_file):
                key = normalize_question(extract_user_question(row))
                if args.dedupe and key:
                    if key in seen:
                        skipped += 1
                        continue
                    seen.add(key)

                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                written += 1

    print(f"Wrote {written} examples to {output}")
    if args.dedupe:
        print(f"Skipped duplicated examples: {skipped}")


if __name__ == "__main__":
    main()
