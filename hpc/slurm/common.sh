#!/bin/bash

set -euo pipefail

SLURM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SLURM_DIR}/../.." && pwd)"

cd "${REPO_ROOT}"
mkdir -p artifacts/adapters artifacts/evaluations artifacts/who_generation results/logs/slurm

if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
  source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -x "$HOME/miniconda3/bin/conda" ]; then
  eval "$("$HOME/miniconda3/bin/conda" shell.bash hook)"
else
  echo "[ERROR] Could not find Conda under $HOME/miniconda3" >&2
  exit 1
fi

conda activate "${CONDA_ENV:-tfm}"
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
