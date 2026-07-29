import argparse
import json
from collections import Counter
from pathlib import Path


def load_result(path):
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def dataset_rows(result):
    for name, value in result.items():
        if name == "overall" or not isinstance(value, dict):
            continue
        if {"accuracy", "correct", "total", "predictions"} <= set(value):
            yield name, value


def print_summary(label, result):
    print(f"\n## {label}")
    print("| Dataset | Accuracy | Correct | Total |")
    print("|---|---:|---:|---:|")
    for name, value in dataset_rows(result):
        print(
            f"| {name} | {value['accuracy']:.4f} | "
            f"{value['correct']} | {value['total']} |"
        )

    overall = result.get("overall", {})
    if overall:
        print(
            f"| overall | {overall.get('accuracy', 0):.4f} | "
            f"{overall.get('correct', 0)} | {overall.get('total', 0)} |"
        )


def print_comparison(base, tuned):
    print("\n## Comparison")
    print("| Dataset | Base | Fine-tuned | Delta |")
    print("|---|---:|---:|---:|")

    base_by_name = dict(dataset_rows(base))
    tuned_by_name = dict(dataset_rows(tuned))
    names = [name for name in base_by_name if name in tuned_by_name]

    for name in names:
        base_acc = base_by_name[name]["accuracy"]
        tuned_acc = tuned_by_name[name]["accuracy"]
        print(f"| {name} | {base_acc:.4f} | {tuned_acc:.4f} | {tuned_acc - base_acc:+.4f} |")

    if "overall" in base and "overall" in tuned:
        base_acc = base["overall"]["accuracy"]
        tuned_acc = tuned["overall"]["accuracy"]
        print(f"| overall | {base_acc:.4f} | {tuned_acc:.4f} | {tuned_acc - base_acc:+.4f} |")


def print_prediction_distribution(label, result):
    print(f"\n## Prediction Distribution: {label}")
    for name, value in dataset_rows(result):
        counter = Counter(
            prediction.get("prediction") or "<empty>"
            for prediction in value["predictions"]
        )
        total = sum(counter.values())
        common = ", ".join(
            f"{pred}={count} ({count / total:.1%})"
            for pred, count in counter.most_common()
        )
        print(f"{name}: {common}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--tuned", required=True)
    args = parser.parse_args()

    base = load_result(args.base)
    tuned = load_result(args.tuned)

    print_summary("Base", base)
    print_summary("Fine-tuned", tuned)
    print_comparison(base, tuned)
    print_prediction_distribution("Base", base)
    print_prediction_distribution("Fine-tuned", tuned)


if __name__ == "__main__":
    main()
