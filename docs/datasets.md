# Dataset documentation

## Drugs-SFT

- **Source:** Drugs.com Answers.
- **Construction:** Selenium extraction of question pages followed by text cleaning, record validation, and conversion to chat-format JSONL.
- **Size:** 3,609 examples.
- **Purpose:** capture real user-facing questions related to drugs, conditions, treatments, and adverse effects.

The source extraction is stored in `../data/sources/drugs/`, while the SFT corpus is `../data/corpora/drugs_sft.jsonl`.

## WHO-SFT

- **Source:** 237 WHO Fact Sheets.
- **Construction:** topic collection, document chunking, source-grounded QA generation with a local LLM, JSON repair when needed, validation, and deduplication.
- **Size:** 4,057 examples.
- **Purpose:** provide institutionally sourced medical knowledge with a traceable original URL for each generated record.

Input topic files are in `../data/sources/who/topics/`, the generated QA JSON is in `../data/generated/`, and the final SFT corpus is `../data/corpora/who_sft.jsonl`.

## Drugs+WHO-SFT

This collection is a concatenation of Drugs-SFT and WHO-SFT after normalized-question deduplication. It contains 7,664 examples; two duplicated questions were removed.

## Format and provenance

All corpora use a chat-format JSONL representation with `system`, `user`, and `assistant` messages. The `source_url` field preserves provenance. These fields are used by the QLoRA training code without further schema conversion.

The collections are research resources. Original source terms and redistribution requirements remain applicable.
