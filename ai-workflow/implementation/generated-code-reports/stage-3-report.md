# Generated Code Report — Stage 3

> **Feature:** `lora-finetuning`  
> **Date:** 2026-06-25

## Files Created

| Path | Purpose |
|------|---------|
| `src/training/lora_config.py` | Build PEFT `LoraConfig` from YAML |
| `src/training/collator.py` | Prompt/completion dataset prep for TRL completion-only loss |
| `src/training/lora_trainer.py` | `train_lora()` — model load, PEFT wrap, SFTTrainer, save adapter |
| `src/training/mlflow_utils.py` | MLflow logging for training runs |
| `scripts/train_lora.py` | CLI for per-task LoRA training |
| `tests/training/test_overfit_smoke.py` | Overfit smoke test (5 rows → adapter files + low loss) |

## Files Modified

| Path | Purpose |
|------|---------|
| `src/training/tasks.py` | Response templates aligned with runtime prompt suffixes |

## Validation Status

| Check | Result |
|-------|--------|
| `python -m unittest tests.training.test_prompt_parity` | ✅ 5/5 pass |
| `python -m unittest tests.training.test_overfit_smoke` | ✅ 1/1 pass (train_loss=1.38, adapter files written) |
| Linter (`src/training/`) | ✅ No issues |

## API Additions

```python
from src.training.lora_trainer import train_lora, TrainLoraResult

result = train_lora(
    "text2sql",
    max_samples=5,
    epochs=10,
    skip_eval=True,
)
result.output_dir          # Path to adapter dir
result.train_loss          # Final training loss
result.metadata_path       # run_metadata.json
```

## CLI Additions

```bash
python scripts/train_lora.py --task text2sql
python scripts/train_lora.py --task text2sql --max-samples 50 --epochs 1 --no-mlflow
python scripts/train_lora.py --task sql2nosql --train-csv path/to/train.csv --output-dir models/checkpoints/sql2nosql/
```

## Adapter Output Layout

```
models/checkpoints/<task>/
  adapter_config.json
  adapter_model.safetensors
  run_metadata.json
```
