# Code Generation Capstone

A two-task code synthesis system that fine-tunes **codegen-350M-multi** for:

1. **NL → Python** — natural language to Python code (Spider, BirdBench, BigQuery/Python, Pile)
2. **Java → Python** — cross-language translation (CoDocBench, CodeParrot)

Includes RAG inference, Docker-based code execution sandbox, and evaluation with BLEU, BERTScore, CodeBLEU, CodeBERTScore, and execution accuracy.

## Project Structure

```
PRAgenticAI/
├── data/scripts/       # Dataset download & preprocessing
├── training/           # LoRA fine-tuning scripts & configs
├── inference/          # RAG pipeline, generator, FastAPI
├── evaluation/         # Metrics & benchmark runner
├── sandbox/            # Docker execution environment
├── tests/              # Pytest suite
└── notebooks/        # Dataset exploration
```

## Quick Start

### 1. Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# For training:
pip install -r requirements-train.txt
```

**Mac (Apple Silicon / MPS):** PyTorch will automatically use the Mac GPU via MPS (Metal). No CUDA install needed — `pip install torch` is sufficient.

```bash
# Verify MPS is available
python -c "import torch; print('MPS:', torch.backends.mps.is_available())"
```

**Linux/Windows (NVIDIA GPU):** Install CUDA-enabled PyTorch if needed:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### 2. Download & Preprocess Data

```bash
bash data/scripts/download.sh
python data/scripts/preprocess_nl2py.py
python data/scripts/preprocess_java2py.py
```

### 3. Fine-tune Models

**Mac (MPS — recommended on Apple Silicon):**
```bash
python training/train_nl2py.py --config training/configs/nl2py_mps.yaml
python training/train_java2py.py --config training/configs/java2py_mps.yaml
```

**CUDA GPU:**
```bash
python training/train_nl2py.py --config training/configs/nl2py.yaml
python training/train_java2py.py --config training/configs/java2py.yaml
```

Device selection order is automatic: CUDA → MPS (Mac GPU) → CPU. MPS configs use `bf16` and smaller batch sizes tuned for unified memory.

## Run on Google Colab

The project also runs on Google Colab (NVIDIA GPU). Device selection is automatic, so the same code targets CUDA on Colab, MPS on Mac, and CPU otherwise.

1. **Upload the project to Google Drive.** Copy the whole project folder (including `data/raw/avatar_tc` and any `data/processed`) to e.g. `MyDrive/PRAgenticAI`. The `data/` and `models/` folders are gitignored, so they must be uploaded manually.
2. **Open a notebook in Colab** — `notebooks/finetune_qwen.ipynb` (preprocess + train + eval) or `notebooks/baseline_qwen_eval.ipynb` (baseline eval only).
3. **Select a GPU runtime:** Runtime → Change runtime type → GPU.
4. **Run the two "Colab setup" cells first.** They mount Drive, point `PROJECT_ROOT` at your uploaded folder (edit `DRIVE_PROJECT_PATH` if you used a different location), and install dependencies. Colab already ships a CUDA-enabled PyTorch.
5. **Run the rest of the notebook top to bottom.**

For CLI training on Colab, use the Colab/CUDA config:

```bash
python data/scripts/preprocess_avatar_tc.py
python training/train_java2py.py --config training/configs/java2py_qwen_colab.yaml
```

`java2py_qwen_colab.yaml` sets `device: auto` and `fp16: true` (valid on every Colab GPU including the free T4; on A100/L4 you can switch to `bf16: true`).

**Colab scope and limitations:**
- Colab supports the notebook flow only: preprocess, LoRA fine-tune, and the BLEU / CodeBLEU / BERTScore / CodeBERTScore eval. This covers `notebooks/finetune_qwen.ipynb` and `notebooks/baseline_qwen_eval.ipynb`.
- The Docker sandbox execution-accuracy eval (section 5) and the FastAPI / uvicorn server (section 4) are **not** supported on Colab — Colab has no Docker daemon, and serving an API would require external tunneling.
- The `data/raw/avatar_tc` dataset is bundled with the project and must be uploaded to Drive along with the rest of the folder. `data/scripts/download.sh` does **not** fetch AVATAR-TC (it only handles Spider / BirdBench / CoDocBench).
- After the dependency-install cell upgrades `transformers` / `peft` / `trl` over Colab's preinstalled versions, you may need to restart the runtime (Runtime -> Restart session) and re-run from the setup cell.

### 4. Build RAG Index & Start API

```bash
python inference/rag_pipeline.py --task nl2py --build-index
python inference/rag_pipeline.py --task java2py --build-index
uvicorn inference.api:app --host 0.0.0.0 --port 8000
```

Automated **NL → Java → Python** pipeline (one natural-language prompt):

```bash
curl -X POST http://localhost:8000/nl2java2py \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Write a function that checks if a string is a palindrome"}'
```

Response includes both `java_code` and `python_code`.
### 5. Run Evaluation

```bash
# Build sandbox image first
docker build -t code-sandbox sandbox/

python evaluation/run_eval.py --task nl2py --split test --max-samples 100
python evaluation/run_eval.py --task java2py --split test --max-samples 100
```

### 6. Run Tests

```bash
pytest tests/ -v
```

## Deploy to Hugging Face

Upload the merged multi-task checkpoint and launch a Gradio Space demo.

```bash
.venv/bin/pip install -r requirements-deploy.txt
hf auth login

# Upload model + push Space (defaults to Saikrishna2511)
.venv/bin/python scripts/deploy_to_hf.py --hardware cpu-basic
```

Space source lives in `deploy/hf_space/`. Set `MODEL_ID` in Space Settings if the variable was not applied automatically.

Live demo: https://huggingface.co/spaces/Saikrishna2511/qwen-multitask-demo

## Run locally

Launch the same Gradio UI on your machine (uses `models/qwen_multitask/merged` by default):

```bash
source .venv/bin/activate
pip install -r requirements-deploy.txt
python scripts/run_local_gradio.py
```

Open **http://127.0.0.1:7860**. On Apple Silicon, inference uses MPS automatically.

Options:

```bash
# Hugging Face Hub model instead of local weights
python scripts/run_local_gradio.py --model-id Saikrishna2511/qwen-multitask

# Different port if 7860 is in use
python scripts/run_local_gradio.py --port 7861
```

Troubleshooting:

- **Model not found** — ensure `models/qwen_multitask/merged` exists (from training) or pass `--model-id` for a Hub repo
- **Slow first request** — normal; ~988MB loads into memory once at startup
- **Port already in use** — rerun with `--port 7861`

Smoke-test handlers without loading the model:

```bash
python scripts/smoke_test_space.py
```

## API Endpoints

| Method | Path           | Body                                              | Response                          |
|--------|----------------|---------------------------------------------------|-----------------------------------|
| POST   | `/nl2java2py`  | `{"prompt": "check if a string is a palindrome"}` | `java_code` + `python_code`       |
| POST   | `/nl2py`       | `{"query": "sort a list"}`                        | Python code                       |
| POST   | `/java2py`     | `{"java_code": "..."}`                            | Python code                       |
| POST   | `/code2doc`    | `{"python_code": "..."}`                          | Documentation                     |
| POST   | `/comments`    | `{"python_code": "..."}`                          | Commented Python                  |
| GET    | `/health`      | —                                                 | status + model_path               |

## Datasets

| Dataset      | Task    | Source                                      |
|--------------|---------|---------------------------------------------|
| Spider       | NL2Py   | https://spider2-sql.github.io/              |
| BirdBench    | NL2Py   | https://bird-bench.github.io/               |
| CoDocBench   | Java2Py | https://github.com/kunpai/codocbench        |
| CodeParrot   | Both    | HuggingFace `codeparrot/github-code`        |
| BigQuery/Py  | NL2Py   | HuggingFace datasets                        |

## Evaluation Metrics

- **BLEU / BERTScore** — natural language similarity
- **CodeBLEU / CodeBERTScore** — code similarity vs ground truth
- **Execution Accuracy** — sandbox pass rate on test cases

## References

- [codegen-350M-multi](https://huggingface.co/Salesforce/codegen-350M-multi)
- [CoDocBench](https://github.com/kunpai/codocbench)
- [Spider](https://spider2-sql.github.io/)
- [BirdBench](https://bird-bench.github.io/)
- [CodeBLEU](https://arxiv.org/abs/2009.10297)
- [CodeBERTScore](https://arxiv.org/abs/2302.05527)
