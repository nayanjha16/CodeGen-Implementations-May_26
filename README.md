# CodeGen – Interactive Database Querying Using Small Code Language Models

A modular, reproducible, research-oriented project for evaluating small code language models on database query generation and translation tasks.

**Default model:** [Salesforce/codegen-350M-multi](https://huggingface.co/Salesforce/codegen-350M-multi) (configurable via `.env`)

## Features

- **Natural Language → SQL** generation with greedy and beam search decoding
- **SQL → MongoDB** rule-based translation (SELECT, WHERE, ORDER BY, LIMIT, GROUP BY)
- **Benchmark evaluation** on Spider and BIRD datasets
- **Metrics**: Exact Match, Execution Accuracy, Syntax Validity, BLEU, ROUGE-L, BERTScore, CodeBLEU (text-to-SQL); translation success, structural equivalence, token F1 (SQL-to-NoSQL)
- **MLflow** experiment tracking
- **Local caching** — models and datasets download once, then reuse from disk
- **Fine-tuning** script for seq2seq models on Spider
- **TEND** pipeline for SQL-to-NoSQL dataset generation and evaluation

## Project Structure

```
CodeGen-Implementations-May_26/
├── src/                          # Application source code
│   ├── text2sql/                 # Prompt builder, generator, validator, executor
│   ├── sql2nosql/                # SQL-to-MongoDB translator and evaluator
│   ├── models/                   # HuggingFace model loader (with local cache)
│   ├── datasets/                 # Spider & BIRD loaders, preprocessing
│   ├── evaluation/               # Metrics, benchmarks, MLflow tracking, export
│   └── utils/                    # Config, paths, logging, device, seeds
├── models/
│   ├── base_model/               # Downloaded HuggingFace models (cached once)
│   └── trained_model/            # Fine-tuned checkpoints from training
├── data/
│   ├── spider/                   # Spider dataset (downloaded once)
│   ├── bird/                     # BIRD dataset (downloaded once)
│   ├── samples/                  # Sample SQLite databases
│   └── TEND/                     # TEND pipeline CSV/JSON outputs
├── results/                      # Evaluation run folders (metrics + detail CSVs)
├── configs/
│   └── default.yaml              # Generation, evaluation, and seed settings
├── scripts/
│   ├── run_baseline_eval.py      # Primary baseline evaluation script
│   ├── finetune_text2sql.py      # Fine-tune seq2seq models on Spider
│   ├── setup_sample_db.py        # Create sample SQLite database
│   └── setup_env.ps1             # Windows venv setup helper
├── TEND/                         # SQL-to-NoSQL dataset generation (see TEND/README.md)
├── ai-workflow/                  # Research, planning, and workflow documentation
├── .env                          # Environment variables (create locally; not committed)
├── environment.yml               # Conda environment definition
└── requirements.txt
```

## Quick Start

### 1. Install Dependencies

**Option A — Conda (recommended)**

```bash
conda env create -f environment.yml
conda activate ai
pip install -r requirements.txt
export PYTHONPATH="$(pwd)"
```

```powershell
# Windows PowerShell
conda env create -f environment.yml
conda activate ai
pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
```

**Option B — Python venv**

```bash
python3.11 -m venv myvenv
source myvenv/bin/activate
pip install -r requirements.txt
export PYTHONPATH="$(pwd)"
```

```powershell
# Windows PowerShell
py -3.11 -m venv myvenv
.\myvenv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
```

Or run the Windows helper:

```powershell
.\scripts\setup_env.ps1
$env:PYTHONPATH = (Get-Location).Path
```

### 2. Configure Environment

Create a `.env` file in the project root and set at minimum `MODEL_NAME` and `BERTSCORE_MODEL_NAME`:

```bash
# Required
MODEL_NAME=Salesforce/codegen-350M-multi
BERTSCORE_MODEL_NAME=distilbert-base-uncased

# Optional: use a fine-tuned checkpoint instead of the base model
# MODEL_CHECKPOINT=my-run-epoch-3

# Local storage paths (defaults shown)
MODELS_BASE_DIR=models/base_model
MODELS_CHECKPOINTS_DIR=models/trained_model
DATA_DIR=data
SPIDER_DATA_DIR=data/spider
BIRD_DATA_DIR=data/bird
RESULTS_DIR=results

# Dataset download URLs
SPIDER_REPO_URL=https://github.com/taoyds/spider/archive/refs/heads/master.zip
SPIDER_DATASET_URL=https://drive.google.com/uc?export=download&id=1TqleXec_OykOYFREKKtschzY29dUcVAQ
BIRD_DATASET_URL=https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip
```

| Variable                 | Description                                 | Default                 |
| ------------------------ | ------------------------------------------- | ----------------------- |
| `MODEL_NAME`             | HuggingFace model identifier (**required**) | —                       |
| `BERTSCORE_MODEL_NAME`   | BERTScore metric model (**required**)       | —                       |
| `MODEL_CHECKPOINT`       | Checkpoint name under `models/trained_model/` | —                     |
| `MODELS_BASE_DIR`        | Where base models are cached                | `models/base_model`     |
| `MODELS_CHECKPOINTS_DIR` | Where training checkpoints are stored       | `models/trained_model`  |
| `DATA_DIR`               | Root data directory                         | `data`                  |
| `SPIDER_DATA_DIR`        | Spider dataset location                     | `data/spider`           |
| `BIRD_DATA_DIR`          | BIRD dataset location                       | `data/bird`             |
| `RESULTS_DIR`            | Evaluation output root directory            | `results`               |
| `SPIDER_REPO_URL`        | Spider GitHub archive URL                   | —                       |
| `SPIDER_DATASET_URL`     | Spider full dataset mirror URL              | —                       |
| `BIRD_DATASET_URL`       | BIRD dataset archive URL                    | —                       |

YAML settings in `configs/default.yaml` cover generation parameters, evaluation limits, and seeds. Model name and storage paths always come from `.env`.

**Supported model families**

| Family | Example `MODEL_NAME` | Loader type |
| ------ | -------------------- | ----------- |
| CodeGen (causal LM) | `Salesforce/codegen-350M-multi` | `AutoModelForCausalLM` |
| T5 / seq2seq | `google-t5/t5-base` | `AutoModelForSeq2SeqLM` |
| CodeT5 (seq2seq) | `Salesforce/codet5-base` | `AutoModelForSeq2SeqLM` |

Seq2seq models automatically use beam search (`seq2seq_decoding_strategy` in `configs/default.yaml`).

### 3. Create Sample Database

```bash
python scripts/setup_sample_db.py
```

Creates `data/samples/students.db` with students, courses, and enrollments tables.

---

## Scripts

### `run_baseline_eval.py` — Baseline Model Evaluation

The primary evaluation script. Runs the configured model on built-in examples or full benchmark datasets and computes text-to-SQL and SQL-to-NoSQL metrics.

**Text-to-SQL metrics:** Exact Match, Execution Accuracy, Syntax Validity, BLEU, ROUGE-L, BERTScore, CodeBLEU

**SQL-to-NoSQL metrics:** Translation Success Rate, Structural Equivalence, Token F1, Syntax Validity

#### Quick baseline (no downloads, fastest)

Uses 3 built-in reference examples and the sample SQLite database. Good for verifying your setup.

```bash
python scripts/run_baseline_eval.py
```

#### Spider benchmark

Downloads Spider dataset to `data/spider/` and model to `models/base_model/` on first run. Subsequent runs use the local cache.

```bash
python scripts/run_baseline_eval.py --dataset spider
python scripts/run_baseline_eval.py --dataset spider --split validation --max-samples 20
```

#### BIRD benchmark

```bash
python scripts/run_baseline_eval.py --dataset bird
python scripts/run_baseline_eval.py --dataset bird --split validation --max-samples 50
```

#### Log results to MLflow

```bash
python scripts/run_baseline_eval.py --dataset spider --mlflow
python scripts/run_baseline_eval.py --dataset bird --max-samples 10 --mlflow
```

#### Save results to a named run folder

```bash
python scripts/run_baseline_eval.py --dataset spider --output spider_baseline
python scripts/run_baseline_eval.py --dataset spider --output spider_baseline.json
```

Both commands create `results/spider_baseline/` containing:

- `metrics.json` — aggregate text-to-SQL and SQL-to-NoSQL metrics
- `text2sql_details.csv` — per-sample prompts, SQL outputs, and scores
- `sql2nosql_details.csv` — per-sample MongoDB translation details

#### All options

| Flag            | Default                 | Description                                        |
| --------------- | ----------------------- | -------------------------------------------------- |
| `--dataset`     | `quick`                 | `quick` (built-in examples), `spider`, or `bird`   |
| `--split`       | `validation`            | Dataset split: `train`, `validation`/`dev`, `test` |
| `--max-samples` | `5`                     | Number of examples to evaluate                     |
| `--mlflow`      | off                     | Log metrics to MLflow                              |
| `--output`      | `baseline_eval_results` | Run name; outputs go to `results/<name>/`          |

#### Example output

```
Baseline Evaluation: Salesforce/codegen-350M-multi
Dataset: spider | Max samples: 10

============================================================
  Text-to-SQL Results (spider_validation)
============================================================
  Exact Match Accuracy          : 0.1000
  Execution Accuracy            : 0.2000
  Syntax Validity Rate          : 0.9000
  ...

============================================================
  SQL-to-MongoDB Results (spider_validation)
============================================================
  Translation Success Rate      : 0.8000
  Structural Equivalence        : 0.6000
  ...

  Run saved: results/spider_baseline
    metrics: results/spider_baseline/metrics.json
    text2sql: results/spider_baseline/text2sql_details.csv
    sql2nosql: results/spider_baseline/sql2nosql_details.csv
```

#### What happens on first run

1. **Model** — checks `models/base_model/<model-slug>/` for a cached copy; if missing, downloads from HuggingFace and saves locally
2. **Dataset** — checks `data/spider/` or `data/bird/` for a `.downloaded` marker; if missing, downloads and extracts the archive
3. **Evaluation** — generates SQL, translates to MongoDB, compares against gold queries, computes all metrics
4. **Results** — prints metrics to terminal and saves JSON/CSVs under `results/<run-name>/`

#### Using a fine-tuned checkpoint

After training, save your checkpoint under `models/trained_model/<run-name>/` (must contain `config.json` and model weights). Then set in `.env`:

```bash
MODEL_CHECKPOINT=my-run-epoch-3
```

The loader uses the checkpoint instead of the base model.

---

### `finetune_text2sql.py` — Fine-tune on Spider

Fine-tunes encoder-decoder models (e.g. `google-t5/t5-base`) on Spider training data. Raw T5 models do not generate SQL out of the box without fine-tuning.

```bash
python scripts/finetune_text2sql.py --epochs 3 --output spider-t5-base
```

Then evaluate the checkpoint:

```bash
# In .env: MODEL_CHECKPOINT=spider-t5-base
python scripts/run_baseline_eval.py --dataset spider --output spider-t5-finetuned
```

---

### `setup_sample_db.py` — Sample SQLite Database

Creates `data/samples/students.db` for quick baseline runs and local execution-accuracy checks.

---

### `setup_env.ps1` — Windows Environment Setup

Creates `.venv`, installs `requirements.txt`, and prints next-step commands.

---

## TEND — SQL-to-NoSQL Dataset Pipeline

The `TEND/` package builds TEND-style training and evaluation datasets from Spider (BIRD planned). It produces SQL/MongoDB schema-query pairs, validation flags, and optional Qwen-based semantic evaluation.

See [TEND/README.md](TEND/README.md) for full usage.

```bash
python TEND/run_tend.py --split validation --max-samples 50
```

Outputs are written under `data/TEND/`.

---

## Local Caching

Assets are downloaded once and reused on every subsequent run.

### Models

```
models/base_model/Salesforce__codegen-350M-multi/
├── config.json
├── model.safetensors (or pytorch_model.bin)
├── tokenizer files
└── .downloaded          # cache marker

models/base_model/distilbert-base-uncased/   # BERTScore model (BERTSCORE_MODEL_NAME)
├── config.json
├── model.safetensors
└── .downloaded
```

- Checked before every load via `config.json` + `.downloaded`
- Downloaded from HuggingFace only when missing
- Configured by `MODEL_NAME` in `.env`
- BERTScore metric model cached the same way via `BERTSCORE_MODEL_NAME`

### Datasets

```
data/spider/
├── dev.json
├── train_spider.json
├── tables.json
├── database/
├── spider_data/         # full dataset mirror (if needed)
└── .downloaded          # cache marker

data/bird/
├── bird_data/
│   ├── dev.json
│   ├── dev_tables.json
│   └── dev_databases/
└── .downloaded          # cache marker
```

- Checked before every load via `.downloaded` marker and data file presence
- Downloaded only when missing
- Storage paths: `SPIDER_DATA_DIR`, `BIRD_DATA_DIR` in `.env`
- Download URLs: `SPIDER_REPO_URL`, `SPIDER_DATASET_URL`, `BIRD_DATASET_URL` in `.env`

### Checkpoints (training output)

```
models/trained_model/
└── spider-t5-base/
    ├── config.json
    └── model weights
```

Set `MODEL_CHECKPOINT=spider-t5-base` in `.env` to load a checkpoint instead of the base model.

---

## Configuration

### Environment (`.env`) — models, datasets, and paths

All model names, dataset URLs, and storage paths are configured here. Never hardcoded in scripts.

```bash
MODEL_NAME=Salesforce/codegen-350M-multi
BERTSCORE_MODEL_NAME=distilbert-base-uncased
MODELS_BASE_DIR=models/base_model
MODELS_CHECKPOINTS_DIR=models/trained_model
RESULTS_DIR=results
SPIDER_DATA_DIR=data/spider
BIRD_DATA_DIR=data/bird
SPIDER_REPO_URL=https://github.com/taoyds/spider/archive/refs/heads/master.zip
SPIDER_DATASET_URL=https://drive.google.com/uc?export=download&id=1TqleXec_OykOYFREKKtschzY29dUcVAQ
BIRD_DATASET_URL=https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip
```

### YAML (`configs/default.yaml`) — runtime behavior

```yaml
model:
  max_length: 512
  device: "auto"       # auto, cuda, mps, cpu

generation:
  max_new_tokens: 256
  temperature: 0.7
  decoding_strategy: "greedy"  # greedy, beam
  seq2seq_decoding_strategy: "beam"  # auto-used for T5/BART models

text2sql:
  prompt_template: "auto"  # auto, default, seq2seq

evaluation:
  max_samples: 100
  experiment_name: "codegen-text2sql"

seeds:
  random: 42
  numpy: 42
  torch: 42
```

To use a different HuggingFace model, change `MODEL_NAME` in `.env` and delete the old cache folder under `models/base_model/` if needed.

---

## Datasets

### Spider

- Auto-downloads to `data/spider/` on first use
- Standardized format: `{question, schema, sql, db_id}`
- Splits: `train`, `validation` (dev), `test`

### BIRD

- Auto-downloads to `data/bird/` on first use
- Includes evidence and difficulty metadata
- Splits: `train`, `validation` (dev), `test`

```python
from src.datasets.spider_loader import SpiderLoader

loader = SpiderLoader()
examples = loader.load_split("validation")
print(examples[0])
```

---

## Evaluation Metrics

### Text-to-SQL

| Metric             | Description                      |
| ------------------ | -------------------------------- |
| Exact Match        | Normalized SQL string equality   |
| Execution Accuracy | Result set comparison on SQLite  |
| Syntax Validity    | Valid SQL structure rate         |
| BLEU               | N-gram overlap                   |
| ROUGE-L            | Longest common subsequence       |
| BERTScore          | Contextual embedding similarity  |
| CodeBLEU           | n-gram + syntax + semantic match |

### SQL-to-NoSQL

| Metric                    | Description                                      |
| ------------------------- | ------------------------------------------------ |
| Translation Success Rate  | Fraction of SQL queries translated to MongoDB    |
| Structural Equivalence    | Filter/projection/collection structural match    |
| Token F1                  | Token overlap on MongoDB query strings           |
| Syntax Validity           | Valid MongoDB shell syntax rate                  |

---

## MLflow Tracking

```bash
# After running with --mlflow flag
mlflow ui --backend-store-uri sqlite:///mlflow.db

# Or for mlruns directory
mlflow ui --backend-store-uri mlruns
```

Tracked per run: model name, dataset, prompt template, decoding strategy, text-to-SQL and SQL-to-NoSQL metrics.

---

## Reproducibility

Seeds are set in `configs/default.yaml` for `random`, `numpy`, and `torch`. All evaluation scripts call `set_seeds(config)` before running.

```bash
python scripts/run_baseline_eval.py --dataset spider --max-samples 10
```

---

## Troubleshooting

| Issue                             | Fix                                                                                      |
| --------------------------------- | ---------------------------------------------------------------------------------------- |
| `MODEL_NAME is not set`           | Create `.env` in project root and set `MODEL_NAME` (no leading spaces on the line)       |
| `BERTSCORE_MODEL_NAME is not set` | Add `BERTSCORE_MODEL_NAME=distilbert-base-uncased` to `.env`                             |
| Model re-downloads every run      | Check `models/base_model/<slug>/.downloaded` exists; ensure write permissions            |
| Dataset re-downloads every run    | Check `data/spider/.downloaded` or `data/bird/.downloaded` exists                        |
| Out of memory on GPU              | Set `device: "cpu"` in `configs/default.yaml` or use `--max-samples 5`                 |
| Checkpoint not found              | Ensure `models/trained_model/<name>/config.json` exists and `MODEL_CHECKPOINT` matches   |
| `ModuleNotFoundError: src`        | Set `PYTHONPATH` to project root from the project root directory                         |
| Invalid HuggingFace model ID      | Use a valid ID (e.g. `google-t5/t5-base`, not `Salesforce/codegen-t5-base`)              |
| CodeT5 tokenizer error            | Use `google-t5/t5-base`, or install `transformers>=4.36.0,<5.0.0` for `Salesforce/codet5-base` |
| PowerShell activation blocked     | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then activate the venv        |

---

## License

Research and academic use. See individual dataset and model licenses for Spider, BIRD, and CodeGen.
