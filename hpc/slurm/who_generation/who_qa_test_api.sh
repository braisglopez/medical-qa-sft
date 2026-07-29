#!/bin/bash
#SBATCH --job-name=who_qa_test
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --qos=regular
#SBATCH --output=results/logs/slurm/%x_%j.log

source "$(dirname "$0")/../common.sh"

python data_preparation/who/generation/generate_who_qa.py \
  --input-dir data/sources/who/topics \
  --files diabetes \
  --output artifacts/who_generation/who_qa_test_api.json \
  --sft-output artifacts/who_generation/who_sft_test_api.jsonl \
  --overwrite

python data_preparation/who/generation/check_qa_outputs.py \
  --json artifacts/who_generation/who_qa_test_api.json \
  --jsonl artifacts/who_generation/who_sft_test_api.jsonl \
  --min-records 1
