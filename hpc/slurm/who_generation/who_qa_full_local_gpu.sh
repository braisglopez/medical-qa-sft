#!/bin/bash
#SBATCH --job-name=who_qa_local_full
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=36:00:00
#SBATCH --qos=regular
#SBATCH --output=results/logs/slurm/%x_%j.log

source "$(dirname "$0")/../common.sh"
python data_preparation/who/generation/preflight_local_gpu.py

python data_preparation/who/generation/generate_who_qa_local.py \
  --input-dir data/sources/who/topics \
  --output artifacts/who_generation/who_qa_exhaustive_local.json \
  --sft-output artifacts/who_generation/who_sft_local.jsonl \
  --raw-output-dir artifacts/who_generation/raw_full \
  --max-chars-per-chunk 3000 \
  --max-new-tokens 1100 \
  --repair-max-new-tokens 1800 \
  --repair-attempts 3 \
  --continue-on-error
