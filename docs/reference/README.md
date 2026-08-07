# Reference documentation

Technical runbooks, metrics, and reproducibility guides for the CodeGen fine-tuning project.

**Demo package:** [../project-demo/](../project-demo/) — **AI-Powered Database Intelligence** presentation and reviewer docs.

---

## Index

| Document | Purpose |
|----------|---------|
| [version-tracker.md](version-tracker.md) | **Source of truth** — LoRA v1–v3 hyperparameters, gold n=50 metrics, production checklist |
| [gold-set-commands.md](gold-set-commands.md) | Copy-paste commands for the frozen 50-example validation set |
| [evaluation-and-deploy-runbook.md](evaluation-and-deploy-runbook.md) | Baseline → LoRA eval → Hub publish → Cloud Run redeploy |
| [evaluation-and-training.md](evaluation-and-training.md) | Script and module reference for training and evaluation |
| [codegen-350M-multi.md](codegen-350M-multi.md) | Base model architecture, tokenizer, LoRA target modules |
| [Multi_Adapter_Deployment_Plan.md](Multi_Adapter_Deployment_Plan.md) | Multi-adapter Cloud Run design and manifest |

## Presentations

| File | Purpose |
|------|---------|
| [lora-v1-v3-vs-baseline-comparison.pptx](lora-v1-v3-vs-baseline-comparison.pptx) | Full LoRA v1–v3 vs baseline deck |
| [lora-v1-v3-vs-baseline-comparison-short.pptx](lora-v1-v3-vs-baseline-comparison-short.pptx) | Short deck (generated) |

Regenerate charts and PPTX: `python scripts/generate_v1_v3_comparison_charts.py` then `python scripts/generate_lora_v1_v3_presentation.py`.
