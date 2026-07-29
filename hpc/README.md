# CiTIUS / Slurm execution

This directory contains the scripts used to run corpus generation, QLoRA training, and MIRAGE evaluation on the CiTIUS HPC cluster.

## Layout

```text
slurm/training/       Gemma and Qwen adapter-training jobs.
slurm/evaluation/     Base-model and adapter MIRAGE evaluation jobs.
slurm/who_generation/ GPU preflight, test, and full WHO QA-generation jobs.
windows/              PowerShell deployment and result-retrieval helpers.
```

## Before submitting a job

The archived scripts preserve the paths used during the experiments, where the project lived in `~/tfm` and the Conda environment was named `tfm`. Update those paths if the repository is cloned to another location.

Typical preparation on the cluster is:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate tfm
cd ~/medical-qa-sft
```

Then submit an appropriate script, for example:

```bash
sbatch hpc/slurm/training/train_gemma_who_lora.sh
```

The final jobs use Slurm resource requests for one GPU, CPU workers, memory, and a time limit. GPU model availability is controlled by the cluster scheduler.

## Credentials

Do not put tokens or API keys in these scripts. `windows/env.example` documents the environment variables needed only by the optional OpenAI-compatible WHO generation path.
