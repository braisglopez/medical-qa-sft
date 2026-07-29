import argparse
import json
from collections import Counter
from pathlib import Path


def iter_datasets(result):
    for name, value in result.items():
        if name == "overall" or not isinstance(value, dict):
            continue
        predictions = value.get("predictions")
        if isinstance(predictions, list):
            yield name, predictions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("result")
    parser.add_argument("--examples", type=int, default=5)
    args = parser.parse_args()

    result = json.loads(Path(args.result).read_text(encoding="utf-8"))

    for dataset_name, predictions in iter_datasets(result):
        pred_counts = Counter(item.get("prediction") or "<empty>" for item in predictions)
        raw_prefix_counts = Counter(
            (item.get("raw_generation") or "<empty>").strip()[:30]
            for item in predictions
        )
        invalid = [
            item
            for item in predictions
            if item.get("options")
            and (item.get("prediction") or "") not in item.get("options")
        ]

        print(f"\n## {dataset_name}")
        print(f"predictions: {pred_counts.most_common()}")
        if any(item.get("options") for item in predictions):
            print(f"invalid_or_empty_predictions: {len(invalid)}/{len(predictions)}")
        print(f"common_raw_prefixes: {raw_prefix_counts.most_common(10)}")
        print("examples:")
        for item in predictions[: args.examples]:
            print(
                f"- gold={item.get('gold')} pred={item.get('prediction') or '<empty>'} "
                f"correct={item.get('correct')} raw={item.get('raw_generation')!r}"
            )


if __name__ == "__main__":
    main()
