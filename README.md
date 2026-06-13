# CodeGen – Interactive Database Querying Using Small Code Language Models

A modular, reproducible, research-oriented project for evaluating small code language models on database query generation and translation tasks.

**Default model:** [Salesforce/codegen-350M-multi](https://huggingface.co/Salesforce/codegen-350M-multi) (configurable via `.env`)

## Features

- **Natural Language → SQL** generation with greedy and beam search decoding
- **SQL → MongoDB** rule-based translation (SELECT, WHERE, ORDER BY, LIMIT, GROUP BY)
- **Interactive query pipeline** with validation, execution, and explanations
- **Benchmark evaluation** on Spider and BirdBench datasets
- **Metrics**: Exact Match, Execution Accuracy, BLEU, ROUGE-L, BERTScore, CodeBLEU
- **MLflow** experiment tracking
- **FastAPI** REST API with Swagger docs
- **Streamlit** interactive UI
- **Local caching** — models and datasets download once, then reuse from disk

## Project Structure

```
CodeGen-Studio/
├── src/                     # Application source code
│   ├── text2sql/            # Prompt builder, generator, validator, executor
│   ├── sql2nosql/           # SQL to MongoDB translator
│   ├── query_engine/        # End-to-end interactive pipeline
│   ├── api/                 # FastAPI backend
│   ├── models/              # HuggingFace model loader (with local cache)
│   ├── datasets/            # Spider & BIRD loaders, preprocessing
│   ├── evaluation/          # Metrics, benchmarks, MLflow tracking
│   └── utils/               # Config, paths, logging, seeds
├── models/
│   ├── base/                # Downloaded HuggingFace models (cached once)
│   └── checkpoints/         # Fine-tuned model checkpoints from training
├── data/
│   ├── spider/              # Spider dataset (downloaded once)
│   ├── bird/                # BIRD dataset (downloaded once)
│   ├── processed/           # Preprocessed dataset exports
│   └── samples/             # Sample SQLite databases
├── results/                 # Evaluation output JSON
├── apps/
│   └── streamlit/           # Streamlit UI
├── configs/                 # YAML configuration (generation, evaluation, API)
├── scripts/                 # Setup, evaluation, and launcher scripts
├── tests/                   # pytest test suite
├── .env.example             # Environment variable template
├── requirements.txt
└── docker-compose.yml
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
DATA_DIR=data
SPIDER_DATA_DIR=data/spider
BIRD_DATA_DIR=data/bird
SPIDER_REPO_URL=https://github.com/taoyds/spider/archive/refs/heads/master.zip
SPIDER_DATASET_URL=https://drive.google.com/uc?export=download&id=1TqleXec_OykOYFREKKtschzY29dUcVAQ
BIRD_DATASET_URL=https://github.com/AlibabaResearch/DAMO-ConvAI/archive/refs/heads/master.zip
```

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_NAME` | HuggingFace model identifier (**required**) | — |
| `BERTSCORE_MODEL_NAME` | BERTScore metric model (**required**) | — |
| `MODEL_CHECKPOINT` | Checkpoint name under `models/checkpoints/` | — |
| `MODELS_BASE_DIR` | Where base models are cached | `models/base` |
| `MODELS_CHECKPOINTS_DIR` | Where training checkpoints are stored | `models/checkpoints` |
| `DATA_DIR` | Root data directory | `data` |
| `SPIDER_DATA_DIR` | Spider dataset location | `data/spider` |
| `BIRD_DATA_DIR` | BIRD dataset location | `data/bird` |
| `SPIDER_REPO_URL` | Spider GitHub archive URL | — |
| `SPIDER_DATASET_URL` | Spider full dataset mirror URL | — |
| `BIRD_DATASET_URL` | BIRD dataset archive URL | — |

YAML settings in `configs/default.yaml` cover generation parameters, evaluation limits, API ports, and seeds. Model name and storage paths always come from `.env`.

### 3. Create Sample Database

```bash
python scripts/setup_sample_db.py
```

Creates `data/samples/students.db` with students, courses, and enrollments tables.

### 4. Run Tests

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Scripts

### `run_baseline_eval.py` — Baseline Model Evaluation

The primary evaluation script. Runs the configured model on built-in examples or full benchmark datasets and computes all metrics.

**Metrics computed:** Exact Match, Execution Accuracy, Syntax Validity, BLEU, ROUGE-L, BERTScore, CodeBLEU

#### Quick baseline (no downloads, fastest)

Uses 3 built-in reference examples and the sample SQLite database. Good for verifying your setup.

```bash
python scripts/run_baseline_eval.py
```

#### Spider benchmark

Downloads Spider dataset to `data/spider/` and model to `models/base/` on first run. Subsequent runs use the local cache.

```bash
python scripts/run_baseline_eval.py --dataset spider
python scripts/run_baseline_eval.py --dataset spider --split validation --max-samples 20
```

#### BirdBench benchmark

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
```

Creates `results/spider_baseline/` containing:
- `metrics.json` — aggregate metrics
- `details.csv` — per-sample prompts, outputs, and scores

#### All options

| Flag | Default | Description |
|------|---------|-------------|
| `--dataset` | `quick` | `quick` (built-in examples), `spider`, or `bird` |
| `--split` | `validation` | Dataset split: `train`, `validation`/`dev`, `test` |
| `--max-samples` | `5` | Number of examples to evaluate |
| `--mlflow` | off | Log metrics to MLflow |
| `--output` | `baseline_eval_results` | Run name; outputs go to `results/<name>/` |

#### Example output

```
Baseline Evaluation: Salesforce/codegen-350M-multi
Dataset: spider | Max samples: 10
Note: First run downloads model and dataset to local models/ and data/ folders.

============================================================
  Baseline Results (spider_validation)
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

1. **Model** — checks `models/base/<model-slug>/` for a cached copy; if missing, downloads from HuggingFace (~700 MB for codegen-350M) and saves locally
2. **Dataset** — checks `data/spider/` or `data/bird/` for a `.downloaded` marker; if missing, downloads and extracts the archive
3. **Evaluation** — generates SQL, compares against gold queries, computes all metrics
4. **Results** — prints metrics to terminal and saves JSON to `results/`

#### Using a fine-tuned checkpoint

After training, save your checkpoint under `models/checkpoints/<run-name>/` (must contain `config.json` and model weights). Then set in `.env`:

```bash
MODEL_CHECKPOINT=my-run-epoch-3
```

The loader uses the checkpoint instead of the base model.

---

### Other Scripts

| Script | Purpose |
|--------|---------|
| `scripts/setup_sample_db.py` | Create sample SQLite database |
| `scripts/demo_presentation.py` | IIT Hyderabad-style live demo (metrics, SQL→NoSQL) |
| `scripts/evaluate.sh` | Shell wrapper for Spider/Bird benchmark via `BenchmarkRunner` |
| `scripts/train.sh` | Training placeholder (sets seeds, prints config) |
| `scripts/run_api.sh` | Start FastAPI server on port 8000 |
| `scripts/run_streamlit.sh` | Start Streamlit UI on port 8501 |

#### Demo presentation

```bash
# Metrics + SQL→NoSQL only (no model download)
python scripts/demo_presentation.py

# Include live text-to-SQL generation (uses cached model)
python scripts/demo_presentation.py --with-model

# Evaluation section only
python scripts/demo_presentation.py --eval-only --mlflow
```

#### Shell evaluation wrapper

```bash
bash scripts/evaluate.sh spider validation
bash scripts/evaluate.sh bird validation
MAX_SAMPLES=20 bash scripts/evaluate.sh spider validation
```

#### Start API server

```bash
# Linux/macOS
bash scripts/run_api.sh

# Windows
set PYTHONPATH=%CD% && uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs: http://localhost:8000/docs

#### Start Streamlit UI

```bash
bash scripts/run_streamlit.sh
# or: streamlit run apps/streamlit/app.py
```

UI: http://localhost:8501

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
├── DAMO-ConvAI-master/bird/finetuning/
│   ├── train.json
│   └── dev.json
└── .downloaded
```

- Checked before every load via `.downloaded` marker and data file presence
- Downloaded only when missing
- Storage paths: `SPIDER_DATA_DIR`, `BIRD_DATA_DIR` in `.env`
- Download URLs: `SPIDER_REPO_URL`, `SPIDER_DATASET_URL`, `BIRD_DATASET_URL` in `.env`

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
SPIDER_DATA_DIR=data/spider
BIRD_DATA_DIR=data/bird
SPIDER_REPO_URL=https://github.com/taoyds/spider/archive/refs/heads/master.zip
SPIDER_DATASET_URL=https://drive.google.com/uc?export=download&id=1TqleXec_OykOYFREKKtschzY29dUcVAQ
BIRD_DATASET_URL=https://github.com/AlibabaResearch/DAMO-ConvAI/archive/refs/heads/master.zip
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

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/generate-sql` | NL → SQL generation |
| POST | `/translate-nosql` | SQL → MongoDB translation |
| POST | `/execute-query` | Execute SQL on SQLite DB |
| POST | `/evaluate` | Compute evaluation metrics |
| POST | `/interactive-query` | Full query pipeline |

### Example: Generate SQL

```bash
curl -X POST http://localhost:8000/generate-sql \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show all students older than 20",
    "schema": "Table students(id, name, age)"
  }'
```

### Example: Translate to MongoDB

```bash
curl -X POST http://localhost:8000/translate-nosql \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT name FROM users WHERE age > 20"}'
```

---

## Datasets

### Spider

- Auto-downloads to `data/spider/` on first use
- Standardized format: `{question, schema, sql, db_id}`
- Splits: `train`, `validation` (dev), `test`

### BirdBench

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

| Metric | Description |
|--------|-------------|
| Exact Match | Normalized SQL string equality |
| Execution Accuracy | Result set comparison on SQLite |
| Syntax Validity | Valid SQL structure rate |
| BLEU | N-gram overlap |
| ROUGE-L | Longest common subsequence |
| BERTScore | Contextual embedding similarity |
| CodeBLEU | n-gram + syntax + semantic match |

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

## Docker

```bash
docker compose up --build
# or: docker compose -f docker/docker-compose.yml up --build
```

Services:
- **API**: http://localhost:8000
- **Streamlit**: http://localhost:8501
- **MLflow**: http://localhost:5000

Mount `.env` and `models/`, `data/` volumes to persist cached assets across container restarts.

---

## Reproducibility

Seeds are set in `configs/default.yaml` for `random`, `numpy`, and `torch`. All evaluation scripts call `set_seeds(config)` before running.

```bash
# Verify seeds and config
bash scripts/train.sh

# Full baseline evaluation with reproducible seeds
python scripts/run_baseline_eval.py --dataset spider --max-samples 10
```

---

## Testing

```bash
pytest tests/ -v
pytest tests/ --cov=src
```

Test coverage includes: config/env loading, model caching logic, dataset loading, SQL generation, validation, execution, NoSQL translation, and benchmark runner.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `MODEL_NAME is not set` | Run `cp .env.example .env` and set `MODEL_NAME` |
| `BERTSCORE_MODEL_NAME is not set` | Add `BERTSCORE_MODEL_NAME=distilbert-base-uncased` to `.env` |
| Model re-downloads every run | Check `models/base/<slug>/.downloaded` exists; ensure write permissions |
| Dataset re-downloads every run | Check `data/spider/.downloaded` or `data/bird/.downloaded` exists |
| Out of memory on GPU | Set `device: "cpu"` in `configs/default.yaml` or use `--max-samples 5` |
| Checkpoint not found | Ensure `models/checkpoints/<name>/config.json` exists and `MODEL_CHECKPOINT` matches |
| `ModuleNotFoundError: src` | Export `PYTHONPATH=$(pwd)` from project root |

---

## License

Research and academic use. See individual dataset and model licenses for Spider, BIRD, and CodeGen.
