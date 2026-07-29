#!/bin/bash
#SBATCH --job-name=gemma_who_lora
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=10:00:00
#SBATCH --qos=regular
#SBATCH --output=results/logs/slurm/%x_%j.log

source "$(dirname "$0")/../common.sh"

python training/train_gemma_unsloth.py \
  --dataset data/corpora/who_sft.jsonl \
  --model unsloth/gemma-3-4b-it-unsloth-bnb-4bit \
  --output-dir artifacts/adapters/gemma3_4b_who_lora_lr5e5_epoch1_r8 \
  --max-seq-length 1024 \
  --epochs 1 \
  --learning-rate 5e-5 \
  --batch-size 2 \
  --grad-accum 4 \
  --lora-r 8 \
  --lora-alpha 8 \
  --lora-dropout 0
