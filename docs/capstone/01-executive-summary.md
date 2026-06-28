# Executive Summary

## Project Title

**CodeGen Studio: Interactive Database Querying Using Small Code Language Models**

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
| 3 | Fine-tune task-specific LoRA adapters on the TEND dataset | ✅ Complete |
| 4 | Compare baseline vs fine-tuned models with automated + semantic metrics | ✅ Complete |
| 5 | Support multiple hardware backends (CUDA, MPS, DirectML, CPU) | ✅ Complete |

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

- Execution accuracy remains 0% — SQLite databases for Spider examples are not bundled
- LoRA v1 trained on only 50 samples (smoke run); full ~10k training expected to improve further
- Documentation task judge score still 0% despite large metric gains — judge calibration needed
- No production API/UI — research-oriented CLI pipeline

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
