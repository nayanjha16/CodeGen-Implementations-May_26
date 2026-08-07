# Project Demo — AI-Powered Database Intelligence

Presentation and supporting docs for **Group-44 · Codegen-11 · IIIT Hyderabad · TalentSprint**.  
**Team:** K.Bhavani · Sai Hemanta · Narayanan · **August 2026**

**Repository:** [github.com/nayanjha16/CodeGen-Implementations-May_26](https://github.com/nayanjha16/CodeGen-Implementations-May_26.git) · branch **`Group-44`**

Metrics source of truth: [../reference/version-tracker.md](../reference/version-tracker.md)

---

## Start here

| File | Purpose |
|------|---------|
| **[presentation.html](presentation.html)** | **Live slide deck** (7 slides) — open in browser; use ← → to navigate |

### Slide outline

| # | Slide |
|---|-------|
| 1 | Title — AI-Powered Database Intelligence |
| 2 | Problem → Solution |
| 3 | System Architecture |
| 4 | Results — LoRA v3 vs baseline |
| 5 | Deploy — Cloud Run + Hugging Face |
| 6 | AI Database Agent — live demo |
| 7 | Thank you + links |

---

## Files in this folder

| File | Purpose |
|------|---------|
| [presentation.html](presentation.html) | Browser slide deck |
| [09-reviewer-submission.md](09-reviewer-submission.md) | Full reviewer walkthrough (repo map, verify steps) |
| [01-executive-summary.md](01-executive-summary.md) | One-page problem → approach → v3 results |
| [02-system-architecture.md](02-system-architecture.md) | Architecture diagrams |
| [03-methodology.md](03-methodology.md) | Training, evaluation, validation protocol |
| [04-data-and-datasets.md](04-data-and-datasets.md) | TEND corpus and gold validation set |
| [05-results-and-analysis.md](05-results-and-analysis.md) | Baseline vs v2 vs v3 metrics narrative |
| [06-tech-stack-reproducibility.md](06-tech-stack-reproducibility.md) | Reproduce train / eval / deploy / **agent demo (§5.6)** |

---

## What to use when

| Audience | Use |
|----------|-----|
| **Committee / live demo** | [presentation.html](presentation.html) |
| **Reviewers (deep dive)** | [09-reviewer-submission.md](09-reviewer-submission.md) |
| **Quick intro** | [01-executive-summary.md](01-executive-summary.md) |
| **Exact numbers** | [../reference/version-tracker.md](../reference/version-tracker.md) |
| **Commands** | [../reference/gold-set-commands.md](../reference/gold-set-commands.md) · [../reference/evaluation-and-deploy-runbook.md](../reference/evaluation-and-deploy-runbook.md) |

---

## Production snapshot

| Item | Value |
|------|-------|
| Base model | `Salesforce/codegen-350M-multi` |
| **LoRA v3 (prod)** | r=32 + FFN, 10 epochs, full TEND ~8,040/task · [`configs/default.yaml`](../../configs/default.yaml) |
| Hub | `codegenstudio/codegen-350M-*-lora` |
| API | `fastapi-deploy/codegen_api` on Cloud Run (`checkpoint_version: v3`) |
| Agent | `agent/` — LangGraph + MCP + Web UI |

### Hugging Face

| Artifact | URL |
|----------|-----|
| TEND dataset | [huggingface.co/datasets/care2achieve/tend](https://huggingface.co/datasets/care2achieve/tend) |
| text2sql LoRA | [codegenstudio/codegen-350M-text2sql-lora](https://huggingface.co/codegenstudio/codegen-350M-text2sql-lora) |
| sql2nosql LoRA | [codegenstudio/codegen-350M-sql2nosql-lora](https://huggingface.co/codegenstudio/codegen-350M-sql2nosql-lora) |
| nosql2doc LoRA | [codegenstudio/codegen-350M-nosql2doc-lora](https://huggingface.co/codegenstudio/codegen-350M-nosql2doc-lora) |

### Headline metrics (gold n=50, TEND execution, greedy)

| Task | Baseline | LoRA v3 |
|------|----------|---------|
| Text2SQL exec | 14% | **66%** |
| SQL2NoSQL exec | 22% | **86%** |
| Doc judge /10 | 8.33 | **8.82** |

---

## Related

- [../../README.md](../../README.md) — project setup
- [../../agent/README.md](../../agent/README.md) — AI Database Agent
- [../../fastapi-deploy/README.md](../../fastapi-deploy/README.md) — Cloud Run API
- [../README.md](../README.md) — documentation index
- [../reference/](../reference/) — runbooks and PPTX charts
