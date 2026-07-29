# Data resources

This directory contains the source-level records and the final training collections used in the experiments. All records are in English.

## Layout

```text
sources/drugs/drugs_answers_all_pages.json
    Canonical extraction from Drugs.com Answers (3,609 records).

sources/who/topics/
    237 WHO Fact Sheet topic files used as input for QA generation.

generated/who_qa_exhaustive_local.json
    Canonical generated WHO QA collection before conversion to chat JSONL
    (4,057 records).

corpora/drugs_sft.jsonl
    Drugs-SFT: 3,609 chat-format training examples.

corpora/who_sft.jsonl
    WHO-SFT: 4,057 chat-format training examples.

corpora/drugs_who_sft.jsonl
    Combined Drugs+WHO-SFT collection: 7,664 examples after deduplication.
```

## SFT format

Every corpus uses one JSON object per line. Each record contains a `messages` list compatible with the chat template used during SFT, together with `source_url` for provenance.

```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "source_url": "https://..."
}
```

## Provenance and use

The Drugs-SFT records derive from Drugs.com Answers. WHO-SFT is derived from WHO Fact Sheets and generated with the pipeline in `../data_preparation/who/`. The source URL is retained whenever available to enable traceability.

These materials are provided for research and reproducibility. Before redistributing or using them beyond this project, review the terms of use and copyright conditions of the original sources.
