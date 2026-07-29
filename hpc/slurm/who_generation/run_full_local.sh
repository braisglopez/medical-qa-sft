#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
cd "${REPO_ROOT}"
mkdir -p artifacts/who_generation

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
