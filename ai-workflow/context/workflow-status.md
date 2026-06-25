# Workflow Status — CodeGen Studio

## Active Initiative — TENDv2 (Ollama)

- **Phase**: Implementation — chunked pipeline complete (2026-06-24)
- **Summary**: Ollama-powered TEND v2 — codegen `qwen2.5-coder:3b`, judge `qwen3:4b`.
- **Plan**: `ai-workflow/planning/feature-plans/tendv2-ollama-plan.md`
- **Chunked pipeline plan**: `ai-workflow/planning/feature-plans/tendv2-chunked-pipeline-plan.md`
- **Roadmap**: `ai-workflow/planning/implementation-roadmaps/tendv2-roadmap.md`,
  `implementation-roadmaps/tendv2-chunked-roadmap.md`
- **Approval**: `tendv2-ollama-approval.md` (approved);
  `tendv2-chunked-pipeline-approval.md` (approved — implemented)

---

## Current Phase

- **Phase**: Implementation — **Stage 1 complete**
- **Active stage**: Stage 2 — SFT Dataset Builder (next)
- **Date**: 2026-06-21

## Initiative

Add **parameter-efficient fine-tuning (LoRA)** for three tasks — **text2sql**,
**sql2nosql**, **nosql2doc** — trained on the TEND dataset (`data/TEND/`).

## Approval

- **Status**: APPROVED (2026-06-21)
- **Stage 0**: Skipped — user will regenerate full TEND data later

## Phase Checklist

| Phase | Status |
|-------|--------|
| Research | ✅ Complete |
| Planning | ✅ Complete |
| Approval | ✅ Approved |
| Implementation Stage 1 (Foundation) | ✅ Complete |
| Implementation Stage 2 (Dataset builder) | ⏭️ Next |
| Implementation Stages 3–6 | ⬜ Pending |
| Validation | ⬜ Not started |
| Optimization | ⬜ Not started |

## Stage 1 Artifacts

| Artifact | Path |
|----------|------|
| Stage log | `ai-workflow/implementation/stage-logs/stage-1.md` |
| Code report | `ai-workflow/implementation/generated-code-reports/stage-1-report.md` |
| Pre-flight script | `scripts/inspect_lora_modules.py` |

## Locked Decisions

- Base model: `Salesforce/codegen-350M-multi`
- Adapter save path: `models/checkpoints/<task>/`
- LoRA target_modules: `qkv_proj`, `out_proj` (verified)
- Plain LoRA fp32; one adapter per task; no merge

## Next Steps (Stage 2)

1. `src/training/prompt_factory.py` — wire existing prompt builders
2. `src/training/tend_dataset.py` — CSV → HuggingFace Dataset
3. `src/training/filters.py` — `overall_correct == True` filter
4. `tests/training/test_prompt_parity.py`

## Reference

- Feature plan: `ai-workflow/planning/feature-plans/lora-finetuning-plan.md`
- Task breakdown: `ai-workflow/planning/task-breakdowns/lora-finetuning-tasks.md`
- Current state: `ai-workflow/context/current-state.md`
