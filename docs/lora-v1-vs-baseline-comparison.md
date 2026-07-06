# LoRA v1 vs Baseline — Spider Gold Validation

> **Project:** CodeGen Fine-Tuning with PEFT & LoRA  
> **Date:** 2026-07-06  
> **Model:** `Salesforce/codegen-350M-multi`  
> **LoRA adapter:** `v1`  
> **Judge model:** `qwen3:8b`  
> **Dataset:** `spider_gold_validation` (50 examples per task)  
> **Execution eval:** PostgreSQL result-set comparison enabled

## Training context

LoRA v1 was fine-tuned on **50 training samples** for **10 epochs** (smoke-scale run). Evaluation below uses the full 50-example Spider gold validation split.

## Compared runs

| Run | Path |
|-----|------|
| Baseline (no adapter) | `results/spider_gold_validation_codegen-350M-multi_0607_1841/metrics.json` |
| LoRA v1 | `results/spider_gold_validation_codegen-350M-multi_lora-v1_0607_1907/metrics.json` |

## Summary

With the updated evaluation stack (execution accuracy, structural similarity, embedding similarity, and a 0–10 judge score), LoRA v1 shows **mixed results**. The clearest wins are **sql2nosql structural similarity** (0.16 → 0.55) and **documentation embedding similarity** (0.71 → 0.89). **Execution accuracy** regresses on sql2nosql (22% → 4%) and text2sql (12% → 10%), and the documentation **judge score** drops (3.4 → 2.2).

---

## Text2SQL — slight structural gain, execution slightly down

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Execution accuracy** | **12%** | 10% | −2 pp |
| Structural similarity | 0.700 | **0.704** | +0.004 (+0.6%) |
| Exact match | 0% | 0% | 0 |

LoRA v1 marginally improves query structure overlap but does not improve exact match or execution accuracy on this split.

---

## SQL2NoSQL — large structural gain, execution regresses

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Structural similarity** | 0.163 | **0.553** | **+0.390 (+239%)** |
| Execution accuracy | **22%** | 4% | −18 pp |
| Exact match | **4%** | 0% | −4 pp |

LoRA v1 produces MongoDB queries that are much closer in structure to gold references, but fewer queries return correct result sets when executed against live databases.

---

## Documentation — strong embedding gain, judge score down

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Embedding similarity** | 0.714 | **0.889** | **+0.175 (+24.5%)** |
| Judge score (0–10) | **3.4** | 2.2 | −1.2 (−36%) |

Generated documentation is semantically closer to references by embedding distance, but the LLM judge rates LoRA v1 output lower on correctness, completeness, clarity, and relevance.

---

## Takeaways

- **SQL2NoSQL:** LoRA v1 is the clearest structural win — **3.4×** structural similarity (0.16 → 0.55) — but execution accuracy and exact match both fall.
- **Documentation:** Embedding similarity improves substantially (0.71 → 0.89), yet the judge score drops (3.4 → 2.2), suggesting surface-level semantic overlap without satisfying the rubric.
- **Text2SQL:** Both runs remain weak on exact match (0%); LoRA v1 is roughly flat on structure and slightly worse on execution (12% → 10%).
- **Training scale:** Despite training on only 50 samples for 10 epochs, LoRA v1 shows meaningful structural and embedding gains on sql2nosql and documentation — but execution-based metrics do not yet reflect those improvements.
