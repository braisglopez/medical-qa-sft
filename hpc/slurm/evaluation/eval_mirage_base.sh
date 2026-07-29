#!/bin/bash
#SBATCH --job-name=mirage_base
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=08:00:00
#SBATCH --qos=regular
#SBATCH --output=results/logs/slurm/%x_%j.log

source "$(dirname "$0")/../common.sh"

MODEL="${MODEL:-unsloth/gemma-3-4b-it-unsloth-bnb-4bit}"
OUTPUT_NAME="${OUTPUT_NAME:-mirage_gemma3_4b_base_constrained}"
LIMIT_ARGS=()
OUTPUT="artifacts/evaluations/${OUTPUT_NAME}_full.json"

if [[ -n "${LIMIT:-}" ]]; then
  LIMIT_ARGS=(--limit "${LIMIT}")
  OUTPUT="artifacts/evaluations/${OUTPUT_NAME}_limit${LIMIT}.json"
fi

python evaluation/evaluate_mirage.py \
  --benchmark benchmarks/MIRAGE/benchmark.json \
  --model "${MODEL}" \
  --output "${OUTPUT}" \
  --selection-mode constrained \
  "${LIMIT_ARGS[@]}"
