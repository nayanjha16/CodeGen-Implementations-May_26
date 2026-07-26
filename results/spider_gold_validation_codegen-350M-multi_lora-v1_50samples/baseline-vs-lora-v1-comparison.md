# Baseline vs LoRA v1 — superseded (n=50 not used)

**LoRA v1 is evaluated at n=5 only** (smoke eval). A full n=50 run was not kept for v1 to save eval time.

Use the canonical report:

[`results/spider_gold_validation_codegen-350M-multi_lora-v1/baseline-vs-lora-v1-comparison.md`](../spider_gold_validation_codegen-350M-multi_lora-v1/baseline-vs-lora-v1-comparison.md)

When **LoRA v3** adapters are ready, run n=50 baseline + LoRA eval once with output folders such as:

- `spider_gold_validation_codegen-350M-multi_baseline-v3`
- `spider_gold_validation_codegen-350M-multi_lora-v3`

Legacy CSVs in this folder (if present) are from an older n=50 experiment and are not the official v1 comparison.
