# Current State — CodeGen Studio

> Updated after **Stage 1 implementation** (2026-06-21).

## Active Initiative — TENDv2 (Ollama) — 2026-06-24

- **Phase**: Chunked/resumable pipeline **implemented** (2026-06-24).
- **Goal**: `TENDv2/` mirrors `TENDv1/` but uses local Ollama models —
  `qwen2.5-coder:3b` (Mongo schema/query + documentation) and `qwen3:4b` (judge).
- **Key pieces**: shared `src/llm/ollama_client.py` (async+sync), async pipeline
  with bounded concurrency, incremental CSV writes to `data/TENDv2/`.
- **Datasets**: Spider first, then BIRD (train/test).
- **New (2026-06-24)**: Chunked pipeline implemented — 500-record JSON chunks,
  resumable bronze processing, stable merged CSVs (no timestamps).
- Plan: `feature-plans/tendv2-chunked-pipeline-plan.md` (approved via implement request).
- Stage log: `implementation/stage-logs/tendv2-chunked-pipeline.md`

---


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
