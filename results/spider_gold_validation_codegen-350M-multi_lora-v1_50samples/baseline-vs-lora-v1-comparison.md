# Baseline vs LoRA v1 — Comparison Report (n=50)

> **Generated:** 2026-07-04  
> **Base model:** `Salesforce/codegen-350M-multi`  
> **LoRA adapter run:** `v1` (`models/checkpoints/v1/`)  
> **Judge model:** `gemma3:4b` (Ollama)  
> **Dataset:** `spider_gold_validation` (50 examples)  
> **Samples per task:** 50

## Compared runs

| Run | Type | Results folder |
|-----|------|----------------|
| Baseline | Base model only | `results/spider_gold_validation_codegen-350M-multi_baseline_50samples/` |
| LoRA v1 | Fine-tuned adapters | `results/spider_gold_validation_codegen-350M-multi_lora-v1_50samples/` |

**Training context for v1:** Smoke-scale LoRA — 50 training rows, 5 epochs per task.

---

## Executive summary

LoRA v1 **outperforms the baseline on all three tasks** at n=50.

| Task | Judge correct (baseline → LoRA) | Change |
|------|----------------------------------|--------|
| **text2sql** | 4% → **20%** | **+16 pp (5×)** |
| **sql2nosql** | 30% → **62%** | **+32 pp (+107%)** |
| **documentation** | 24% → **56%** | **+32 pp (+133%)** |

LoRA v1 also improves syntax validity, translation success, and similarity metrics across the board. Execution accuracy remains **0%** on both runs (Spider SQLite DBs not wired).

---

## Text-to-SQL

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Judge correct rate** | 4% | **20%** | **+16 pp** |
| Exact match | 4% | **8%** | +4 pp |
| CodeBLEU / BERTScore | 0.554 | **0.629** | +0.075 (+14%) |
| ROUGE-L | 0.422 | **0.574** | +0.152 (+36%) |
| BLEU | 0.046 | **0.113** | +0.067 (+147%) |
| Syntax validity | 98% | **100%** | +2 pp |
| Translation success | 92% | **100%** | +8 pp |
| Execution accuracy | 0% | 0% | — |

**Takeaway:** Clearest relative judge gain (5×). Similarity metrics improve; syntax/translation reach 100%.

---

## SQL-to-MongoDB

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Judge correct rate** | 30% | **62%** | **+32 pp** |
| Syntax validity | 26% | **98%** | **+72 pp** |
| Translation success | 26% | **98%** | **+72 pp** |
| Structural equivalence | 44% | **76%** | **+32 pp** |
| Token F1 | 0.242 | **0.546** | +0.304 (+126%) |
| CodeBLEU / BERTScore | 0.202 | **0.514** | +0.312 (+154%) |
| ROUGE-L | 0.230 | **0.462** | +0.232 (+101%) |
| BLEU | ~0.000 | **0.009** | +0.009 |
| Exact match | 4% | 0% | −4 pp |
| Execution accuracy | 0% | 0% | — |

**Takeaway:** Largest absolute validity gains. Baseline often fails to produce valid MongoDB shell queries (26% validity); LoRA v1 reaches 98%.

---

## MongoDB documentation (nosql2doc)

| Metric | Baseline | LoRA v1 | Change |
|--------|----------|---------|--------|
| **Judge correct rate** | 24% | **56%** | **+32 pp** |
| Syntax validity | 26% | **80%** | **+54 pp** |
| Translation success | 26% | **80%** | **+54 pp** |
| Structural equivalence | 12% | **40%** | **+28 pp** |
| Token F1 | 0.121 | **0.333** | +0.212 (+175%) |
| CodeBLEU / BERTScore | 0.083 | **0.242** | +0.159 (+191%) |
| ROUGE-L | 0.107 | **0.300** | +0.193 (+180%) |
| BLEU | 0.004 | **0.071** | +0.067 (+1647%) |
| Exact match | 0% | 0% | — |
| Execution accuracy | 0% | 0% | — |

**Takeaway:** Documentation quality jumps sharply — judge more than doubles, validity 26% → 80%.

---

## Side-by-side summary (n=50)

| Metric | text2sql (B → L) | sql2nosql (B → L) | documentation (B → L) |
|--------|------------------|-------------------|------------------------|
| Judge correct | 4% → **20%** | 30% → **62%** | 24% → **56%** |
| Exact match | 4% → **8%** | 4% → 0% | 0% → 0% |
| Syntax validity | 98% → **100%** | 26% → **98%** | 26% → **80%** |
| Translation success | 92% → **100%** | 26% → **98%** | 26% → **80%** |
| CodeBLEU | 0.554 → **0.629** | 0.202 → **0.514** | 0.083 → **0.242** |
| ROUGE-L | 0.422 → **0.574** | 0.230 → **0.462** | 0.107 → **0.300** |

*B = baseline, L = LoRA v1*

---

## Caveats

1. **Execution accuracy is 0%** on both runs — Spider SQLite DBs are not wired yet.
2. **Smoke training** — v1 used only 50 train rows; full-dataset training should improve further.
3. **Exact match** uses case-insensitive SQL normalization for text2sql.
4. **Judge variance** — gemma3:4b semantic scores can differ from string/similarity metrics.

---

## Verdict

On the full 50-example Spider gold validation set with `gemma3:4b` judging, **LoRA v1 is clearly better than the unfine-tuned baseline** across all three pipeline tasks. The strongest wins are **sql2nosql** and **documentation** validity (26% → 98% / 80%) and judge accuracy (+32 pp each). **text2sql** judge improves 5× (4% → 20%).

**Preferred configuration:** LoRA v1 adapters over the base model for this workload.

---

## Reproduce

```powershell
# Baseline (n=50)
python scripts/run_baseline_eval.py --max-samples 50 --output spider_gold_validation_codegen-350M-multi_baseline_50samples

# LoRA v1 (n=50)
python scripts/run_baseline_eval.py --max-samples 50 --adapter-run v1 --output spider_gold_validation_codegen-350M-multi_lora-v1_50samples
```
