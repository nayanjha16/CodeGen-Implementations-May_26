# Dataset Reference — TEND (Hugging Face)

Training and evaluation use the published **TEND silver** dataset on Hugging Face:

**Repository:** [care2achieve/tend](https://huggingface.co/datasets/care2achieve/tend)

Loader: `src/datasets/tend_loader.py`

---

## Configurations

| Config | Train rows | Test rows | Notes |
|--------|------------|-----------|-------|
| `spider` | 6,730 | 859 | Spider-derived silver examples |
| `bird` | 3,967 | 766 | BIRD-derived silver examples |

> **Split naming:** `test` corresponds to each source dataset's validation/dev split (Spider `dev`, BIRD `dev`). `train` corresponds to the source training split.

---

## Record schema

Each example includes aligned fields for all three pipeline tasks:

| Field | Used for |
|-------|----------|
| `question` | Text→SQL input |
| `schema` (`sql_schema`) | Text→SQL input |
| `sql` (`sql_query`) | Text→SQL target; SQL→MongoDB input |
| `nosql_schema` | SQL→MongoDB input |
| `nosql_query` | SQL→MongoDB target; Documentation input |
| `documentation` | Documentation target |
| `db_id` | Metadata |
| `id` | Stable example id |

---

## Loading examples

```python
from src.datasets.tend_loader import TENDLoader

# Spider validation (test split)
loader = TENDLoader(config="spider")
examples = loader.load_split("test")

# BIRD training
bird_train = TENDLoader(config="bird").load_split("train")
```

Via Hugging Face `datasets` directly:

```python
from datasets import load_dataset

spider = load_dataset("care2achieve/tend", "spider")
bird = load_dataset("care2achieve/tend", "bird")
```

---

## Evaluation

```bash
python scripts/run_baseline_eval.py --tend-config spider --split test --max-samples 20
python scripts/run_baseline_eval.py --tend-config bird --split train --max-samples 50
```

Smoke test:

```bash
python scripts/test_tend_loader.py
```

---

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `TEND_DATASET_ID` | `care2achieve/tend` | Hugging Face dataset id |
| `TEND_CACHE_DIR` | `~/.cache/codegen/tend` | Local cache for standardized JSONL splits (project-relative path allowed) |

---

## Caching

`TENDLoader` downloads each config/split once, then reads from disk on later runs. Cache layout:

```
{TEND_CACHE_DIR}/care2achieve__tend/{spider|bird}/{train|test}.jsonl
```

To refresh after a dataset update, delete the matching `.jsonl` file or the whole cache directory.

---

## Source credits

TEND is a derived benchmark built on Spider and BIRD. Cite the original datasets when using this release. See the [dataset README](https://huggingface.co/datasets/care2achieve/tend) for citations and license (CC BY 4.0).
