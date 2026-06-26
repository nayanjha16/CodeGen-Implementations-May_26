# Generated Code Report — Stage 2

> **Feature:** `lora-finetuning`  
> **Date:** 2026-06-25

## Files Created

| Path | Purpose |
|------|---------|
| `src/training/filters.py` | Required-field row filter with skip-reason stats |
| `src/training/prompt_factory.py` | Task → runtime prompt builder wiring |
| `src/training/tend_dataset.py` | Load spider+bird HF TEND rows; build SFT `Dataset` |
| `src/training/token_stats.py` | Prompt length statistics |
| `scripts/build_sft_dataset.py` | Smoke CLI for combined train corpus |
| `tests/training/test_prompt_parity.py` | Prompt parity + filter tests |

## Files Modified

| Path | Purpose |
|------|---------|
| `src/training/tasks.py` | `TaskSpec`, response templates, dataset config helpers |
| `src/training/__init__.py` | Export task helpers (lazy imports elsewhere) |
| `configs/default.yaml` | `training.datasets: [spider, bird]`, eval splits |

## Validation Status

| Check | Result |
|-------|--------|
| `python -m unittest tests.training.test_prompt_parity` | ✅ 5/5 pass |
| `python scripts/build_sft_dataset.py` | ✅ 10,697 combined train rows |
| Prompt parity (text2sql, sql2nosql, nosql2doc) | ✅ Matches runtime builders |
| Linter (`src/training/`) | ✅ No issues |

## API Additions

```python
from src.training.tend_dataset import (
    load_tend_training_rows,   # spider + bird train
    load_tend_eval_rows,       # spider + bird test
    build_sft_dataset,         # → SFTBuildResult(dataset, stats, ...)
)

rows = load_tend_training_rows()  # 10,697 rows
result = build_sft_dataset(task="text2sql")
result.dataset  # HuggingFace Dataset with `text` column
```

## CLI Additions

```bash
python scripts/build_sft_dataset.py
```
