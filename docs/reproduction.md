# Reproduction guide

The original experiments were executed on the CiTIUS HPC cluster using Slurm, a Conda environment named `tfm`, and NVIDIA L4, V100S, or A100 GPUs according to availability. The commands below show the logical workflow; inspect `../hpc/README.md` before submitting a job.

## 1. Build Drugs-SFT

The canonical Drugs extraction is already included. Rebuild the SFT corpus with:

```bash
python training/prepare_sft_dataset.py \
  --input data/sources/drugs/drugs_answers_all_pages.json \
  --output data/corpora/drugs_sft.jsonl
```

## 2. Build the combined corpus

```bash
python training/combine_sft_datasets.py \
  --inputs data/corpora/drugs_sft.jsonl data/corpora/who_sft.jsonl \
  --output data/corpora/drugs_who_sft.jsonl \
  --dedupe
```

## 3. Generate WHO-SFT

The complete output is already included. To regenerate it on a GPU, use the appropriate job under `hpc/slurm/who_generation/`. The core scripts are in `data_preparation/who/generation/`.

## 4. Train an adapter

Use the training wrapper that matches the intended experiment, for example:

```bash
sbatch hpc/slurm/training/train_gemma_who_lora.sh
```

The adapter output path is intentionally ignored by Git. Publish the resulting adapter to Hugging Face and record its model card in `adapters.md`.

## 5. Evaluate on MIRAGE

The final protocol uses constrained answer selection:

```bash
python evaluation/evaluate_mirage.py \
  --benchmark benchmarks/MIRAGE/benchmark.json \
  --model <base-model-or-adapter-path> \
  --output results/predictions/example.json \
  --selection-mode constrained
```

## 6. Analyse changes

```bash
python evaluation/analyze_mirage_changes.py \
  --name example \
  --base results/predictions/<base>.json \
  --tuned results/predictions/<adapter>.json \
  --output-dir results/analysis/example
```

Run `python <script> --help` for the complete command-line interfaces.
