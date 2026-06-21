# Current State — CodeGen Studio

> Updated after **Stage 1 implementation** (2026-06-21).

## Snapshot

- **Date**: 2026-06-21
- **Phase**: Implementation — **Stage 1 complete**, Stage 2 next
- **Approval**: APPROVED (`lora-finetuning-approval.md`); Stage 0 skipped (user will run data prep later)
- **Base model**: `Salesforce/codegen-350M-multi`

## Stage 1 Deliverables (done)

- `configs/default.yaml` — `training:` + `lora:` blocks (fp32, LoRA r=16, target_modules verified)
- `src/utils/config.py` — `get_training_config()`, `get_lora_config()`, `get_adapter_path(task)`, `get_adapter_name()`
- `src/training/` — package skeleton with `TaskType` enum
- `scripts/inspect_lora_modules.py` — pre-flight check (1.97M trainable params on codegen-350M)
- `.env.example` — `MODEL_ADAPTER` documented; adapters save to `models/checkpoints/<task>/`

## Pending (next stages)

| Stage | Work | Status |
|-------|------|--------|
| 0 | Full TEND data + `manifest.json` | ⏸ Deferred by user |
| 2 | SFT dataset builder + prompt parity tests | ⬜ Next |
| 3 | LoRA trainer + `train_lora.py` | ⬜ |
| 4 | PEFT adapter loading in `model_loader` | ⬜ |
| 5 | Train three adapters | ⬜ |
| 6 | Eval integration + comparison | ⬜ |

## Known Gaps (remaining)

- No `tend_dataset.py` or training loop yet
- No adapter-aware model loading
- Training data: existing smoke CSVs only (`data/TEND/spider_*_0621_*.csv`)

## Validation Status

- Stage 1 pre-flight: ✅ `inspect_lora_modules.py` passed
- No unit test suite yet (`tests/training/` — planned Stage 2+)

## Environment

- Python 3.11 (`conda` env `ai`)
- Run scripts with project conda env or ensure `requirements.txt` installed
