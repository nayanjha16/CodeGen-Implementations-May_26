# Workflow Status — CodeGen Studio

## Active Initiative — TENDv2 (Ollama)

- **Phase**: Implementation — chunked pipeline complete (2026-06-24)
- Plan: `ai-workflow/planning/feature-plans/tendv2-ollama-plan.md`

---

## LoRA Fine-Tuning Initiative

- **Phase**: Implementation — **Stage 5 complete**
- **Active stage**: Stage 6 — Eval integration (next)
- **Date**: 2026-06-25

### Phase Checklist

| Phase | Status |
|-------|--------|
| Research | ✅ Complete |
| Planning | ✅ Complete |
| Approval | ✅ Approved |
| Implementation Stages 1–5 | ✅ Complete |
| Implementation Stage 6 | ⬜ Pending |
| Validation | ⬜ Not started |
| Optimization | ⬜ Not started |

### Stage 5 Artifacts

| Artifact | Path |
|----------|------|
| Stage log | `ai-workflow/implementation/stage-logs/stage-5.md` |
| Code report | `ai-workflow/implementation/generated-code-reports/stage-5-report.md` |
| Batch train CLI | `scripts/train_all_lora.py` |
| Verify CLI | `scripts/verify_lora_adapters.py` |
| Adapters (v1 run) | `models/checkpoints/v1/{text2sql,sql2nosql,nosql2doc}/` |

### Next Steps (Stage 6)

1. Extend eval script with `--adapter` / per-task loading
2. Run LoRA eval for each adapter vs baseline
3. Comparison table (`qwen_correct_rate`)

### Reference

- Feature plan: `ai-workflow/planning/feature-plans/lora-finetuning-plan.md`
- Current state: `ai-workflow/context/current-state.md`
