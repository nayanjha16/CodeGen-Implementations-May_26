# Stage Log — LoRA Fine-Tuning Stage 5

> **Feature:** `lora-finetuning`  
> **Date:** 2026-06-25

## Implemented Tasks

| ID | Task | Status |
|----|------|--------|
| R-01 | Optional baseline eval via `train_all_lora.py --run-baseline` | ✅ |
| R-02 | Train text2sql adapter | ✅ (`v1` run, 50-row subset) |
| R-03 | Train sql2nosql adapter | ✅ (`v1` run, 50-row subset) |
| R-04 | Train nosql2doc adapter | ✅ (`v1` run, 50-row subset) |
| R-05 | `run_metadata.json` + training summary per run | ✅ |

## Changed Files

| Path | Change |
|------|--------|
| `src/training/lora_trainer.py` | Best-checkpoint saving, richer metadata, `checkpoint_run` |
| `src/training/adapter_verify.py` | Created — verify adapter artifacts |
| `scripts/train_all_lora.py` | Batch training, baseline hook, run logging (fixed indent) |
| `scripts/verify_lora_adapters.py` | Created — CLI verification |
| `scripts/train_lora.py` | `--version` / run folder support |
| `tests/training/test_adapter_verify.py` | Created |

## Training Run — `v1`

| Task | Train rows | Eval loss | Adapter path |
|------|------------|-----------|--------------|
| text2sql | 50 | 1.21 | `models/checkpoints/v1/text2sql/` |
| sql2nosql | 50 | 0.86 | `models/checkpoints/v1/sql2nosql/` |
| nosql2doc | 50 | 2.19 | `models/checkpoints/v1/nosql2doc/` |

Verify: `python scripts/verify_lora_adapters.py --version v1`

Summary: `models/checkpoints/v1/training_summary_20260625_232657.json`

## Assumptions

- **Subset run:** `v1` used 50 train/eval rows per task (smoke-scale validation of full pipeline).
- **Full corpus:** Run without `--max-samples` (expect hours on MPS; ~30s/step on long sequences).
- **Layout:** `models/checkpoints/<run>/<task>/` via `--version` / `MODEL_ADAPTER_RUN`.
- Full-model baseline for comparison: `train_all_lora.py --run-baseline` (optional before LoRA).

## Blockers

None for pipeline; full-corpus wall-clock is hardware-limited on MPS.

## Next Stage

Stage 6 — Eval integration (`--adapter` on baseline eval) and LoRA vs baseline comparison.
