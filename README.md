# CodeGen – Interactive Database Querying Using Small Code Language Models

A modular, reproducible, research-oriented project for evaluating and fine-tuning small code language models on database query generation and translation tasks.

**Default base model:** [Salesforce/codegen-350M-multi](https://huggingface.co/Salesforce/codegen-350M-multi) (configurable via `.env`)

## Features

- **Natural Language → SQL** generation with greedy and beam search decoding
- **SQL → MongoDB** model-based conversion with gold references from TEND
- **NoSQL → Documentation** generation (nosql2doc)
- **LoRA fine-tuning** — one task-specific adapter per pipeline stage (text2sql, sql2nosql, nosql2doc)
- **Benchmark evaluation** on the [TEND silver dataset](https://huggingface.co/datasets/care2achieve/tend) (Spider + BIRD configs)
- **Metrics**: Exact Match, Execution Accuracy, BLEU, ROUGE-L, BERTScore, CodeBLEU, Ollama semantic judge
- **MLflow** experiment tracking
- **Local caching** — models and datasets download once, then reuse from disk

## Project Structure

```
CodeGen-Implementations-May_26/
├── src/
│   ├── text2sql/            # Prompt builder, generator, validator, executor
│   ├── sql2nosql/           # SQL to MongoDB generation + evaluation
│   ├── documentation/       # nosql2doc prompt builder
│   ├── models/              # HuggingFace model loader (base + LoRA adapters)
│   ├── datasets/            # TEND Hugging Face loader, preprocessing
│   ├── training/            # LoRA trainer, SFT dataset builder, collator
│   ├── evaluation/          # Metrics, benchmarks, MLflow, Ollama judge
│   └── utils/               # Config, paths, logging, seeds
├── models/
│   ├── base/                # Downloaded HuggingFace base models (cached once)
│   └── checkpoints/         # LoRA adapter weights (one dir per run, then task)
├── data/
│   ├── spider_gold_validation.jsonl   # Frozen 50-example eval set
│   └── DATASETS.md
├── results/                 # Evaluation output (metrics.json, details.csv)
├── tests/training/          # Unit + smoke tests for LoRA pipeline
├── configs/default.yaml     # Generation, evaluation, training, LoRA settings
├── scripts/                 # Setup, training, evaluation, verification
├── .env.example
└── requirements.txt
```

## Quick Start

### 1. Install Dependencies

```bash
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

#### Windows with Intel/AMD GPU (DirectML)

For systems with an Intel or AMD integrated/discrete GPU on Windows (DirectX 12), install
`torch-directml` **instead of** the standard `torch` package, then install the rest of the
dependencies from the Windows-specific requirements file:

```powershell
conda create -n ai python=3.11 -y
conda activate ai
pip install torch-directml
pip install -r requirements-windows-directml.txt
$env:PYTHONPATH = (Get-Location).Path
```

With `device: auto` in config, DirectML is selected when CUDA and MPS are unavailable.
You can also force it explicitly:

```powershell
python scripts/run_baseline_eval.py --device dml
python scripts/train_lora.py --version v1 --task text2sql --device dml --max-samples 50 --epochs 1
```

DirectML works best for **inference and evaluation**. LoRA training via TRL `SFTTrainer` may
fail on some DirectML builds; use `--device cpu` for training smoke tests, or train on
CUDA/MPS and evaluate on Windows with `--device dml`.

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` — at minimum set `MODEL_NAME` and `BERTSCORE_MODEL_NAME`:

```bash
# Required
MODEL_NAME=Salesforce/codegen-350M-multi
BERTSCORE_MODEL_NAME=distilbert-base-uncased

# Optional: load a LoRA adapter at inference time
# MODEL_ADAPTER=text2sql
# MODEL_ADAPTER_RUN=v1

# Local storage paths (defaults shown)
MODELS_BASE_DIR=models/base
MODELS_CHECKPOINTS_DIR=models/checkpoints
TEND_DATASET_ID=care2achieve/tend
TEND_CACHE_DIR=data/cache/tend
RESULTS_DIR=results

# Ollama semantic judge (used in baseline eval detail CSVs)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_JUDGE_MODEL=qwen3:4b
OLLAMA_TIMEOUT=120
```

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `MODEL_NAME` | HuggingFace base model identifier (**required**) | — |
| `BERTSCORE_MODEL_NAME` | BERTScore metric model (**required**) | — |
| `MODEL_ADAPTER` | Task name whose LoRA adapter to load (`text2sql`, `sql2nosql`, `nosql2doc`) | — |
| `MODEL_ADAPTER_RUN` | Checkpoint run folder under `models/checkpoints/` (e.g. `v1`) | — |
| `MODELS_BASE_DIR` | Where base models are cached | `models/base` |
| `MODELS_CHECKPOINTS_DIR` | Where LoRA adapters are stored | `models/checkpoints` |
| `TEND_DATASET_ID` | Hugging Face TEND dataset id | `care2achieve/tend` |
| `TEND_CACHE_DIR` | Local cache for TEND JSONL splits | `data/cache/tend` |
| `SPIDER_GOLD_VALIDATION_PATH` | Frozen Spider gold validation JSONL | `data/spider_gold_validation.jsonl` |
| `RESULTS_DIR` | Evaluation output directory | `results` |
| `OLLAMA_BASE_URL` | Ollama API URL for semantic judge | `http://localhost:11434` |
| `OLLAMA_JUDGE_MODEL` | Ollama model for semantic correctness | `qwen3:4b` |

YAML settings in `configs/default.yaml` cover generation, evaluation limits, training hyperparameters, and LoRA config. Model name and storage paths always come from `.env`.

---

## Recommended Workflow

Run these steps in order for a full baseline → train → evaluate cycle:

```bash
# 0. Pre-flight: verify LoRA target modules on the base model
python scripts/inspect_lora_modules.py

# 1. Smoke-test TEND dataset loading
python scripts/test_tend_loader.py

# 2. Run unit + smoke tests (fast, ~1–2 min)
python -m unittest discover -s tests/training -v

# 3. Baseline evaluation (base model, no adapter)
python scripts/run_baseline_eval.py --max-samples 50

# 4. Smoke-check SFT dataset builder
python scripts/build_sft_dataset.py

# 5. Train one task (smoke run)
python scripts/train_lora.py --version v1 --task text2sql --max-samples 50 --epochs 1 --no-mlflow

# 6. Full training (all three tasks)
python scripts/train_all_lora.py --version v1 --no-mlflow

# 7. Verify adapter artifacts
python scripts/verify_lora_adapters.py --version v1

# 8. Evaluate with LoRA adapters (one adapter per task)
python scripts/run_baseline_eval.py --adapter-run v1 --max-samples 50
```

---

## Testing

### Unit and smoke tests

All training tests live under `tests/training/`:

| Test file | What it checks |
| --------- | -------------- |
| `test_prompt_parity.py` | Training prompts match runtime `PromptBuilder`s; dataset filters; token budget ≤ 2048 |
| `test_overfit_smoke.py` | LoRA trainer overfits 5 rows, writes `adapter_config.json` + weights |
| `test_adapter_load.py` | Trains tiny adapters per task; `load_model(adapter_path=...)` generates non-empty output |
| `test_adapter_verify.py` | Adapter verification helper reports missing files correctly |

```bash
# Run all training tests
python -m unittest discover -s tests/training -v

# Run a subset (fast sanity check)
python -m unittest tests.training.test_prompt_parity tests.training.test_overfit_smoke -v

# Single test
python -m unittest tests.training.test_overfit_smoke.OverfitSmokeTest -v
```

The overfit smoke test trains 5 Spider rows for 10 epochs and expects `train_loss < 1.5`. Adapter load tests train 3 rows per task and verify generation works.

### Dataset integration smoke test

```bash
python scripts/test_tend_loader.py
```

Loads Spider + BIRD train/test splits from Hugging Face (or cache) and validates required TEND fields. Also checks the 50-row frozen gold validation set.

### SFT dataset builder smoke test

```bash
python scripts/build_sft_dataset.py
```

Builds 50-row samples for each task (`text2sql`, `sql2nosql`, `nosql2doc`) from combined Spider + BIRD train data and prints filter/token statistics.

### LoRA pre-flight check

Before training, confirm `lora.target_modules` in `configs/default.yaml` match the base model architecture:

```bash
python scripts/inspect_lora_modules.py
python scripts/inspect_lora_modules.py --model Salesforce/codegen-350M-multi
```

Prints attention module suffixes and confirms trainable parameter count > 0. For CodeGen-350M the configured modules are `qkv_proj` and `out_proj`.

---

## Training (LoRA Fine-Tuning)

LoRA fine-tuning trains **one adapter per task** on the causal LM base model (`MODEL_NAME`). Base weights stay frozen in `models/base/`; only adapter weights are saved under `models/checkpoints/<run>/<task>/`.

Pass **`--version`** (alias `--name`) to name the checkpoint run folder (e.g. `v1`, `2506-full`). If omitted, the run folder defaults to today's date as `DDMM` (e.g. `2706` on 27 June).

### Supported tasks

| Task | Target field | Training prompt ends with |
| ---- | ------------ | ------------------------- |
| `text2sql` | `sql` | `\n\nSQL:` |
| `sql2nosql` | `nosql_query` | `\n\nMongoDB:` |
| `nosql2doc` | `documentation` | `\n\nDocumentation:` |

### Training data

By default, training loads **Spider + BIRD train** rows from Hugging Face TEND (`~10,697` combined rows). Held-out eval during training uses **Spider + BIRD test** splits. Override with `--train-csv` / `--eval-csv` (CSV or JSONL).

### Sequence budget

Configured in `configs/default.yaml`:

```yaml
training:
  max_length: 2048           # total sequence budget (matches model.max_length)
  max_target_tokens: 256     # reserve for completion; prompt budget ≈ 1791
```

Long prompts are truncated from the **start** (schema head dropped, question + tail kept) so the supervised target is never cut. Only ~0.02% of rows exceed the budget at 2048 tokens.

### Train a single task

```bash
# Full training (default: 5 epochs, spider+bird train/eval)
python scripts/train_lora.py --version v1 --task text2sql

# Smoke / debug run
python scripts/train_lora.py --version v1 --task text2sql --max-samples 50 --epochs 1 --no-mlflow

# Override device or output directory
python scripts/train_lora.py --version v1 --task sql2nosql --device mps
python scripts/train_lora.py --task sql2nosql --output-dir models/checkpoints/v2/sql2nosql

# Custom training data
python scripts/train_lora.py --version v1 --task nosql2doc --train-csv data/my_train.jsonl --eval-csv data/my_eval.jsonl
```

| Flag | Default | Description |
| ---- | ------- | ----------- |
| `--task` | *(required)* | `text2sql`, `sql2nosql`, or `nosql2doc` |
| `--version` / `--name` | `DDMM` | Checkpoint run folder under `models/checkpoints/` (e.g. `v1`) |
| `--train-csv` | HF spider+bird train | Optional CSV/JSONL training rows |
| `--eval-csv` | HF spider+bird test | Optional CSV/JSONL eval rows |
| `--output-dir` | `models/checkpoints/<run>/<task>/` | Adapter output directory (overrides `--version`) |
| `--max-samples` | all rows | Limit rows for smoke/debug |
| `--epochs` | `5` (from config) | Override epoch count |
| `--device` | `auto` | `auto`, `cuda`, `mps`, `dml`, or `cpu` |
| `--config` | `configs/default.yaml` | Alternate YAML config |
| `--no-mlflow` | off | Disable MLflow logging |

### Train all tasks

```bash
# Train text2sql → sql2nosql → nosql2doc sequentially
python scripts/train_all_lora.py --version v1

# Smoke run
python scripts/train_all_lora.py --version v1 --max-samples 50 --epochs 1 --no-mlflow

# Run baseline eval first, then train
python scripts/train_all_lora.py --version v1 --run-baseline --baseline-max-samples 50

# Dry run (print planned tasks)
python scripts/train_all_lora.py --version v1 --dry-run
```

| Flag | Default | Description |
| ---- | ------- | ----------- |
| `--version` / `--name` | `DDMM` | Checkpoint run folder under `models/checkpoints/` (e.g. `v1`) |
| `--tasks` | all three | Subset of tasks to train |
| `--run-baseline` | off | Run baseline eval before training |
| `--dry-run` | off | Print planned runs without training |

After all tasks complete, `train_all_lora.py` verifies adapter artifacts and writes a timestamped summary JSON to `models/checkpoints/<run>/training_summary_<timestamp>.json`.

### Training hyperparameters (`configs/default.yaml`)

```yaml
training:
  datasets: [spider, bird]
  split: train
  eval_datasets: [spider, bird]
  eval_split: test
  max_length: 2048
  max_target_tokens: 256
  learning_rate: 2.0e-4
  weight_decay: 0.01
  epochs: 5
  per_device_train_batch_size: 8
  per_device_eval_batch_size: 8
  gradient_accumulation_steps: 4   # effective batch size = 32
  warmup_ratio: 0.05
  lr_scheduler_type: cosine
  max_grad_norm: 1.0
  fp16: false
  bf16: false

lora:
  r: 16
  lora_alpha: 32
  lora_dropout: 0.05
  bias: none
  target_modules:
    - qkv_proj
    - out_proj
```

Training uses TRL `SFTTrainer` with **completion-only loss** (prompt tokens masked). Each run writes:

```
models/checkpoints/v1/
├── text2sql/
│   ├── adapter_config.json
│   ├── adapter_model.safetensors
│   └── run_metadata.json      # train/eval loss, filter stats, token stats
├── sql2nosql/
├── nosql2doc/
├── train_all_lora.log
└── training_summary_<timestamp>.json
```

### Verify trained adapters

```bash
python scripts/verify_lora_adapters.py --version v1
python scripts/verify_lora_adapters.py --version v1 --task text2sql
python scripts/verify_lora_adapters.py --version v1 --no-require-metadata
```

Checks for `adapter_config.json`, `adapter_model.safetensors`, and optionally `run_metadata.json`.

### Training wall-clock notes

| Device | Approx. time per task (full 10k rows, 5 epochs) |
| ------ | ----------------------------------------------- |
| CUDA GPU | Hours (fastest) |
| Apple MPS | ~10–15+ hours per task |
| Windows DirectML (Intel/AMD) | Faster than CPU for inference; training experimental |
| CPU | Very slow; use `--max-samples` for smoke tests |

Use `--max-samples 50 --epochs 1 --no-mlflow` to validate the pipeline before committing to a full run.

---

## Evaluation

### `run_baseline_eval.py` — Primary evaluation script

Evaluates the configured model (base or LoRA adapter) on all three tasks. By default uses the **frozen Spider gold validation set** (`data/spider_gold_validation.jsonl`, 50 examples).

```bash
# Default: 50 gold validation examples, all three tasks
python scripts/run_baseline_eval.py

# Limit samples
python scripts/run_baseline_eval.py --max-samples 20

# Log to MLflow
python scripts/run_baseline_eval.py --mlflow

# Named output folder under results/
python scripts/run_baseline_eval.py --output my_baseline_run

# Skip Ollama semantic judge (faster, no Ollama required)
python scripts/run_baseline_eval.py --no-judge

# Evaluate full Hugging Face TEND split instead of gold validation
python scripts/run_baseline_eval.py --full-split --split test --tend-config spider
```

| Flag | Default | Description |
| ---- | ------- | ----------- |
| `--tend-config` | `spider` | TEND subset: `spider` or `bird` |
| `--split` | `test` | TEND split when `--full-split` is set |
| `--full-split` | off | Use full HF split instead of gold validation |
| `--max-samples` | `50` | Number of examples |
| `--mlflow` | off | Log metrics to MLflow |
| `--output` | auto-generated | Run folder name under `results/` |
| `--adapter-run` / `--version` / `--name` | none | LoRA checkpoint run (e.g. `v1`) |
| `--no-judge` | off | Skip Ollama semantic judge |

**Metrics computed:** Exact Match, Execution Accuracy, Syntax Validity, BLEU, ROUGE-L, BERTScore, CodeBLEU, Ollama judge correct rate.

Output per run:

```
results/<run_name>/
├── metrics.json
├── text2sql_details.csv
├── sql2nosql_details.csv
└── documentation_details.csv
```

#### Evaluate with LoRA adapters

Use `--adapter-run` to load task-specific adapters from a checkpoint run:

```bash
python scripts/run_baseline_eval.py --adapter-run v1 --max-samples 50
```

Each task loads its own adapter from `models/checkpoints/v1/<task>/` on top of the base model in `models/base/`.

For single-task loading via `.env`, set both `MODEL_ADAPTER` and `MODEL_ADAPTER_RUN`:

```bash
MODEL_ADAPTER=text2sql MODEL_ADAPTER_RUN=v1 python scripts/run_baseline_eval.py --max-samples 50
```

### `run_all_baseline_eval.py` — Multi-model comparison

Runs baseline eval across a hardcoded list of models on the gold validation set:

```bash
python scripts/run_all_baseline_eval.py
python scripts/run_all_baseline_eval.py --max-samples 50
python scripts/run_all_baseline_eval.py --dry-run
python scripts/run_all_baseline_eval.py --list-models
python scripts/run_all_baseline_eval.py --no-judge
```

Output folder format: `spider_gold_validation_<model>_<DDMM>_<HHMM>/`

---

## Local Caching

### Base models

```
models/base/Salesforce__codegen-350M-multi/
├── config.json
├── model.safetensors
├── tokenizer files
└── .downloaded          # cache marker
```

Checked before every load. Downloaded from HuggingFace only when missing. Configured by `MODEL_NAME` in `.env`.

### LoRA adapters (training output)

```
models/checkpoints/
└── v1/                          # --version v1 (or DDMM if omitted)
    ├── text2sql/
    │   ├── adapter_config.json
    │   ├── adapter_model.safetensors
    │   └── run_metadata.json
    ├── sql2nosql/
    ├── nosql2doc/
    ├── train_all_lora.log
    └── training_summary_<timestamp>.json
```

Set `MODEL_ADAPTER=text2sql` and `MODEL_ADAPTER_RUN=v1` in `.env` to load a single adapter at inference time, or pass `--adapter-run v1` to `run_baseline_eval.py` for all three tasks.

### TEND dataset (Hugging Face)

- Loaded via `src/datasets/tend_loader.py` from `TEND_DATASET_ID`
- Cached as standardized JSONL under `TEND_CACHE_DIR`
- Configurations: `spider`, `bird`
- Splits: `train`, `test` (`test` = source validation/dev)

```
data/cache/tend/care2achieve__tend/spider/train.jsonl
data/cache/tend/care2achieve__tend/spider/test.jsonl
```

```python
from src.datasets.tend_loader import TENDLoader

loader = TENDLoader(config="spider")
examples = loader.load_split("test")
print(examples[0]["question"], examples[0]["sql"])
```

---

## Configuration

### Environment (`.env`) — models, adapters, datasets, paths

All model names, adapter selection, dataset URLs, and storage paths are configured here.

### YAML (`configs/default.yaml`) — runtime behavior

```yaml
model:
  max_length: 2048
  device: "auto"       # auto (cuda > mps > dml > cpu), cuda, mps, dml, cpu

generation:
  max_new_tokens: 256
  documentation_max_new_tokens: 96
  temperature: 0.7
  decoding_strategy: "greedy"

evaluation:
  batch_size: 8
  max_samples: 50
  mlflow_tracking_uri: "sqlite:///mlflow.db"
  experiment_name: "codegen-text2sql"

training:
  max_length: 2048
  max_target_tokens: 256
  epochs: 5
  learning_rate: 2.0e-4
  # ... see full file for LoRA and batch settings

lora:
  target_modules: [qkv_proj, out_proj]
  r: 16
  lora_alpha: 32
```

To use a different HuggingFace base model, change `MODEL_NAME` in `.env`, run `inspect_lora_modules.py` to verify LoRA target modules, and update `lora.target_modules` in the YAML if needed.

---

## Datasets

See [data/DATASETS.md](data/DATASETS.md) for TEND field definitions, split naming, and loading examples.

| Dataset | Use |
| ------- | --- |
| TEND (HF `care2achieve/tend`) | LoRA training (spider + bird train/test) |
| `data/spider_gold_validation.jsonl` | Frozen 50-example baseline evaluation |

---

## Evaluation Metrics

| Metric | Description |
| ------ | ----------- |
| Exact Match | Normalized SQL string equality |
| Execution Accuracy | Result set comparison on SQLite |
| Syntax Validity | Valid SQL structure rate |
| BLEU | N-gram overlap |
| ROUGE-L | Longest common subsequence |
| BERTScore | Contextual embedding similarity |
| CodeBLEU | n-gram + syntax + semantic match |
| Judge Correct Rate | Ollama semantic equivalence (optional) |

---

## MLflow Tracking

Training and evaluation runs can log to MLflow when enabled:

```bash
python scripts/train_lora.py --task text2sql          # MLflow on by default
python scripts/run_baseline_eval.py --mlflow

mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Tracked per run: model name, task, hyperparameters, train/eval loss, all evaluation metrics.

---

## Reproducibility

Seeds are set in `configs/default.yaml` for `random`, `numpy`, and `torch`. All evaluation and training scripts call `set_seeds(config)` before running.

---

## Troubleshooting

| Issue | Fix |
| ----- | --- |
| `MODEL_NAME is not set` | Run `cp .env.example .env` and set `MODEL_NAME` |
| `BERTSCORE_MODEL_NAME is not set` | Add `BERTSCORE_MODEL_NAME=distilbert-base-uncased` to `.env` |
| `ModuleNotFoundError: src` | Export `PYTHONPATH=$(pwd)` from project root |
| Model re-downloads every run | Check `models/base/<slug>/.downloaded` exists; ensure write permissions |
| Out of memory on GPU/MPS/DirectML | Reduce `--max-samples`, set `--device cpu`, or lower `per_device_train_batch_size` in config |
| Zero trainable LoRA params | Run `inspect_lora_modules.py`; fix `lora.target_modules` in config |
| Adapter not found | Ensure `models/checkpoints/<run>/<task>/adapter_config.json` exists; use `--adapter-run <run>` or set `MODEL_ADAPTER=<task>` and `MODEL_ADAPTER_RUN=<run>` |
| Ollama judge fails | Start Ollama locally or pass `--no-judge` to skip semantic scoring |
| Token length warnings during training | Update to latest code; prompts are truncated to 2048 before SFT tokenization |
| DirectML training fails | Expected on some builds; use `--device cpu` for training or train on CUDA/MPS |
| Training very slow on Mac | Expected on MPS/CPU; use smoke runs (`--max-samples 50 --epochs 1`) to validate first |
| Training very slow on Windows Intel GPU | Use `--device dml` for eval; keep training on CPU or offload to CUDA/MPS |

---

## License

Research and academic use. See individual dataset and model licenses for Spider, BIRD, and CodeGen.
