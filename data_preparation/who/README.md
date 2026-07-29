# WHO Fact Sheets pipeline

The WHO workflow has two stages.

1. `collection/` contains the Selenium scripts used to collect the Fact Sheet index and download each topic as structured JSON.
2. `generation/` contains the final QA-generation and validation workflow used on the CiTIUS cluster.

The input collection contains 237 WHO Fact Sheet topic files in `../../data/sources/who/topics/`. The final generated QA records are stored in `../../data/generated/who_qa_exhaustive_local.json`, and their SFT representation is `../../data/corpora/who_sft.jsonl`.

## QA generation

`generation/generate_who_qa_local.py` loads a local Hugging Face/Unsloth model on a GPU. It processes each source document in chunks, asks the model to emit source-grounded QA records in JSON, validates and deduplicates the results, and writes resumable progress information.

`generation/generate_who_qa.py` implements the equivalent path for an OpenAI-compatible endpoint. `check_qa_outputs.py` validates the resulting JSON and JSONL files. `preflight_local_gpu.py` checks the Python, CUDA, PyTorch, and Unsloth environment before a Slurm run.

The exact Slurm launchers are kept in `../../hpc/slurm/`.
