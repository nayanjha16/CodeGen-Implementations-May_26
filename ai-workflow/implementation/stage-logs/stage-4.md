# Stage Log — LoRA Fine-Tuning Stage 4

> **Feature:** `lora-finetuning`  
> **Date:** 2026-06-25

## Implemented Tasks

| ID | Task | Status |
|----|------|--------|
| L-01 | `is_adapter_dir()` — detect `adapter_config.json` | ✅ |
| L-02 | `resolve_adapter_path()` in `model_loader.py` | ✅ |
| L-03 | `CodeGenModel.load()` — base + `PeftModel.from_pretrained()` | ✅ |
| L-04 | `load_model(adapter=..., adapter_path=..., task=...)` + env wiring | ✅ |
| L-05 | `tests/training/test_adapter_load.py` | ✅ |
| L-06 | Docstrings on loader helpers and `CodeGenModel` | ✅ |

## Changed Files

| Path | Change |
|------|--------|
| `src/models/model_loader.py` | Adapter detection, path resolution, PEFT load path |
| `src/models/__init__.py` | Export `is_adapter_dir`, `resolve_adapter_path` |
| `tests/training/test_adapter_load.py` | Created — path + load/generate tests |

## Assumptions

- Base weights always load from `models/base/`; adapters from `models/checkpoints/<task>/`.
- `MODEL_CHECKPOINT` must not point at a LoRA adapter dir (explicit error guides to `MODEL_ADAPTER`).
- Causal LM only for adapters (seq2seq models raise on `adapter_path`).
- Existing full-checkpoint and base-model load paths unchanged when no adapter is set.

## Blockers

None.

## Next Stage

Stage 5 — Full training runs for text2sql, sql2nosql, nosql2doc adapters.
