# Project Demo — CodeGen Fine-Tuning with PEFT & LoRA

Presentation and supporting docs for **Group-44 · Codegen-11 · IIITH**.  
**Team:** K.Bhavani · Sai Hemanta · Narayanan

**Repository:** [github.com/nayanjha16/CodeGen-Implementations-May_26](https://github.com/nayanjha16/CodeGen-Implementations-May_26.git) · branch **`Group-44`**

All facts match the root repo. **Metrics:** [../reference/version-tracker.md](../reference/version-tracker.md)

---

## Files in this folder (lean set)

| File | Purpose |
|------|---------|
| **[presentation.html](presentation.html)** | **Live slide deck** — open in browser for demo |
| **[09-reviewer-submission.md](09-reviewer-submission.md)** | **Reviewer guide** — team, TEND, folder map, verify steps |
| [01-executive-summary.md](01-executive-summary.md) | One-page problem → approach → v3 results |
| [02-system-architecture.md](02-system-architecture.md) | Architecture diagrams (training, eval, agent, Cloud Run) |
| [03-methodology.md](03-methodology.md) | Training, evaluation, validation protocol |
| [04-data-and-datasets.md](04-data-and-datasets.md) | TEND corpus and gold validation set |
| [05-results-and-analysis.md](05-results-and-analysis.md) | Baseline vs v2 vs v3 metrics |
| [06-tech-stack-reproducibility.md](06-tech-stack-reproducibility.md) | Dependencies, config, reproduce train/eval/deploy/**agent demo** |

Removed (redundant with deck + docs above): ~~`07-presentation-guide.md`~~, ~~`08-final-presentation-detailed.md`~~, ~~`final-presentation.html`~~.

---

## What to use when

| Audience | Read |
|----------|------|
| **Committee / live demo** | [presentation.html](presentation.html) |
| **Reviewers** | [09-reviewer-submission.md](09-reviewer-submission.md) |
| **Quick intro** | [01-executive-summary.md](01-executive-summary.md) |
| **Exact numbers** | [../reference/version-tracker.md](../reference/version-tracker.md) |
| **Commands** | [../reference/gold-set-commands.md](../reference/gold-set-commands.md) · [../reference/evaluation-and-deploy-runbook.md](../reference/evaluation-and-deploy-runbook.md) |
| **Reproduce agent demo** | [06-tech-stack-reproducibility.md §5.6](06-tech-stack-reproducibility.md#56-run-ai-database-agent-demo) |

---

## Production snapshot

| Item | Value |
|------|-------|
| Base model | `Salesforce/codegen-350M-multi` |
| **LoRA v3 (prod)** | r=32 + FFN, 10 epochs, full TEND ~8,040/task · [`configs/default.yaml`](../../configs/default.yaml) |
| Hub | `codegenstudio/codegen-350M-*-lora` |
| API | `fastapi-deploy/codegen_api` on Cloud Run (`checkpoint_version: v3`) |
| Demo | `agent/` — LangGraph + MCP + Web UI |

### Hugging Face links

| Artifact | URL |
|----------|-----|
| TEND dataset | [huggingface.co/datasets/care2achieve/tend](https://huggingface.co/datasets/care2achieve/tend) |
| text2sql LoRA | [codegenstudio/codegen-350M-text2sql-lora](https://huggingface.co/codegenstudio/codegen-350M-text2sql-lora) |
| sql2nosql LoRA | [codegenstudio/codegen-350M-sql2nosql-lora](https://huggingface.co/codegenstudio/codegen-350M-sql2nosql-lora) |
| nosql2doc LoRA | [codegenstudio/codegen-350M-nosql2doc-lora](https://huggingface.co/codegenstudio/codegen-350M-nosql2doc-lora) |

### Headline metrics (gold n=50, TEND execution, greedy)

| Task | Baseline v3 | LoRA v3 |
|------|-------------|---------|
| Text2SQL exec | 14% | **66%** |
| SQL2NoSQL exec | 22% | **86%** |
| Doc judge /10 | 8.33 | **8.82** |

### LoRA ladder

| Version | Train | Epochs | Role |
|---------|-------|--------|------|
| v1 | 50 rows/task | 10 | Smoke |
| v2 | ~8,040 TEND, r=16 | 5 | Full corpus |
| **v3** | ~8,040 TEND, r=32+FFN | 10 | **Production** |

---

## Root project docs

- [../../README.md](../../README.md)
- [../../agent/README.md](../../agent/README.md)
- [../../fastapi-deploy/README.md](../../fastapi-deploy/README.md)
- [../reference/](reference/) — version tracker, runbooks, PPTX
- [../README.md](../README.md) — documentation index
