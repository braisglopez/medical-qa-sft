import argparse
import json
from pathlib import Path


def count_json_records(path):
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"[CHECK] Missing JSON output: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"[CHECK] Expected JSON list in {path}")

    return len(data)


def count_jsonl_records(path):
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"[CHECK] Missing JSONL output: {path}")

    count = 0
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit(f"[CHECK] Invalid JSONL at {path}:{line_number}: {e}")
            count += 1

    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True)
    parser.add_argument("--jsonl", required=True)
    parser.add_argument("--min-records", type=int, default=1)
    args = parser.parse_args()

    json_count = count_json_records(args.json)
    jsonl_count = count_jsonl_records(args.jsonl)

    print(f"[CHECK] JSON records: {json_count}")
    print(f"[CHECK] JSONL records: {jsonl_count}")

    if json_count < args.min_records:
        raise SystemExit(
            f"[CHECK] Too few JSON records: {json_count} < {args.min_records}"
        )
    if jsonl_count < args.min_records:
        raise SystemExit(
            f"[CHECK] Too few JSONL records: {jsonl_count} < {args.min_records}"
        )

    print("[CHECK] OK")


if __name__ == "__main__":
    main()
