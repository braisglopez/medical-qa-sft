# Medical QA SFT

Reproducible resources and experiments for the Master's thesis *Construction of Medical Question-Answer Training Collections and Fine-Tuning of Large Language Models for Reliable Medical Question Answering*.

The repository studies how the provenance and construction of medical question-answer (QA) collections affect supervised fine-tuning (SFT) of open instruction-tuned language models. It contains two complementary collections:

- **Drugs-SFT**: 3,609 QA pairs extracted from Drugs.com Answers.
- **WHO-SFT**: 4,057 QA pairs generated from WHO Fact Sheets with source-level traceability.

The collections are used to train QLoRA adapters for Gemma 3 4B-IT and Qwen2.5 0.5B-Instruct. Models are evaluated with the MIRAGE benchmark using constrained answer selection.

## Repository contents

```text
data/               Source records and final SFT corpora.
data_preparation/   Drugs.com extraction and WHO QA generation pipelines.
training/           Dataset preparation and QLoRA training code.
evaluation/         MIRAGE evaluation and comparative analysis scripts.
hpc/                Slurm and CiTIUS deployment scripts.
benchmarks/         MIRAGE benchmark input and attribution.
results/            Final predictions, analyses, tables, and selected logs.
docs/               Dataset, reproduction, experiment, and adapter notes.
```

Adapters are intentionally not stored in Git because of their size. Their model cards and Hugging Face locations are listed in [docs/adapters.md](docs/adapters.md).

## Main workflow

1. Extract Drugs.com QA records or collect WHO Fact Sheets.
2. Build Drugs-SFT and WHO-SFT in a common chat-format JSONL representation.
3. Train QLoRA adapters using the scripts in `training/` and `hpc/slurm/`.
4. Evaluate base models and adapters on MIRAGE with constrained answer selection.
5. Produce aggregate, per-dataset, and question-level analyses.

## Installation

Create an isolated Python environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

GPU training and evaluation require a CUDA-compatible PyTorch installation and the Unsloth stack. The Slurm scripts assume the `tfm` Conda environment used on the CiTIUS cluster; adapt paths and environment names before running elsewhere.

## Data and ethical notice

The resources are intended exclusively for research. They must not be used for diagnosis, treatment, or clinical decision-making. Source records retain their provenance and are subject to the terms of use of Drugs.com and the World Health Organization. Review those terms before redistributing derived data.

## Status

The repository is being organized from the final experimental snapshot. Code, corpora, benchmark inputs, final predictions, and analysis artifacts are added in separate commits to preserve traceability.
