# Executive Summary

## Project Title

**CodeGen Fine-Tuning with PEFT & LoRA**

Fine-tuning `Salesforce/codegen-350M-multi` with Parameter-Efficient Fine-Tuning (PEFT) via LoRA on three database query tasks: Text→SQL, SQL→MongoDB, and NoSQL→Documentation.

---

## Problem Statement

Modern database systems span relational (SQL) and document (NoSQL) stores. Developers and analysts need to:

1. Translate natural-language questions into SQL
2. Convert SQL queries to MongoDB shell syntax
3. Generate human-readable documentation for NoSQL queries

Large language models can perform these tasks, but full fine-tuning of multi-billion-parameter models is expensive and impractical for research or edge deployment. **Small code LMs (350M parameters)** offer a lightweight alternative, but zero-shot performance on structured database tasks is often insufficient.

---

## Objectives

| # | Objective | Status |
|---|-----------|--------|
| 1 | Build a modular, reproducible pipeline for three database query tasks | ✅ Complete |
| 2 | Evaluate baseline (zero-shot) performance on a fixed benchmark | ✅ Complete |
| 3 | Fine-tune task-specific LoRA adapters (smoke run on 50 samples) | ✅ Complete |
| 4 | Compare baseline vs fine-tuned models with automated + semantic metrics | ✅ Complete |
| 5 | Support multiple hardware backends (CUDA, MPS, DirectML, CPU) | ✅ Complete |
| 6 | Full-scale LoRA training on complete TEND dataset | 🔜 Next step |

---

## Approach

We use **Parameter-Efficient Fine-Tuning (PEFT) via LoRA** on a single shared base model (`codegen-350M-multi`). Each of the three tasks gets its own small adapter (~few MB) while base weights remain frozen.

```
Natural Language ──► [Text2SQL adapter] ──► SQL
SQL ──► [SQL2NoSQL adapter] ──► MongoDB query
MongoDB query ──► [NoSQL2Doc adapter] ──► Documentation
```

Tasks are **evaluated and trained independently** using gold supervision from the TEND dataset — predictions from one stage are never fed into the next during benchmarking.

---

## Key Contributions

1. **End-to-end research pipeline** — dataset loading, prompt construction, generation, validation, metrics, and MLflow tracking in a single modular codebase
2. **Prompt parity** — training prompts match inference prompts exactly (verified by unit tests)
3. **Multi-metric evaluation** — Exact Match, Execution Accuracy, CodeBLEU, BERTScore, plus Ollama LLM-as-judge for semantic correctness
4. **Reproducible benchmark** — frozen 50-example Spider gold validation set for before/after comparison
5. **Demonstrated LoRA gains** — even a smoke-scale run (50 samples, 10 epochs) shows measurable improvement over baseline

---

## Key Results (LoRA v1 vs Baseline)

Evaluated on 50-example Spider gold validation set with `qwen3:4b` semantic judge:

| Task | Best improvement | Highlight metric |
|------|------------------|------------------|
| **Text2SQL** | Judge accuracy **4% → 14%** (+250%) | Syntax validity 98% → 100% |
| **SQL2NoSQL** | Structural equivalence **44% → 76%** | Syntax validity 26% → 98% |
| **Documentation** | CodeBLEU **0.03 → 0.24** (+705%) | Translation success 28% → 76% |

See [Results & Analysis](05-results-and-analysis.md) for full tables.

---

## Limitations & Future Work

**Current limitations**

- LoRA v1 is a smoke run — trained on only 50 samples for 10 epochs
- Execution accuracy remains 0% in this repo — Spider SQLite DBs are not bundled locally
- Documentation judge score still 0% despite large automated metric gains — LLM judge is an interim validation method

**Next steps**

1. **Execution-verified gold data (TEND project)** — companion repo at `/Volumes/Work/TEND` generates bronze rows by executing SQL and MongoDB queries against live databases, then filters to silver (execution-verified) and gold tiers for training and validation
2. **Replace LLM judge with query execution** — validate generated SQL and MongoDB outputs by executing them against live databases and comparing result sets (same approach as TEND), instead of relying on Ollama semantic judging
3. **Full-scale LoRA training** — train all three task adapters on the complete TEND corpus (~10,697 train rows)
4. **Full validation** — benchmark on TEND test split (~1,625 rows) and refreshed gold validation sets from TEND silver/gold pipeline

---

## Tech Stack (Summary)

| Layer | Technology |
|-------|------------|
| Language | Python 3.11 |
| Model | HuggingFace Transformers, PEFT, TRL SFTTrainer |
| Base LM | Salesforce/codegen-350M-multi |
| Dataset | TEND (care2achieve/tend) — Spider + BIRD |
| Metrics | BLEU, ROUGE-L, BERTScore, CodeBLEU, Ollama judge |
| Tracking | MLflow (SQLite backend) |
| Config | YAML + `.env` |
