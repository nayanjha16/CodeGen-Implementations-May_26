# Baseline vs LoRA v2 — Comparison Report (n=50, execution accuracy enabled)

> **Generated:** 2026-07-19  
> **Base model:** `Salesforce/codegen-350M-multi`  
> **Dataset:** `spider_gold_validation` (50 examples)  
> **Database execution:** **True** on both runs (Postgres + Mongo via TEND)  
> **Judge:** skipped on LoRA v2 (`--no-judge`); baseline judge timed out before writing `metrics.json`

## Compared runs

| Run | Type | Source |
|-----|------|--------|
| Baseline | Base model only (no adapter) | Console metrics from EX-enabled run 2026-07-19 (pipeline completed; Ollama judge export failed) |
| LoRA v2 | Full-corpus LoRA adapters | `results/spider_gold_validation_codegen-350M-multi_lora-v2_50samples_1907/metrics.json` |

Both runs used live DB execution (`Database execution available: True`). Documentation judge scores are not comparable (baseline judge aborted; v2 used `--no-judge`).

**Training context**

| Run | Training |
|-----|----------|
| Baseline | Zero-shot CodeGen-350M |
| LoRA v2 | Full LoRA adapters under `models/checkpoints/v2/` |

---

## Executive summary

LoRA v2 **outperforms baseline on every primary EX / EM / structural metric**.

| Task | Metric | Baseline → LoRA v2 | Change |
|------|--------|--------------------|--------|
| **text2sql** | Execution accuracy | 8% → **60%** | **+52 pp** |
| **text2sql** | Exact match | 2% → **14%** | **+12 pp** |
| **sql2nosql** | Execution accuracy | 12% → **46%** | **+34 pp** |
| **sql2nosql** | Exact match | 4% → **28%** | **+24 pp** |
| **documentation** | Embedding similarity | 0.745 → **0.921** | **+0.176** |

---

## Text-to-SQL

| Metric | Baseline | LoRA v2 | Change |
|--------|----------|---------|--------|
| **Execution accuracy** | 8% | **60%** | **+52 pp** |
| **Exact match** | 2% | **14%** | **+12 pp** |
| Structural similarity | 0.678 | **0.925** | +0.247 |

**Takeaway:** With live Postgres scoring, LoRA v2 reaches **60% EX** vs **8%** zero-shot.

---

## SQL-to-MongoDB

| Metric | Baseline | LoRA v2 | Change |
|--------|----------|---------|--------|
| **Execution accuracy** | 12% | **46%** | **+34 pp** |
| **Exact match** | 4% | **28%** | **+24 pp** |
| Structural similarity | 0.244 | **0.900** | +0.656 |

**Takeaway:** LoRA v2 is much stronger on structure and execution match against gold SQL results in Mongo.

---

## MongoDB documentation (nosql2doc)

| Metric | Baseline | LoRA v2 | Change |
|--------|----------|---------|--------|
| **Embedding similarity** | 0.745 | **0.921** | +0.176 |
| Judge score (0–10) | n/a (timed out) | n/a (`--no-judge`) | — |

**Takeaway:** Semantic embedding quality improves under LoRA v2. Judge scores were not collected in either of these EX-focused runs.

---

## Interpretation

1. **Fair EX comparison:** both runs scored against live TEND Postgres/Mongo (`database_execution: true`).  
2. **Largest absolute EX gain:** text2sql **+52 pp** (8% → 60%).  
3. **sql2nosql** gains **+34 pp EX** and a large structural jump (0.24 → 0.90).  
4. **Judge scores** need a follow-up run with Ollama healthy (omit `--no-judge`) for documentation quality comparison.

---

## Reproduce

```powershell
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH = (Get-Location).Path
$env:TEND_REPO_PATH = "C:/Users/Bhavani/Documents/Codegen/TEND"

# Baseline (no adapter; keep TEND DBs healthy)
python scripts/run_baseline_eval.py --max-samples 50 --no-judge --output spider_gold_validation_codegen-350M-multi_baseline_50samples

# LoRA v2
python scripts/run_baseline_eval.py --max-samples 50 --adapter-run v2 --no-judge --output spider_gold_validation_codegen-350M-multi_lora-v2_50samples_1907
```

---

## Artifact paths

| Artifact | Path |
|----------|------|
| LoRA v2 metrics | `results/spider_gold_validation_codegen-350M-multi_lora-v2_50samples_1907/metrics.json` |
| Baseline EX numbers | Console log from 2026-07-19 EX baseline run (text2sql EX 8%, sql2nosql EX 12%, doc embed 0.745) |
| This report | `results/spider_gold_validation_codegen-350M-multi_lora-v2_50samples_1907/baseline-vs-lora-v2-comparison.md` |
