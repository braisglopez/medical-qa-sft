# MIRAGE evaluation and analysis

`evaluate_mirage.py` evaluates a base model or a saved adapter against the MIRAGE benchmark. The final experiments use `--selection-mode constrained`, which permits only the valid answer identifiers for each question and generates exactly one answer token.

The remaining scripts support result inspection:

- `summarize_mirage_results.py`: base-versus-adapter accuracy comparison;
- `analyze_mirage_changes.py`: question-level improvements, regressions, transitions, and answer distributions; and
- `inspect_mirage_predictions.py`: inspection of malformed or free-form generations from preliminary experiments.

The canonical benchmark input is in `../benchmarks/MIRAGE/benchmark.json`. Final predictions and derived analyses are stored in `../results/`.
