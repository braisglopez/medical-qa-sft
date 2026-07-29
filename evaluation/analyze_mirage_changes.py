import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


STATUS_ORDER = ("improved", "worsened", "both_correct", "both_wrong")


def load_json(path):
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def dataset_results(result):
    for name, value in result.items():
        if name == "overall" or not isinstance(value, dict):
            continue
        predictions = value.get("predictions")
        if isinstance(predictions, list):
            yield name, value


def normalize_text(text):
    text = str(text or "").lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def prediction_key(row):
    return (
        normalize_text(row.get("question")),
        normalize_text(row.get("gold")),
    )


def indexed_predictions(rows):
    counts = Counter()
    indexed = {}
    for row in rows:
        base_key = prediction_key(row)
        counts[base_key] += 1
        key = (*base_key, counts[base_key])
        indexed[key] = row
    return indexed


def correctness_status(base_row, tuned_row):
    base_correct = bool(base_row.get("correct"))
    tuned_correct = bool(tuned_row.get("correct"))
    if base_correct and tuned_correct:
        return "both_correct"
    if (not base_correct) and (not tuned_correct):
        return "both_wrong"
    if (not base_correct) and tuned_correct:
        return "improved"
    return "worsened"


def clean_prediction(value):
    return str(value or "<empty>").strip() or "<empty>"


def pair_rows(base_result, tuned_result):
    base_sets = dict(dataset_results(base_result))
    tuned_sets = dict(dataset_results(tuned_result))

    for dataset in base_sets:
        if dataset not in tuned_sets:
            continue

        base_index = indexed_predictions(base_sets[dataset]["predictions"])
        tuned_index = indexed_predictions(tuned_sets[dataset]["predictions"])
        common_keys = [key for key in base_index if key in tuned_index]

        for key in common_keys:
            yield dataset, base_index[key], tuned_index[key]


def ensure_dir(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_csv(path, rows, fieldnames):
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_analysis(name, base_result, tuned_result):
    summary = defaultdict(lambda: Counter())
    transitions = Counter()
    transitions_by_gold = Counter()
    distributions = defaultdict(Counter)
    question_rows = []

    for dataset, base_row, tuned_row in pair_rows(base_result, tuned_result):
        status = correctness_status(base_row, tuned_row)
        base_pred = clean_prediction(base_row.get("prediction"))
        tuned_pred = clean_prediction(tuned_row.get("prediction"))
        gold = clean_prediction(base_row.get("gold"))

        summary[dataset]["total"] += 1
        summary[dataset][status] += 1
        summary[dataset]["base_correct"] += int(bool(base_row.get("correct")))
        summary[dataset]["tuned_correct"] += int(bool(tuned_row.get("correct")))
        summary[dataset]["prediction_changed"] += int(base_pred != tuned_pred)
        summary[dataset]["prediction_same"] += int(base_pred == tuned_pred)

        transitions[(dataset, base_pred, tuned_pred)] += 1
        transitions_by_gold[(dataset, gold, base_pred, tuned_pred)] += 1
        distributions[("base", dataset)][base_pred] += 1
        distributions[("tuned", dataset)][tuned_pred] += 1

        question_rows.append(
            {
                "comparison": name,
                "dataset": dataset,
                "status": status,
                "question": base_row.get("question", ""),
                "gold": gold,
                "base_prediction": base_pred,
                "tuned_prediction": tuned_pred,
                "base_correct": int(bool(base_row.get("correct"))),
                "tuned_correct": int(bool(tuned_row.get("correct"))),
                "base_raw_generation": base_row.get("raw_generation", ""),
                "tuned_raw_generation": tuned_row.get("raw_generation", ""),
                "options_json": json.dumps(
                    base_row.get("options", {}),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            }
        )

    return summary, transitions, transitions_by_gold, distributions, question_rows


def summary_rows(name, summary):
    rows = []
    overall = Counter()

    for dataset in sorted(summary):
        counts = summary[dataset]
        rows.append(summary_row(name, dataset, counts))
        overall.update(counts)

    if overall:
        rows.append(summary_row(name, "overall", overall))
    return rows


def summary_row(name, dataset, counts):
    total = counts["total"]
    base_correct = counts["base_correct"]
    tuned_correct = counts["tuned_correct"]
    improved = counts["improved"]
    worsened = counts["worsened"]
    return {
        "comparison": name,
        "dataset": dataset,
        "total": total,
        "base_correct": base_correct,
        "tuned_correct": tuned_correct,
        "base_accuracy": base_correct / total if total else 0.0,
        "tuned_accuracy": tuned_correct / total if total else 0.0,
        "delta_accuracy": (tuned_correct - base_correct) / total if total else 0.0,
        "improved": improved,
        "worsened": worsened,
        "both_correct": counts["both_correct"],
        "both_wrong": counts["both_wrong"],
        "net_improvement": improved - worsened,
        "prediction_changed": counts["prediction_changed"],
        "prediction_same": counts["prediction_same"],
    }


def transition_rows(name, transitions):
    return [
        {
            "comparison": name,
            "dataset": dataset,
            "base_prediction": base_pred,
            "tuned_prediction": tuned_pred,
            "count": count,
        }
        for (dataset, base_pred, tuned_pred), count in sorted(transitions.items())
    ]


def transition_by_gold_rows(name, transitions):
    return [
        {
            "comparison": name,
            "dataset": dataset,
            "gold": gold,
            "base_prediction": base_pred,
            "tuned_prediction": tuned_pred,
            "count": count,
        }
        for (dataset, gold, base_pred, tuned_pred), count in sorted(transitions.items())
    ]


def distribution_rows(name, distributions):
    rows = []
    for (run, dataset), counter in sorted(distributions.items()):
        total = sum(counter.values())
        for prediction, count in sorted(counter.items()):
            rows.append(
                {
                    "comparison": name,
                    "run": run,
                    "dataset": dataset,
                    "prediction": prediction,
                    "count": count,
                    "percent": count / total if total else 0.0,
                }
            )
    return rows


def write_markdown_report(path, name, rows, question_rows, examples_per_status):
    by_dataset = {row["dataset"]: row for row in rows if row["dataset"] != "overall"}
    overall = next((row for row in rows if row["dataset"] == "overall"), None)
    examples = defaultdict(lambda: defaultdict(list))
    for row in question_rows:
        bucket = examples[row["dataset"]][row["status"]]
        if len(bucket) < examples_per_status:
            bucket.append(row)

    with Path(path).open("w", encoding="utf-8") as f:
        f.write(f"# MIRAGE Pairwise Analysis: {name}\n\n")
        if overall:
            f.write("## Overall\n\n")
            f.write(
                "| Total | Base acc | Tuned acc | Delta | Improved | Worsened | Net |\n"
            )
            f.write("|---:|---:|---:|---:|---:|---:|---:|\n")
            f.write(
                f"| {overall['total']} | {overall['base_accuracy']:.4f} | "
                f"{overall['tuned_accuracy']:.4f} | {overall['delta_accuracy']:+.4f} | "
                f"{overall['improved']} | {overall['worsened']} | "
                f"{overall['net_improvement']} |\n\n"
            )

        f.write("## By Dataset\n\n")
        f.write(
            "| Dataset | Base acc | Tuned acc | Delta | Improved | Worsened | "
            "Both correct | Both wrong | Net |\n"
        )
        f.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for dataset, row in sorted(by_dataset.items()):
            f.write(
                f"| {dataset} | {row['base_accuracy']:.4f} | "
                f"{row['tuned_accuracy']:.4f} | {row['delta_accuracy']:+.4f} | "
                f"{row['improved']} | {row['worsened']} | "
                f"{row['both_correct']} | {row['both_wrong']} | "
                f"{row['net_improvement']} |\n"
            )

        f.write("\n## Examples\n\n")
        for dataset in sorted(examples):
            f.write(f"### {dataset}\n\n")
            for status in STATUS_ORDER:
                rows_for_status = examples[dataset].get(status, [])
                if not rows_for_status:
                    continue
                f.write(f"#### {status}\n\n")
                for row in rows_for_status:
                    f.write(
                        f"- gold={row['gold']} base={row['base_prediction']} "
                        f"tuned={row['tuned_prediction']} "
                        f"question={row['question']}\n"
                    )
                f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Compare MIRAGE base vs tuned predictions question by question."
    )
    parser.add_argument("--base", required=True)
    parser.add_argument("--tuned", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--output-dir", default="outputs/mirage_analysis")
    parser.add_argument("--examples-per-status", type=int, default=5)
    args = parser.parse_args()

    output_dir = ensure_dir(Path(args.output_dir) / args.name)
    base_result = load_json(args.base)
    tuned_result = load_json(args.tuned)

    summary, transitions, transitions_by_gold, distributions, question_rows = (
        build_analysis(args.name, base_result, tuned_result)
    )
    summaries = summary_rows(args.name, summary)

    write_csv(
        output_dir / "summary_by_dataset.csv",
        summaries,
        [
            "comparison",
            "dataset",
            "total",
            "base_correct",
            "tuned_correct",
            "base_accuracy",
            "tuned_accuracy",
            "delta_accuracy",
            "improved",
            "worsened",
            "both_correct",
            "both_wrong",
            "net_improvement",
            "prediction_changed",
            "prediction_same",
        ],
    )
    write_csv(
        output_dir / "question_changes.csv",
        question_rows,
        [
            "comparison",
            "dataset",
            "status",
            "question",
            "gold",
            "base_prediction",
            "tuned_prediction",
            "base_correct",
            "tuned_correct",
            "base_raw_generation",
            "tuned_raw_generation",
            "options_json",
        ],
    )
    write_csv(
        output_dir / "transition_matrix.csv",
        transition_rows(args.name, transitions),
        ["comparison", "dataset", "base_prediction", "tuned_prediction", "count"],
    )
    write_csv(
        output_dir / "transition_matrix_by_gold.csv",
        transition_by_gold_rows(args.name, transitions_by_gold),
        [
            "comparison",
            "dataset",
            "gold",
            "base_prediction",
            "tuned_prediction",
            "count",
        ],
    )
    write_csv(
        output_dir / "prediction_distribution.csv",
        distribution_rows(args.name, distributions),
        ["comparison", "run", "dataset", "prediction", "count", "percent"],
    )
    write_markdown_report(
        output_dir / "report.md",
        args.name,
        summaries,
        question_rows,
        args.examples_per_status,
    )

    overall = next((row for row in summaries if row["dataset"] == "overall"), None)
    if overall:
        print(
            f"{args.name}: base={overall['base_accuracy']:.4f} "
            f"tuned={overall['tuned_accuracy']:.4f} "
            f"delta={overall['delta_accuracy']:+.4f} "
            f"improved={overall['improved']} "
            f"worsened={overall['worsened']}"
        )
    print(f"Saved analysis to {output_dir}")


if __name__ == "__main__":
    main()
