#!/bin/bash
#SBATCH --job-name=gemma_drugs_who_lora
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=gpu:1
#SBATCH --mem=40G
#SBATCH --time=12:00:00
#SBATCH --qos=regular
#SBATCH --output=results/logs/slurm/%x_%j.log

source "$(dirname "$0")/../common.sh"

COMBINED_DATASET="artifacts/datasets/drugs_who_sft.jsonl"
mkdir -p "$(dirname "${COMBINED_DATASET}")"

echo "[TRAIN] Building combined SFT dataset: ${COMBINED_DATASET}"
python training/combine_sft_datasets.py \
  --inputs \
    data/corpora/drugs_sft.jsonl \
    data/corpora/who_sft.jsonl \
  --output "${COMBINED_DATASET}" \
  --dedupe

echo "[TRAIN] Combined examples:"
wc -l "${COMBINED_DATASET}"

echo "[TRAIN] Starting Gemma 3 4B LoRA training with Drugs+WHO"
python training/train_gemma_unsloth.py \
  --dataset "${COMBINED_DATASET}" \
  --model unsloth/gemma-3-4b-it-unsloth-bnb-4bit \
  --output-dir artifacts/adapters/gemma3_4b_drugs_who_lora_lr5e5_epoch1_r8 \
  --max-seq-length 1024 \
  --epochs 1 \
  --learning-rate 5e-5 \
  --batch-size 2 \
  --grad-accum 4 \
  --lora-r 8 \
  --lora-alpha 8 \
  --lora-dropout 0
