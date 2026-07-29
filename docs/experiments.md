# Experimental matrix

All reported results use the full MIRAGE benchmark (7,663 questions) with constrained answer selection.

## Final configuration

| Parameter | Value |
|---|---:|
| Training method | QLoRA |
| Quantization | 4-bit base model loading |
| Epochs | 1 |
| Learning rate | 5e-5 |
| LoRA rank | 8 |
| LoRA alpha | 8 |
| Maximum sequence length | 1,024 |
| Per-device batch size | 2 |
| Gradient accumulation | 4 |
| Random seed | 3407 |

An earlier exploratory Gemma configuration used two epochs, a 2e-4 learning rate, rank 16, and a maximum sequence length of 2,048. Its answer distribution became strongly concentrated in option A, so it was not used for the final comparisons.

## Final experiments

| Base model | Collection | Adapter evaluated |
|---|---|---|
| Gemma 3 4B-IT | None | Base model |
| Gemma 3 4B-IT | Drugs-SFT | Yes |
| Gemma 3 4B-IT | WHO-SFT | Yes |
| Gemma 3 4B-IT | Drugs+WHO-SFT | Yes |
| Qwen2.5 0.5B-Instruct | None | Base model |
| Qwen2.5 0.5B-Instruct | Drugs-SFT | Yes |
| Qwen2.5 0.5B-Instruct | WHO-SFT | Yes |

The prediction JSON files and the resulting metrics are available in `../results/`.
