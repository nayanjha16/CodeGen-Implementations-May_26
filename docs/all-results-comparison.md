# All Results — Spider Gold Validation Comparison

> **Project:** CodeGen Fine-Tuning with PEFT & LoRA  
> **Date:** 2026-07-06  
> **Model:** `Salesforce/codegen-350M-multi`  
> **Judge model:** `qwen3:8b`  
> **Dataset:** `spider_gold_validation` (50 examples per task)  
> **Execution eval:** PostgreSQL result-set comparison enabled

## Training context

| Run | Adapter | Training samples | Epochs | Scale |
|-----|---------|------------------|--------|-------|
| Baseline | — | — | — | No fine-tuning |
| LoRA v1 | `v1` | 50 | 10 | Smoke-scale |
| LoRA v2 | `v2` | 500 | 5 | Mid-scale |

LoRA v1 was a smoke-scale run to validate the training and evaluation pipeline. LoRA v2 uses **10× more training data** with half the epochs, representing the first meaningful scale-up.

## Compared runs

| Run | Path |
|-----|------|
| Baseline (no adapter) | `results/spider_gold_validation_codegen-350M-multi_0607_1841/metrics.json` |
| LoRA v1 | `results/spider_gold_validation_codegen-350M-multi_lora-v1_0607_2108/metrics.json` |
| LoRA v2 | `results/spider_gold_validation_codegen-350M-multi_lora-v2_0607_2226/metrics.json` |

## Summary

LoRA v2 is the strongest run across all three tasks. Compared to baseline, it more than doubles **text2sql execution accuracy** (12% → 34%), restores **sql2nosql execution accuracy** while also improving structure (22% → 32%, structural similarity 0.16 → 0.79), and delivers the best **documentation** scores (embedding 0.93, judge 3.1).

LoRA v1 already showed clear gains on text2sql and documentation over baseline, but sql2nosql execution regressed despite large structural improvements. LoRA v2 resolves that trade-off: structural similarity continues to climb and execution accuracy now exceeds baseline on sql2nosql as well.

---

## Text2SQL — v2 leads on every metric

| Metric | Baseline | LoRA v1 | LoRA v2 | v1 vs base | v2 vs base | v2 vs v1 |
|--------|----------|---------|---------|------------|------------|----------|
| **Execution accuracy** | 12% | 20% | **34%** | +8 pp | **+22 pp** | **+14 pp** |
| **Structural similarity** | 0.700 | 0.792 | **0.859** | +0.092 | **+0.159 (+22.7%)** | **+0.067 (+8.5%)** |
| **Exact match** | 0% | 8% | **20%** | +8 pp | **+20 pp** | **+12 pp** |

Text2sql improves monotonically with training scale. LoRA v1 already lifted execution accuracy and structure; LoRA v2 extends that trend with the largest absolute gains — especially exact match (0% → 20%).

---

## SQL2NoSQL — v1 structural gain, v2 fixes execution

| Metric | Baseline | LoRA v1 | LoRA v2 | v1 vs base | v2 vs base | v2 vs v1 |
|--------|----------|---------|---------|------------|------------|----------|
| **Structural similarity** | 0.163 | 0.553 | **0.791** | +0.390 (+239%) | **+0.628 (+385%)** | **+0.238 (+43.0%)** |
| **Execution accuracy** | 22% | 4% | **32%** | −18 pp | **+10 pp** | **+28 pp** |
| **Exact match** | 4% | 0% | **8%** | −4 pp | **+4 pp** | **+8 pp** |

LoRA v1 produced MongoDB queries much closer in structure to gold references (3.4× structural similarity), but execution accuracy collapsed (22% → 4%). LoRA v2 retains the structural gains and translates them into correct result sets — execution accuracy rises to 32%, above baseline.

---

## Documentation — steady improvement with scale

| Metric | Baseline | LoRA v1 | LoRA v2 | v1 vs base | v2 vs base | v2 vs v1 |
|--------|----------|---------|---------|------------|------------|----------|
| **Embedding similarity** | 0.714 | 0.889 | **0.926** | +0.175 (+24.5%) | **+0.212 (+29.7%)** | **+0.037 (+4.1%)** |
| **Judge score (0–10)** | 0.1 | 1.5 | **3.1** | +1.4 | **+3.0** | **+1.6** |
| Exact match | 0% | 0% | 0% | — | — | — |

Documentation quality improves with each adapter version. LoRA v2 reaches the highest embedding similarity (0.93) and judge score (3.1), though exact match remains 0% for all runs and absolute judge scores are still modest.

---

## Cross-task overview

| Task | Best run | Key metric | Value |
|------|----------|------------|-------|
| Text2SQL | LoRA v2 | Execution accuracy | 34% |
| SQL2NoSQL | LoRA v2 | Execution accuracy | 32% |
| Documentation | LoRA v2 | Embedding similarity | 0.926 |

---

## Takeaways

- **Text2SQL:** Training scale pays off — execution accuracy climbs **12% → 20% → 34%** across baseline, v1, and v2. Structural similarity and exact match follow the same trend.
- **SQL2NoSQL:** LoRA v1 showed that structural learning does not guarantee execution correctness. LoRA v2 (500 samples, 5 epochs) fixes this: structural similarity reaches **0.79** while execution accuracy rises to **32%**, beating baseline (22%).
- **Documentation:** Both LoRA runs improve over baseline on embedding similarity and judge score. LoRA v2 is best (0.93 embedding, 3.1 judge), but generated docs still fall short of reference quality in absolute terms.
- **Training scale:** Moving from 50 samples × 10 epochs (v1) to 500 samples × 5 epochs (v2) yields the largest gains on sql2nosql execution and text2sql exact match. Smoke-scale v1 validated the pipeline; v2 is the first run where improvements translate consistently across all tasks.
