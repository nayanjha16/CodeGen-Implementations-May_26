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
| LoRA v1 | `results/spider_gold_validation_codegen-350M-multi_lora-v1_0607_2108/metrics.json` |

## Summary

With the updated evaluation stack (execution accuracy, structural similarity, embedding similarity, and a 0–10 judge score), LoRA v1 shows **clear gains on text2sql and documentation**, with **sql2nosql unchanged in the structural/execution trade-off** seen earlier.

The strongest wins are **text2sql execution accuracy** (12% → 20%), **text2sql structural similarity** (0.70 → 0.79), and **documentation embedding similarity** (0.71 → 0.89). **SQL2NoSQL structural similarity** remains much higher under LoRA (0.16 → 0.55), but **execution accuracy** still regresses (22% → 4%). The documentation **judge score** also improves (0.1 → 1.5 on a 0–10 scale), though both runs remain low in absolute terms.

---

## Text2SQL — execution, structure, and exact match all improve

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Execution accuracy** | 12% | **20%** | **+8 pp** |
| **Structural similarity** | 0.700 | **0.792** | **+0.092 (+13.1%)** |
| **Exact match** | 0% | **8%** | **+8 pp** |

LoRA v1 improves across all three text2sql metrics on this split — the clearest overall task-level win.

---

## SQL2NoSQL — large structural gain, execution regresses

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Structural similarity** | 0.163 | **0.553** | **+0.390 (+239%)** |
| Execution accuracy | **22%** | 4% | −18 pp |
| Exact match | **4%** | 0% | −4 pp |

LoRA v1 produces MongoDB queries that are much closer in structure to gold references, but fewer queries return correct result sets when executed against live databases.

---

## Documentation — embedding and judge score both improve

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Embedding similarity** | 0.714 | **0.889** | **+0.175 (+24.5%)** |
| **Judge score (0–10)** | 0.1 | **1.5** | **+1.4** |

Generated documentation is semantically closer to references by embedding distance, and the LLM judge rates LoRA v1 output higher on correctness, completeness, clarity, and relevance. Absolute judge scores remain low for both runs (baseline max 2.3, LoRA v1 max 10.0).

---

## Takeaways

- **Text2SQL:** LoRA v1 is the clearest win — execution accuracy **12% → 20%**, structural similarity **0.70 → 0.79**, and exact match **0% → 8%**.
- **SQL2NoSQL:** LoRA v1 retains a **3.4×** structural similarity gain (0.16 → 0.55), but execution accuracy and exact match both fall (22% → 4%, 4% → 0%).
- **Documentation:** Both embedding similarity (0.71 → 0.89) and judge score (0.1 → 1.5) improve under LoRA v1, though overall documentation quality remains weak in absolute terms.
- **Training scale:** Despite training on only 50 samples for 10 epochs, LoRA v1 shows meaningful gains on text2sql and documentation; sql2nosql structural improvements still do not translate to better execution accuracy.
