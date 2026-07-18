# LoRA v4 — Beam vs Greedy Decoding Comparison

> **Project:** CodeGen Fine-Tuning with PEFT & LoRA  
> **Date:** 2026-07-18  
> **Model:** `Salesforce/codegen-350M-multi` (LoRA **v4** adapters)  
> **Judge model:** `qwen3:8b`  
> **Dataset:** `spider_gold_validation` (50 examples per task)  
> **Execution eval:** PostgreSQL result-set comparison enabled

Same v4 checkpoints; only `generation.decoding_strategy` differs between runs. Baseline through v4 (greedy) version comparison: [lora-v4-vs-all-versions-comparison.md](lora-v4-vs-all-versions-comparison.md).

## Compared runs

| Run | Decoding | Path |
| --- | -------- | ---- |
| LoRA v4 | greedy | `results/spider_gold_validation_codegen-350M-multi_lora-v4_1807_2149/metrics.json` |
| LoRA v4 | beam (`num_beams=4`) | `results/spider_gold_validation_codegen-350M-multi_lora-v4_1807_2248/metrics.json` |

## Generation settings

| Setting | Greedy (`2149`) | Beam (`2248`, current `default.yaml`) |
| ------- | ----------------- | ------------------------------------- |
| `decoding_strategy` | greedy | beam |
| `num_beams` | — | 4 |
| `do_sample` | false | false |
| `max_new_tokens` | 256 | 256 |

## v4 greedy vs beam

| Task | Metric | Greedy | Beam | Δ (beam − greedy) |
| ---- | ------ | ------ | ---- | ------------------- |
| Text2SQL | Execution accuracy | 60% | **64%** | +4 pp |
| Text2SQL | Exact match | 40% | **44%** | +4 pp |
| Text2SQL | Structural similarity | 0.916 | **0.945** | +0.029 |
| SQL2NoSQL | Execution accuracy | **88%** | 82% | −6 pp |
| SQL2NoSQL | Exact match | **80%** | 66% | −14 pp |
| SQL2NoSQL | Structural similarity | **0.983** | 0.971 | −0.012 |
| Documentation | Judge score | 7.8 | **8.5** | +0.7 |
| Documentation | Embedding similarity | 0.960 | **0.962** | +0.002 |
| Documentation | Exact match | 2% | 2% | 0 pp |

Beam improves text2sql and documentation judge score on v4 adapters; sql2nosql metrics are higher under greedy decoding.

---

## All versions — full metrics (greedy + v4 beam)

Baseline through v4 used greedy decoding. v4 beam is an additional eval on the same v4 adapters (`2248`).

### Text2SQL

| Metric | Baseline | LoRA v1 | LoRA v2 | LoRA v3 | LoRA v4 (greedy) | LoRA v4 (beam) |
| ------ | -------- | ------- | ------- | ------- | ---------------- | -------------- |
| Execution accuracy | 12% | 20% | 34% | 54% | 60% | **64%** |
| Exact match | 0% | 8% | 20% | 38% | 40% | **44%** |
| Structural similarity | 0.700 | 0.792 | 0.859 | 0.910 | 0.916 | **0.945** |

### SQL2NoSQL

| Metric | Baseline | LoRA v1 | LoRA v2 | LoRA v3 | LoRA v4 (greedy) | LoRA v4 (beam) |
| ------ | -------- | ------- | ------- | ------- | ---------------- | -------------- |
| Execution accuracy | 22% | 4% | 32% | 74% | **88%** | 82% |
| Exact match | 4% | 0% | 8% | 58% | **80%** | 66% |
| Structural similarity | 0.163 | 0.553 | 0.791 | 0.926 | **0.983** | 0.971 |

### Documentation

| Metric | Baseline | LoRA v1 | LoRA v2 | LoRA v3 | LoRA v4 (greedy) | LoRA v4 (beam) |
| ------ | -------- | ------- | ------- | ------- | ---------------- | -------------- |
| Embedding similarity | 0.714 | 0.889 | 0.926 | 0.957 | 0.960 | **0.962** |
| Judge score (0–10) | 0.1 | 1.5 | 3.1 | 6.4 | 7.8 | **8.5** |
| Exact match | 0% | 0% | 0% | 2% | 2% | 2% |

### Cross-task best (execution / judge)

| Task | Best overall | Value | Decoding |
| ---- | ------------ | ----- | -------- |
| Text2SQL | LoRA v4 (beam) | 64% exec | beam |
| SQL2NoSQL | LoRA v4 (greedy) | 88% exec | greedy |
| Documentation | LoRA v4 (beam) | 8.5 judge | beam |
