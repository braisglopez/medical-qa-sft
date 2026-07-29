#!/bin/bash
#SBATCH --job-name=who_qa_local_test
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=01:00:00
#SBATCH --qos=regular
#SBATCH --output=results/logs/slurm/%x_%j.log

source "$(dirname "$0")/../common.sh"
python data_preparation/who/generation/preflight_local_gpu.py

python data_preparation/who/generation/generate_who_qa_local.py \
  --input-dir data/sources/who/topics \
  --files diabetes \
  --output artifacts/who_generation/who_qa_test_local.json \
  --sft-output artifacts/who_generation/who_sft_test_local.jsonl \
  --raw-output-dir artifacts/who_generation/raw_test \
  --max-chars-per-chunk 1600 \
  --max-new-tokens 700 \
  --repair-max-new-tokens 1200 \
  --repair-attempts 1 \
  --max-seq-length 4096 \
  --overwrite

python data_preparation/who/generation/check_qa_outputs.py \
  --json artifacts/who_generation/who_qa_test_local.json \
  --jsonl artifacts/who_generation/who_sft_test_local.jsonl \
  --min-records 1
