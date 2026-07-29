#!/bin/bash
#SBATCH --job-name=gemma_drugs_lora
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=06:00:00
#SBATCH --qos=regular
#SBATCH --output=results/logs/slurm/%x_%j.log

source "$(dirname "$0")/../common.sh"

python training/train_gemma_unsloth.py \
  --dataset data/corpora/drugs_sft.jsonl \
  --model unsloth/gemma-3-4b-it-unsloth-bnb-4bit \
  --output-dir artifacts/adapters/gemma3_4b_drugs_lora_v1 \
  --max-seq-length 2048 \
  --epochs 2 \
  --batch-size 2 \
  --grad-accum 4
