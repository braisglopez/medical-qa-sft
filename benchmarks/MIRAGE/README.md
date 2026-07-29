# MIRAGE benchmark input

`benchmark.json` is the benchmark input used for all final evaluations in this repository. It contains 7,663 medical questions across MedQA, MedMCQA, PubMedQA, BioASQ, and medical MMLU.

MIRAGE is maintained by its original authors. Consult the official repository for the benchmark documentation, license, and citation information:

<https://github.com/gzxiong/MIRAGE>

The evaluation code in `../../evaluation/evaluate_mirage.py` normalizes the datasets and evaluates each example with constrained answer selection. This local copy is included only to reproduce the experiments reported here.
