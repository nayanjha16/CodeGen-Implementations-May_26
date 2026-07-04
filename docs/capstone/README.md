# Capstone Project Documentation — CodeGen Fine-Tuning with PEFT & LoRA

Parameter-efficient fine-tuning of `codegen-350M-multi` on three database query tasks using LoRA adapters.

This folder contains all documentation needed to **present, defend, and demonstrate** the capstone project.

---

## Document Index

| # | Document | Purpose | Audience |
|---|----------|---------|----------|
| 1 | [Executive Summary](01-executive-summary.md) | Problem, goals, contributions, key results | Committee, slides intro |
| 2 | [System Architecture](02-system-architecture.md) | High-level diagrams: system, training, evaluation, validation | Architecture review, poster |
| 3 | [Methodology](03-methodology.md) | Training, testing, validation workflows and design decisions | Technical Q&A |
| 4 | [Data & Datasets](04-data-and-datasets.md) | TEND corpus, splits, gold validation set | Data methodology section |
| 5 | [Results & Analysis](05-results-and-analysis.md) | Baseline vs LoRA metrics, findings, limitations | Results slides |
| 6 | [Tech Stack & Reproducibility](06-tech-stack-reproducibility.md) | Dependencies, config, hardware, MLflow | Appendix, demo setup |
| 7 | [Presentation Guide](07-presentation-guide.md) | Slide outline and talking points | Live defense |

---

## Quick Reference

| Item | Value |
|------|-------|
| **Project name** | CodeGen Fine-Tuning with PEFT & LoRA |
| **Base model** | [Salesforce/codegen-350M-multi](https://huggingface.co/Salesforce/codegen-350M-multi) |
| **Fine-tuning** | LoRA (PEFT) — one adapter per task |
| **Tasks** | Text→SQL, SQL→MongoDB, NoSQL→Documentation |
| **Training data** | TEND (Spider + BIRD, ~10,697 train rows) |
| **Benchmark eval** | Frozen 50-example Spider gold validation set |
| **Primary scripts** | `scripts/train_all_lora.py`, `scripts/run_baseline_eval.py` |

---

## Recommended Reading Order

1. **Executive Summary** — start here for a 5-minute overview
2. **System Architecture** — use diagrams in slides or poster
3. **Methodology** — explain how training, testing, and validation differ
4. **Results & Analysis** — support claims with numbers
5. **Presentation Guide** — rehearse slides and Q&A

---

## Related Project Docs

- [README.md](../../README.md) — setup, CLI reference, troubleshooting
- [docs/evaluation-and-training.md](../evaluation-and-training.md) — detailed script flows
- [docs/lora-v1-vs-baseline-comparison.md](../lora-v1-vs-baseline-comparison.md) — smoke-run comparison summary
- [data/DATASETS.md](../../data/DATASETS.md) — TEND field definitions
