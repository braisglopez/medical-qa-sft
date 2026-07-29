#!/bin/bash
#SBATCH --job-name=who_qa_full
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=08:00:00
#SBATCH --qos=regular
#SBATCH --output=results/logs/slurm/%x_%j.log

source "$(dirname "$0")/../common.sh"

python data_preparation/who/generation/generate_who_qa.py \
  --input-dir data/sources/who/topics \
  --output artifacts/who_generation/who_qa_exhaustive_api.json \
  --sft-output artifacts/who_generation/who_sft_api.jsonl
