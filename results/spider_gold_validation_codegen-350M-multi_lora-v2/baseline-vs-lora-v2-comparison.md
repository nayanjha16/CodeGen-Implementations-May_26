# Baseline vs LoRA v2 — Comparison Report (n=50, execution accuracy enabled)

> **Generated:** 2026-07-11  
> **Base model:** `Salesforce/codegen-350M-multi`  
> **Dataset:** `spider_gold_validation` (50 examples)  
> **Judge model:** `gemma3:4b` (Ollama) on baseline; LoRA v2 run includes judge + embedding scores  
> **Database execution:** **True** on LoRA v2 (`database_execution: true` in metrics); baseline judge run in `baseline-v2` (re-run with TEND for EX export)

## Compared runs

| Run | Type | Results folder |
|-----|------|----------------|
| Baseline | Base model only (no adapter) | `results/spider_gold_validation_codegen-350M-multi_baseline-v2/` |
| LoRA v2 | Full-corpus LoRA adapters | `results/spider_gold_validation_codegen-350M-multi_lora-v2/` |

Both runs use the **same 50-example validation set**. LoRA v2 metrics below are from `metrics.json` with live DB execution enabled.

**Training context**

| Run | Training |
|-----|----------|
| Baseline | Zero-shot CodeGen-350M |
| LoRA v2 | Full TEND (~8k rows / task), **r=16** (attention only), **5 epochs** — adapters under `models/checkpoints/v2/` |

See [docs/reference/version-tracker.md](../../docs/reference/version-tracker.md) for the full v1–v3 hyperparameter table.

---

## Executive summary

LoRA v2 **outperforms baseline on every primary metric** with execution accuracy enabled on the LoRA side.

| Task | Metric | Baseline → LoRA v2 | Change |
|------|--------|--------------------|--------|
| **text2sql** | Execution accuracy | 12% → **60%** | **+48 pp (5×)** |
| **text2sql** | Exact match | 0% → **40%** | **+40 pp** |
| **sql2nosql** | Execution accuracy | 22.2% → **74%** | **+51.8 pp** |
| **sql2nosql** | Exact match | 4% → **62%** | **+58 pp** |
| **sql2nosql** | MongoDB success | 36% → **100%** | **+64 pp** |
| **documentation** | Judge score (0–10) | 6.47 → **8.41** | **+1.94** |
| **documentation** | Embedding similarity | 0.718 → **0.959** | **+0.241** |

> Baseline EX / validity figures are from the paired EX-enabled baseline eval on the same 50 examples. Re-export into `baseline-v2/metrics.json` with `--no-judge` if you need them in JSON.

---

## Text-to-SQL

| Metric | Baseline | LoRA v2 | Change |
|--------|----------|---------|--------|
| **Execution accuracy** | 12% | **60%** | **+48 pp** |
| **Exact match** | 0% | **40%** | **+40 pp** |
| Structural similarity | 0.704 | **0.935** | +0.231 |
| Predicted SQL valid | 98% | **100%** | +2 pp |

**Takeaway:** With live Postgres scoring, LoRA v2 reaches **60% EX** vs **12%** zero-shot. Exact match jumps from 0% to 40%.

---

## SQL-to-MongoDB

| Metric | Baseline | LoRA v2 | Change |
|--------|----------|---------|--------|
| **Execution accuracy** | 22.2% | **74%** | **+51.8 pp** |
| **Exact match** | 4% | **62%** | **+58 pp** |
| Structural similarity | 0.163 | **0.933** | +0.770 |
| MongoDB success (valid output) | 36% | **100%** | **+64 pp** |

**Takeaway:** Baseline often fails to emit valid MongoDB (36% success). LoRA v2 is valid on all 50 samples and reaches **74% execution match** against gold SQL results.

---

## MongoDB documentation (nosql2doc)

| Metric | Baseline | LoRA v2 | Change |
|--------|----------|---------|--------|
| Exact match | 0% | **2%** | +2 pp |
| **Embedding similarity** | 0.718 | **0.959** | +0.241 |
| **Judge score (mean / 10)** | 6.47 | **8.41** | **+1.94** |
| Judge correctness | 6.56 | **8.32** | +1.76 |
| Judge completeness | 5.74 | **7.94** | +2.20 |
| Judge clarity | 6.38 | **8.54** | +2.16 |
| Judge relevance | 7.40 | **8.76** | +1.36 |

**Takeaway:** Exact match stays near zero (wording varies). Semantic quality improves clearly: higher embedding similarity and judge scores across all dimensions.

---

## Interpretation

1. **Fair EX comparison:** LoRA v2 scored against live TEND Postgres/Mongo (`database_execution: true`).  
2. **Largest absolute EX gains:** text2sql +48 pp, sql2nosql +52 pp.  
3. **sql2nosql validity** is a major baseline failure mode (36% → 100%).  
4. **Documentation** improves on judge/embedding even when exact match does not.

---

## Reproduce

```powershell
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH = (Get-Location).Path

# Baseline (no adapter, EX enabled when TEND DBs are up)
python scripts/run_baseline_eval.py --max-samples 50 --output spider_gold_validation_codegen-350M-multi_baseline-v2

# LoRA v2
python scripts/run_baseline_eval.py --max-samples 50 --adapter-run v2 --output spider_gold_validation_codegen-350M-multi_lora-v2
```

---

## Artifact paths

| Artifact | Path |
|----------|------|
| Baseline metrics | `results/spider_gold_validation_codegen-350M-multi_baseline-v2/metrics.json` |
| LoRA v2 metrics | `results/spider_gold_validation_codegen-350M-multi_lora-v2/metrics.json` |
| This report | `results/spider_gold_validation_codegen-350M-multi_lora-v2/baseline-vs-lora-v2-comparison.md` |
