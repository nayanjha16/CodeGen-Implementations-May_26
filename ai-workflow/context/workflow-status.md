# Workflow Status — CodeGen Studio

## Active Initiative — TENDv2 (Ollama)

- **Phase**: Implementation — chunked pipeline complete (2026-06-24)
- Plan: `ai-workflow/planning/feature-plans/tendv2-ollama-plan.md`

---

## LoRA Fine-Tuning Initiative

- **Phase**: Implementation — **Stage 4 complete**
- **Active stage**: Stage 5 — Full training runs (next)
- **Date**: 2026-06-25

### Initiative

Add **parameter-efficient fine-tuning (LoRA)** for three tasks — **text2sql**,
**sql2nosql**, **nosql2doc** — trained on **spider + bird train** from HF TEND
(`care2achieve/tend`).

### Approval

- **Status**: APPROVED (2026-06-21)

### Phase Checklist

| Phase | Status |
|-------|--------|
| Research | ✅ Complete |
| Planning | ✅ Complete |
| Approval | ✅ Approved |
| Implementation Stage 1 (Foundation) | ✅ Complete |
| Implementation Stage 2 (Dataset builder) | ✅ Complete |
| Implementation Stage 3 (LoRA trainer) | ✅ Complete |
| Implementation Stage 4 (Adapter loading) | ✅ Complete |
| Implementation Stages 5–6 | ⬜ Pending |
| Validation | ⬜ Not started |
| Optimization | ⬜ Not started |

### Stage 4 Artifacts

| Artifact | Path |
|----------|------|
| Stage log | `ai-workflow/implementation/stage-logs/stage-4.md` |
| Code report | `ai-workflow/implementation/generated-code-reports/stage-4-report.md` |
| Adapter load tests | `tests/training/test_adapter_load.py` |

### Locked Decisions

- Base model: `Salesforce/codegen-350M-multi`
- Training data: **spider train + bird train** (10,697 rows)
- Eval data: **spider test + bird test** (1,625 rows)
- Adapter save path: `models/checkpoints/<task>/`
- Loading: base from `models/base/`, adapter via `load_model(adapter=<task>)`

### Next Steps (Stage 5)

1. Train text2sql adapter: `python scripts/train_lora.py --task text2sql`
2. Train sql2nosql adapter
3. Train nosql2doc adapter
4. Each saves to `models/checkpoints/<task>/` with `run_metadata.json`

### Reference

- Feature plan: `ai-workflow/planning/feature-plans/lora-finetuning-plan.md`
- Current state: `ai-workflow/context/current-state.md`
