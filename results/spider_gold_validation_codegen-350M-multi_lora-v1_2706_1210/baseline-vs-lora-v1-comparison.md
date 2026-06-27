# Baseline vs LoRA v1 — Comparison Report

> **Generated:** 2026-06-27  
> **Base model:** `Salesforce/codegen-350M-multi`  
> **LoRA adapter run:** `v1` (`models/checkpoints/v1/`)  
> **Judge model:** `gemma3:4b` (Ollama)  
> **Dataset:** `spider_gold_validation`  
> **Samples per task:** 5

## Compared runs

| Run | Type | Results folder |
|-----|------|----------------|
| Baseline | Base model only (no adapter) | `results/spider_gold_validation_codegen-350M-multi_2706_1140/` |
| LoRA v1 | Fine-tuned adapters per task | `results/spider_gold_validation_codegen-350M-multi_lora-v1_2706_1210/` |

**Training context for v1:** Smoke-scale LoRA fine-tuning — 50 training rows, 5 epochs per task (Spider + BIRD train split). Adapters were produced on a prior run; this eval loads them from `models/checkpoints/v1/{text2sql,sql2nosql,nosql2doc}/`.

---

## Executive summary

LoRA v1 **outperforms the baseline on every task** for this 5-sample eval. The largest gains are in **semantic judge accuracy** and **output validity** (especially sql2nosql and documentation). Similarity metrics (BLEU, ROUGE-L, BERTScore/CodeBLEU) also improve across all three stages.

| Task | Judge correct (baseline → v1) | Headline |
|------|-------------------------------|----------|
| **text2sql** | 0% → **40%** | +40 pp; ROUGE-L +63%, BLEU +218% |
| **sql2nosql** | 40% → **100%** | +60 pp; syntax validity 20% → 100% |
| **documentation** | 20% → **100%** | +80 pp; structural equivalence 20% → 100% |

**Still weak on both runs:** Exact match and execution accuracy remain **0%** for all tasks (expected at this model scale and sample size).

---

## Text-to-SQL

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Judge correct rate** | 0% | **40%** | **+40 pp** |
| CodeBLEU / BERTScore | 0.719 | **0.776** | +0.058 (+8%) |
| ROUGE-L | 0.468 | **0.764** | +0.296 (+63%) |
| BLEU | 0.062 | **0.196** | +0.134 (+218%) |
| Syntax validity | 100% | 100% | — |
| Translation success | 100% | 100% | — |
| Exact match | 0% | 0% | — |
| Execution accuracy | 0% | 0% | — |
| Structural equivalence | 0% | 0% | — |

**Takeaway:** Fine-tuning improves semantic overlap with gold SQL and judge agreement, while the base model already produced syntactically valid SQL on all 5 examples.

---

## SQL-to-MongoDB

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Judge correct rate** | 40% | **100%** | **+60 pp** |
| Syntax validity | 20% | **100%** | **+80 pp** |
| Translation success | 20% | **100%** | **+80 pp** |
| Structural equivalence | 60% | **100%** | **+40 pp** |
| Token F1 | 0.287 | **0.714** | +0.427 (+149%) |
| CodeBLEU / BERTScore | 0.214 | **0.796** | +0.582 (+272%) |
| ROUGE-L | 0.275 | **0.425** | +0.150 (+55%) |
| BLEU | 0.000 | **0.041** | +0.041 |
| Exact match | 0% | 0% | — |
| Execution accuracy | 0% | 0% | — |

**Takeaway:** Strongest overall improvement. The baseline often failed to produce valid MongoDB shell queries (20% validity); LoRA v1 reaches full validity and perfect judge score on this subset.

---

## MongoDB documentation (nosql2doc)

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Judge correct rate** | 20% | **100%** | **+80 pp** |
| Structural equivalence | 20% | **100%** | **+80 pp** |
| Syntax validity | 60% | **80%** | +20 pp |
| Translation success | 60% | **80%** | +20 pp |
| Token F1 | 0.213 | **0.435** | +0.222 (+104%) |
| CodeBLEU / BERTScore | 0.161 | **0.313** | +0.152 (+94%) |
| ROUGE-L | 0.171 | **0.371** | +0.201 (+118%) |
| BLEU | 0.005 | **0.146** | +0.141 (+3006%) |
| Exact match | 0% | 0% | — |
| Execution accuracy | 0% | 0% | — |

**Takeaway:** Documentation quality jumps sharply — judge goes from 1/5 to 5/5 correct on this subset, with large gains in overlap metrics.

---

## Metric glossary (quick reference)

| Metric | What it measures |
|--------|------------------|
| **Judge correct rate** | Gemma3:4b semantic equivalence vs gold (Ollama) |
| **Exact match** | Normalized string equality with reference |
| **Execution accuracy** | SQLite result-set match (text2sql only) |
| **Syntax validity** | Output parses as valid SQL / MongoDB / doc |
| **Translation success** | Pipeline stage produced a usable output |
| **Structural equivalence** | Schema/structure alignment with reference |
| **BLEU / ROUGE-L / BERTScore / CodeBLEU** | N-gram, sequence, and code-aware similarity |

---

## Caveats

1. **Small sample size (n=5):** Results are indicative, not statistically robust. Re-run with `--max-samples 50` for a fuller picture.
2. **Smoke training:** v1 adapters were trained on only 50 rows; full-dataset training (~10k rows) should yield larger gains.
3. **Same eval set:** Both runs used the same frozen `data/spider_gold_validation.jsonl` subset (first 5 examples).
4. **Per-task adapters:** LoRA eval loads a different adapter for each pipeline stage (`text2sql`, `sql2nosql`, `nosql2doc`).

---

## How to reproduce

```powershell
# Baseline
python scripts/run_baseline_eval.py --max-samples 5

# LoRA v1 (requires adapters under models/checkpoints/v1/)
python scripts/run_baseline_eval.py --max-samples 5 --adapter-run v1
```

---

## Verdict

For this paired 5-example eval on Spider gold validation, **LoRA v1 is clearly better than the unfine-tuned baseline** across all three pipeline tasks. The fine-tuned run should be treated as the preferred configuration for downstream use until a newer adapter run (e.g. `v2` on full data) is available.
