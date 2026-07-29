# Training

`train_gemma_unsloth.py` is the common QLoRA/SFT training entry point used by the experiment wrappers. It loads a chat-format JSONL corpus, applies the tokenizer chat template, trains LoRA adapters over a 4-bit base model, and saves the adapter directory.

`prepare_sft_dataset.py` converts the canonical Drugs extraction to the training JSONL representation. `combine_sft_datasets.py` concatenates multiple SFT corpora and optionally removes duplicate user questions; it was used to build Drugs+WHO-SFT.

The exact model, corpus, and hyperparameter combinations are specified by the Slurm wrappers in `../hpc/slurm/`.
