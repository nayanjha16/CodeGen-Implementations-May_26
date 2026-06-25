# CodeGen – Interactive Database Querying Using Small Code Language Models

A modular, reproducible, research-oriented project for evaluating small code language models on database query generation and translation tasks.

**Default model:** [Salesforce/codegen-350M-multi](https://huggingface.co/Salesforce/codegen-350M-multi) (configurable via `.env`)

## Features

- **Natural Language → SQL** generation with greedy and beam search decoding
- **SQL → MongoDB** model-based conversion with gold references from TEND
- **Benchmark evaluation** on the [TEND silver dataset](https://huggingface.co/datasets/care2achieve/tend) (Spider + BIRD configs)
- **Metrics**: Exact Match, Execution Accuracy, BLEU, ROUGE-L, BERTScore, CodeBLEU
- **MLflow** experiment tracking
- **Local caching** — models and datasets download once, then reuse from disk

## Project Structure

```
CodeGen-Studio/
├── src/                     # Application source code
│   ├── text2sql/            # Prompt builder, generator, validator, executor
│   ├── sql2nosql/           # SQL to MongoDB generation + evaluation
│   ├── models/              # HuggingFace model loader (with local cache)
│   ├── datasets/            # TEND Hugging Face loader, preprocessing
│   ├── evaluation/          # Metrics, benchmarks, MLflow tracking
│   └── utils/               # Config, paths, logging, seeds
├── models/
│   ├── base/                # Downloaded HuggingFace models (cached once)
│   └── checkpoints/         # Fine-tuned model checkpoints from training
├── data/                    # Dataset reference docs (DATASETS.md)
├── results/                 # Evaluation output (metrics.json, details.csv)
├── configs/                 # YAML configuration (generation, evaluation)
├── scripts/                 # Setup and evaluation scripts
├── .env.example             # Environment variable template
└── requirements.txt
```

## Quick Start

### 1. Install Dependencies

```bash
# Create and activate conda environment (recommended)
conda create -n ai python=3.11 -y
conda activate ai
pip install -r requirements.txt
export PYTHONPATH="$(pwd)"
```

```powershell
# Windows PowerShell
conda create -n ai python=3.11 -y
conda activate ai
pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
```

### 2. Configure Environment

Copy the template and set your model name:

```bash
cp .env.example .env
```

Edit `.env` — at minimum set `MODEL_NAME` and `BERTSCORE_MODEL_NAME`:

```bash
# Required
MODEL_NAME=Salesforce/codegen-350M-multi
BERTSCORE_MODEL_NAME=distilbert-base-uncased

# Optional: use a fine-tuned checkpoint instead of the base model
# MODEL_CHECKPOINT=my-run-epoch-3

# Local storage paths (defaults shown)
MODELS_BASE_DIR=models/base
MODELS_CHECKPOINTS_DIR=models/checkpoints
TEND_DATASET_ID=care2achieve/tend
TEND_CACHE_DIR=data/cache/tend
TEND_CACHE_DIR=data/cache/tend
RESULTS_DIR=results
```


| Variable                 | Description                                 | Default              |
| ------------------------ | ------------------------------------------- | -------------------- |
| `MODEL_NAME`             | HuggingFace model identifier (**required**) | —                    |
| `BERTSCORE_MODEL_NAME`   | BERTScore metric model (**required**)       | —                    |
| `MODEL_CHECKPOINT`       | Checkpoint name under `models/checkpoints/` | —                    |
| `MODELS_BASE_DIR`        | Where base models are cached                | `models/base`        |
| `MODELS_CHECKPOINTS_DIR` | Where training checkpoints are stored       | `models/checkpoints` |
| `TEND_DATASET_ID`        | Hugging Face TEND dataset id                | `care2achieve/tend`  |
| `TEND_CACHE_DIR`         | Local cache for TEND JSONL splits             | `~/.cache/codegen/tend` |
| `RESULTS_DIR`            | Evaluation output directory                 | `results`            |


YAML settings in `configs/default.yaml` cover generation parameters, evaluation limits, and seeds. Model name and storage paths always come from `.env`.

## Scripts

### `run_baseline_eval.py` — Baseline Model Evaluation

The primary evaluation script. Runs the configured model on the TEND Hugging Face dataset and computes all metrics.

**Metrics computed:** Exact Match, Execution Accuracy, Syntax Validity, BLEU, ROUGE-L, BERTScore, CodeBLEU

#### TEND benchmark (Hugging Face)

Loads [care2achieve/tend](https://huggingface.co/datasets/care2achieve/tend) via `src/datasets/tend_loader.py`. Gold SQL, MongoDB queries, and documentation come from the published silver dataset.

```bash
python scripts/test_tend_loader.py
python scripts/run_baseline_eval.py --tend-config spider --split test --max-samples 20
python scripts/run_baseline_eval.py --tend-config bird --split train --max-samples 50
```

#### Log results to MLflow

```bash
python scripts/run_baseline_eval.py --tend-config spider --mlflow
python scripts/run_baseline_eval.py --tend-config bird --max-samples 10 --mlflow
```

#### Save results to a named run folder

```bash
python scripts/run_baseline_eval.py --tend-config spider --output tend_spider_baseline
```

Creates `results/spider_baseline/` containing:

- `metrics.json` — aggregate metrics
- `details.csv` — per-sample prompts, outputs, and scores

#### All options


| Flag            | Default                 | Description                                        |
| --------------- | ----------------------- | -------------------------------------------------- |
| `--tend-config` | `spider`                | TEND subset: `spider` or `bird`                    |
| `--split`       | `test`                  | TEND split: `train` or `test` (`test` = source dev) |
| `--max-samples` | `5`                     | Number of examples to evaluate                     |
| `--mlflow`      | off                     | Log metrics to MLflow                              |
| `--output`      | `baseline_eval_results` | Run name; outputs go to `results/<name>/`          |


#### Example output

```
Baseline Evaluation: Salesforce/codegen-350M-multi
Dataset: tend | Max samples: 10

============================================================
  Text-to-SQL (tend_spider_test)
============================================================
  Exact Match Accuracy          : 0.1000
  Execution Accuracy            : 0.2000
  Syntax Validity Rate          : 0.9000
  BLEU                          : 0.3500
  ...
  Run saved: results/baseline_eval_results
    metrics: results/baseline_eval_results/metrics.json
    details: results/baseline_eval_results/details.csv
```

#### What happens on first run

1. **Model** — checks `models/base/<model-slug>/` for a cached copy; if missing, downloads from HuggingFace and saves locally
2. **Dataset** — loads TEND from Hugging Face on first use, then reuses cached JSONL under `TEND_CACHE_DIR` (default `~/.cache/codegen/tend`)
3. **Evaluation** — generates SQL/MongoDB/docs, compares against TEND gold fields, computes all metrics
4. **Results** — prints metrics to terminal and saves JSON/CSVs to `results/`

#### Using a fine-tuned checkpoint

After training, save your checkpoint under `models/checkpoints/<run-name>/` (must contain `config.json` and model weights). Then set in `.env`:

```bash
MODEL_CHECKPOINT=my-run-epoch-3
```

The loader uses the checkpoint instead of the base model.

---

## Local Caching

Assets are downloaded once and reused on every subsequent run.

### Models

```
models/base/Salesforce__codegen-350M-multi/
├── config.json
├── model.safetensors (or pytorch_model.bin)
├── tokenizer files
└── .downloaded          # cache marker

models/base/distilbert-base-uncased/   # BERTScore model (BERTSCORE_MODEL_NAME)
├── config.json
├── model.safetensors
└── .downloaded
```

- Checked before every load via `config.json` + `.downloaded`
- Downloaded from HuggingFace only when missing
- Configured by `MODEL_NAME` in `.env`
- BERTScore metric model cached the same way under `models/base/` via `BERTSCORE_MODEL_NAME`

### TEND dataset (Hugging Face)

- Loaded via `src/datasets/tend_loader.py` from `TEND_DATASET_ID` (default `care2achieve/tend`)
- Cached locally as standardized JSONL under `TEND_CACHE_DIR` (default `~/.cache/codegen/tend`, or e.g. `data/cache/tend` in `.env`)
- Configurations: `spider`, `bird`
- Splits: `train`, `test` (`test` = source validation/dev)
- Standardized format includes gold `sql`, `nosql_query`, and `documentation`

```
data/cache/tend/care2achieve__tend/spider/train.jsonl
data/cache/tend/care2achieve__tend/spider/test.jsonl
```

```python
from src.datasets.tend_loader import TENDLoader

loader = TENDLoader(config="spider")
examples = loader.load_split("test")
print(examples[0]["question"], examples[0]["nosql_query"])
```

### Checkpoints (training output)

```
models/checkpoints/
└── my-run-epoch-3/
    ├── config.json
    └── model weights
```

Set `MODEL_CHECKPOINT=my-run-epoch-3` in `.env` to load a checkpoint instead of the base model.

---

## Configuration

### Environment (`.env`) — models, datasets, and paths

All model names, dataset URLs, and storage paths are configured here. Never hardcoded in scripts.

```bash
MODEL_NAME=Salesforce/codegen-350M-multi
BERTSCORE_MODEL_NAME=distilbert-base-uncased
MODELS_BASE_DIR=models/base
MODELS_CHECKPOINTS_DIR=models/checkpoints
TEND_DATASET_ID=care2achieve/tend
TEND_CACHE_DIR=data/cache/tend
```

### YAML (`configs/default.yaml`) — runtime behavior

```yaml
model:
  max_length: 512
  device: "auto"       # auto, cuda, cpu

generation:
  max_new_tokens: 256
  temperature: 0.2
  decoding_strategy: "greedy"  # greedy, beam

evaluation:
  max_samples: 100
  experiment_name: "codegen-text2sql"

seeds:
  random: 42
  numpy: 42
  torch: 42
```

To use a different HuggingFace model, change `MODEL_NAME` in `.env` and delete the old cache folder under `models/base/` if needed.

---

## Datasets

See [data/DATASETS.md](data/DATASETS.md) for TEND field definitions, split naming, and loading examples.

---

## Evaluation Metrics


| Metric             | Description                      |
| ------------------ | -------------------------------- |
| Exact Match        | Normalized SQL string equality   |
| Execution Accuracy | Result set comparison on SQLite  |
| Syntax Validity    | Valid SQL structure rate         |
| BLEU               | N-gram overlap                   |
| ROUGE-L            | Longest common subsequence       |
| BERTScore          | Contextual embedding similarity  |
| CodeBLEU           | n-gram + syntax + semantic match |


---

## MLflow Tracking

```bash
# After running with --mlflow flag
mlflow ui --backend-store-uri sqlite:///mlflow.db

# Or for mlruns directory
mlflow ui --backend-store-uri mlruns
```

Tracked per run: model name, dataset, prompt template, decoding strategy, all metrics.

---

## Reproducibility

Seeds are set in `configs/default.yaml` for `random`, `numpy`, and `torch`. All evaluation scripts call `set_seeds(config)` before running.

```bash
python scripts/run_baseline_eval.py --tend-config spider --max-samples 10
```

---

## Troubleshooting


| Issue                             | Fix                                                                                  |
| --------------------------------- | ------------------------------------------------------------------------------------ |
| `MODEL_NAME is not set`           | Run `cp .env.example .env` and set `MODEL_NAME`                                      |
| `BERTSCORE_MODEL_NAME is not set` | Add `BERTSCORE_MODEL_NAME=distilbert-base-uncased` to `.env`                         |
| Model re-downloads every run      | Check `models/base/<slug>/.downloaded` exists; ensure write permissions              |
| Out of memory on GPU              | Set `device: "cpu"` in `configs/default.yaml` or use `--max-samples 5`               |
| Checkpoint not found              | Ensure `models/checkpoints/<name>/config.json` exists and `MODEL_CHECKPOINT` matches |
| `ModuleNotFoundError: src`        | Export `PYTHONPATH=$(pwd)` from project root                                         |


---

## License

Research and academic use. See individual dataset and model licenses for Spider, BIRD, and CodeGen.