#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
cd "${REPO_ROOT}"
mkdir -p artifacts/who_generation

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
