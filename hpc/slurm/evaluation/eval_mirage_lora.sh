#!/bin/bash
#SBATCH --job-name=mirage_lora_constrained
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=12:00:00
#SBATCH --qos=regular
#SBATCH --output=results/logs/slurm/%x_%j.log

source "$(dirname "$0")/../common.sh"

LIMIT_ARGS=()
: "${ADAPTER_DIR:?Set ADAPTER_DIR to a local adapter directory before submission.}"
OUTPUT_PREFIX="${OUTPUT_PREFIX:-mirage_adapter_constrained}"
OUTPUT="artifacts/evaluations/${OUTPUT_PREFIX}_full.json"
if [[ -n "${LIMIT:-}" ]]; then
  LIMIT_ARGS=(--limit "${LIMIT}")
  OUTPUT="artifacts/evaluations/${OUTPUT_PREFIX}_limit${LIMIT}.json"
fi

python evaluation/evaluate_mirage.py \
  --benchmark benchmarks/MIRAGE/benchmark.json \
  --model "$ADAPTER_DIR" \
  --output "$OUTPUT" \
  --selection-mode constrained \
  "${LIMIT_ARGS[@]}"
