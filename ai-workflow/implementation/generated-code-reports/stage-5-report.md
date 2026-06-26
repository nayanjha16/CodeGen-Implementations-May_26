# Generated Code Report — Stage 5

> **Feature:** `lora-finetuning`  
> **Date:** 2026-06-25

## Files Created

| Path | Purpose |
|------|---------|
| `src/training/adapter_verify.py` | Verify adapter files + `run_metadata.json` |
| `scripts/train_all_lora.py` | Train all tasks + optional baseline + summary |
| `scripts/verify_lora_adapters.py` | CLI adapter verification |
| `tests/training/test_adapter_verify.py` | Verify helper tests |

## Files Modified

| Path | Purpose |
|------|---------|
| `src/training/lora_trainer.py` | `load_best_model_at_end`, metadata enrichment |
| `scripts/train_lora.py` | `--version` run folder |

## Validation Status

| Check | Result |
|-------|--------|
| `python scripts/verify_lora_adapters.py --version v1` | ✅ 3/3 adapters OK |
| `python -m unittest tests.training.test_adapter_verify` | ✅ 2/2 pass |
| Adapter artifacts present | ✅ `adapter_config.json`, `adapter_model.safetensors`, `run_metadata.json` |

## CLI — Full Training

```bash
# All tasks, default run folder (DDMM, e.g. 2506)
python scripts/train_all_lora.py

# Named run + optional baseline first
python scripts/train_all_lora.py --version 2506-full --run-baseline

# Subset smoke (fast)
python scripts/train_all_lora.py --version smoke --max-samples 100 --epochs 3

# Verify a run
python scripts/verify_lora_adapters.py --version v1
```

## Completed Run (`v1`)

Three adapters under `models/checkpoints/v1/{text2sql,sql2nosql,nosql2doc}/` with finite eval loss and MLflow-ready metadata (MLflow disabled for this run).
