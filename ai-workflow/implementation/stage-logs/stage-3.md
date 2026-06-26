# Stage Log — LoRA Fine-Tuning Stage 3

> **Feature:** `lora-finetuning`  
> **Date:** 2026-06-25

## Implemented Tasks

| ID | Task | Status |
|----|------|--------|
| T-01 | `lora_config.py` — `build_lora_config()` with verified `target_modules` | ✅ |
| T-02 | `collator.py` — prompt/completion prep + TRL collator helper | ✅ |
| T-03 | `lora_trainer.py` — `train_lora()` orchestrating PEFT + `SFTTrainer` | ✅ |
| T-04 | `mlflow_utils.py` — training run logging | ✅ |
| T-05 | `scripts/train_lora.py` CLI | ✅ |
| T-06 | `tests/training/test_overfit_smoke.py` — 5 rows, 10 epochs | ✅ |
| T-07 | Adapter output verification (`adapter_config.json`, `adapter_model.safetensors`, `run_metadata.json`) | ✅ |

## Changed Files

| Path | Change |
|------|--------|
| `src/training/lora_config.py` | Created — PEFT `LoraConfig` builder |
| `src/training/collator.py` | Created — TRL prompt/completion dataset prep |
| `src/training/lora_trainer.py` | Created — training orchestration |
| `src/training/mlflow_utils.py` | Created — MLflow training logger |
| `src/training/tasks.py` | Fixed response templates to match runtime prompt suffixes |
| `scripts/train_lora.py` | Created — train CLI |
| `tests/training/test_overfit_smoke.py` | Created — overfit smoke test |

## Assumptions

- **TRL 1.6 API:** Uses `prompt`/`completion` columns + `completion_only_loss=True` (replaces deprecated `DataCollatorForCompletionOnlyLM`).
- **Data source:** HF TEND spider+bird train/eval by default; optional `--train-csv` / `--eval-csv` for CSV/JSONL.
- **Overfit smoke:** 5 spider rows, 10 epochs, `skip_eval=True` (~8s on MPS); train loss threshold `< 1.5`.
- **Adapter path:** Defaults to `models/checkpoints/<task>/` via `get_adapter_path()`.

## Blockers

None.

## Next Stage

Stage 4 — Adapter-aware model loading in `model_loader.py` + `test_adapter_load.py`.
