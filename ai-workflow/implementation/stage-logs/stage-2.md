# Stage Log — LoRA Fine-Tuning Stage 2

> **Feature:** `lora-finetuning`  
> **Date:** 2026-06-25

## Implemented Tasks

| ID | Task | Status |
|----|------|--------|
| S-01 | Extend `tasks.py` with column maps, response templates, dataset config helpers | ✅ |
| S-02 | `filters.py` — required-field filter + skip reason logging | ✅ |
| S-03 | `prompt_factory.py` — wire existing prompt builders | ✅ |
| S-04 | `tend_dataset.py` — HF TEND loader (spider + bird train) → SFT examples | ✅ |
| S-05 | `token_stats.py` — token distribution logging | ✅ |
| S-06 | `tests/training/test_prompt_parity.py` | ✅ |
| S-07 | Dataset filter + example shape tests (same file) | ✅ |

## Changed Files

| Path | Change |
|------|--------|
| `src/training/tasks.py` | Task specs, HF dataset config helpers |
| `src/training/filters.py` | Created |
| `src/training/prompt_factory.py` | Created |
| `src/training/tend_dataset.py` | Created |
| `src/training/token_stats.py` | Created |
| `src/training/__init__.py` | Updated exports (avoid circular imports) |
| `configs/default.yaml` | `training.datasets` / `eval_datasets` for spider + bird |
| `scripts/build_sft_dataset.py` | Smoke CLI |
| `tests/training/test_prompt_parity.py` | Created |

## Assumptions

- **Training corpus:** `care2achieve/tend` spider train (6,730) + bird train (3,967) = **10,697 rows**
- **Eval corpus:** spider test (859) + bird test (766) = **1,625 rows**
- **Quality filter:** required-field completeness only (HF rows lack `overall_correct`; use all complete rows)
- **Prompt parity:** training prompts match runtime `build_*_prompt` helpers (includes `Task:` prefix)

## Blockers

None.

## Next Stage

Stage 3 — LoRA trainer (`lora_trainer.py`, `train_lora.py`, overfit smoke test).
