# CodeGen – Interactive Database Querying Using Small Code Language Models

A modular, reproducible, research-oriented project for evaluating **Salesforce/codegen-350M-multi** on database query generation and translation tasks.

## Features

- **Natural Language → SQL** generation with greedy and beam search decoding
- **SQL → MongoDB** rule-based translation (SELECT, WHERE, ORDER BY, LIMIT, GROUP BY)
- **Interactive query pipeline** with validation, execution, and explanations
- **Benchmark evaluation** on Spider and BirdBench datasets
- **Metrics**: Exact Match, Execution Accuracy, BLEU, ROUGE-L, BERTScore, CodeBLEU
- **MLflow** experiment tracking
- **FastAPI** REST API with Swagger docs
- **Streamlit** interactive UI

## Project Structure

```
CodeGen-Studio/
├── data/                    # Dataset cache and sample databases
├── datasets/                # Spider & BIRD loaders, preprocessing
├── src/
│   ├── text2sql/            # Prompt builder, generator, validator, executor
│   ├── sql2nosql/           # SQL to MongoDB translator
│   ├── query_engine/        # End-to-end interactive pipeline
│   ├── api/                 # FastAPI backend
│   └── models/              # HuggingFace model loader
├── evaluation/              # Metrics, benchmarks, MLflow tracking
├── streamlit_app/           # Streamlit UI
├── configs/                 # YAML configuration
├── tests/                   # pytest test suite
├── notebooks/               # Demo notebooks
├── scripts/                 # Reproducibility scripts
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Quick Start

### 1. Install Dependencies

```bash
# Linux / macOS
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```powershell
# Windows PowerShell
cd c:\Users\Bhavani\Documents\Codegen\CodeGen-Studio
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
```

Or run the setup script:

```powershell
.\scripts\setup_env.ps1
```

### 2. Create Sample Database

```bash
python scripts/setup_sample_db.py
```

### 3. Run Tests

```bash
pytest tests/ --cov=src --cov=datasets --cov=evaluation --cov-report=term-missing
```

### 4. Start API Server

```bash
# Linux/macOS
bash scripts/run_api.sh

# Windows
set PYTHONPATH=%CD% && uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs: http://localhost:8000/docs

### 5. Start Streamlit UI

```bash
bash scripts/run_streamlit.sh
# or: streamlit run streamlit_app/app.py
```

UI: http://localhost:8501

### 6. Run Evaluation

```bash
bash scripts/evaluate.sh spider validation
bash scripts/evaluate.sh bird validation
```

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

## Docker

```bash
docker-compose up --build
```

Services:
- **API**: http://localhost:8000
- **Streamlit**: http://localhost:8501
- **MLflow**: http://localhost:5000

## Model

Primary model: [Salesforce/codegen-350M-multi](https://huggingface.co/Salesforce/codegen-350M-multi)

Configure in `configs/default.yaml`:

```yaml
model:
  name: "Salesforce/codegen-350M-multi"
  device: "auto"  # auto, cuda, cpu
```

Replace with any HuggingFace causal LM by changing the model name.

## Datasets

### Spider
- Auto-downloads from GitHub
- Standardized format: `{question, schema, sql}`

### BirdBench
- Auto-downloads from DAMO-ConvAI repository
- Includes evidence and difficulty metadata

```python
from datasets.spider_loader import SpiderLoader

loader = SpiderLoader()
examples = loader.load_split("validation")
print(examples[0])
```

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

## MLflow Tracking

```bash
mlflow ui --backend-store-uri mlruns
```

Tracked per run: model name, dataset, prompt template, all metrics.

## Reproducibility

Seeds are set in `configs/default.yaml` for `random`, `numpy`, and `torch`.

```bash
bash scripts/train.sh      # Seed setup & training config
bash scripts/evaluate.sh   # Benchmark evaluation
```

## Testing

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov=datasets --cov=evaluation
```

Test coverage targets: dataset loading, SQL generation, validation, execution, NoSQL translation, API endpoints.

## License

Research and academic use. See individual dataset and model licenses for Spider, BIRD, and CodeGen.
