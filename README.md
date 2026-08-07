# Code Generation Capstone

Multi-task code synthesis built on fine-tuned **Qwen2.5-Coder-0.5B-Instruct**, plus a **LangGraph** agent that routes, generates, executes, judges, and fixes code.

**Tasks (single multitask checkpoint):**

1. **NL → Python** — natural language to Python (MBPP)
2. **Java → Python** — cross-language translation (AVATAR-TC, CoDocBench)
3. **Code → Documentation** — Python doc generation (DocuMint)
4. **Code comments** — add comments to Python

**Agentic pipeline:** NL / Java / pseudocode / design-pattern → Java → Python → sandbox execute → LLM judge → Fix loop (AST-aware).

Also includes RAG few-shot inference, a Docker execution sandbox, FastAPI + Gradio demos, and evaluation with BLEU, BERTScore, CodeBLEU, CodeBERTScore, and execution accuracy.

Live demo: https://huggingface.co/spaces/Saikrishna2511/qwen-multitask-demo  
Model: https://huggingface.co/Saikrishna2511/qwen-multitask

## Project Structure

```
codegen26/
├── agent/              # LangGraph agent (route → codegen → execute → judge → fix)
├── data/scripts/       # Dataset download & preprocessing
├── training/           # LoRA fine-tuning scripts & configs
├── inference/          # RAG pipeline, generator, FastAPI
├── evaluation/         # Metrics, multitask / agent / baseline runners
├── sandbox/            # Docker execution environment
├── deploy/             # HF Space Gradio app + model card
├── scripts/            # Deploy, local Gradio, smoke tests
├── tests/              # Pytest suite
├── notebooks/          # Colab fine-tune & baseline eval
└── langgraph.json      # LangGraph CLI graph entrypoint
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

**Mac (Apple Silicon / MPS):** PyTorch uses the Mac GPU via MPS. No CUDA install needed — `pip install torch` is sufficient.

```bash
python -c "import torch; print('MPS:', torch.backends.mps.is_available())"
```

**Linux/Windows (NVIDIA GPU):**

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### 2. Download & Preprocess Data

```bash
# Optional local extras (CoDocBench). Spider/Bird are off by default (DOWNLOAD_SQL=1 to fetch).
bash data/scripts/download.sh
python data/scripts/preprocess_nl2py.py   # MBPP-only NL2Py by default
python data/scripts/preprocess_java2py.py

# Qwen Stage 1 — AVATAR-TC Java→Python
# Place under data/raw/: avatar_tc, classeval_t, design_patterns_solid
# (+ optional codocbench/). DocuMint + MBPP come from Hugging Face at preprocess.

# Stage 1 Java→Python mix: full AVATAR-TC + ClassEval-T + design patterns (+ CoDocBench)
python data/scripts/preprocess_java_oop.py --avatar-fraction 1.0 --design-upsample 2

# Stage 2 multitask: same Java2Py sources + MBPP (NL2Py) + DocuMint
python data/scripts/preprocess_multitask.py --avatar-fraction 1.0 --design-upsample 2
```

### 3. Fine-tune (Qwen two-stage LoRA)

**Mac (MPS):**

```bash
# Stage 1: specialize on Java→Python (use combined data after preprocess_java_oop)
python training/train_java2py.py --config training/configs/java2py_qwen_colab.yaml
# or lighter local: training/configs/java2py_qwen_mps.yaml (avatar-only path)

# Stage 2: multitask from the Stage-1 merged checkpoint
python training/train_multitask.py --config training/configs/qwen_multitask_mps.yaml
```

**Colab / CUDA (recommended: A100 40GB; L4/A10 good; T4 OK with batch 4):**

```bash
python training/train_java2py.py --config training/configs/java2py_qwen_colab.yaml
python training/train_multitask.py --config training/configs/qwen_multitask_colab.yaml
```

Or run `notebooks/finetune_qwen.ipynb` end-to-end (includes Hugging Face push cell).

Device selection order is automatic: CUDA → MPS → CPU. Merged weights land in `models/java2py_qwen/merged` then `models/qwen_multitask/merged`.

## Run on Google Colab

Works from the browser or the **Cursor Colab extension** (Select Kernel → Colab → GPU). The Colab VM cannot read your Mac path — sync this workspace (or a zip) so `PROJECT_ROOT` resolves under Drive/`/content`.

1. Open `notebooks/finetune_qwen.ipynb` in Cursor or Colab and select a **GPU** runtime (**A100** preferred).
2. Run the **GitHub clone** cell — pulls [krishnasaicareer/codegen26](https://github.com/krishnasaicareer/codegen26.git) `main` into **`/content/codegenQwen/codegen26`** (source of truth; not an old Drive zip).
3. Run PROJECT_ROOT → inventory → optional `download.sh` for `codocbench` → install. NL2Py = **MBPP only** (HF); DocuMint on HF.
4. Set `RUN_PREPROCESS` / `RUN_TRAINING` / `RUN_MULTITASK_*` / `RUN_HF_PUSH` as needed.
5. Store `HF_TOKEN` (and optional `GITHUB_TOKEN` for private clone) in Colab Secrets before publishing.

Colab covers preprocess, LoRA fine-tune, Hub upload, and similarity metrics. The Docker sandbox and FastAPI server are **not** supported on Colab.

## LangGraph Agent

The agent (`agent/`) implements:

`route → retrieve? → (NL / Java / pseudocode / pattern / repo) → Java→Python → execute → judge → (fix → execute)*`

```bash
# API (loads multitask model; wires agent on startup)
uvicorn inference.api:app --host 0.0.0.0 --port 8000

# Full solve loop
curl -X POST http://localhost:8000/agent/solve \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Write a function that checks if a string is a palindrome","max_retries":3}'

# Generate only (no execute/judge/fix)
curl -X POST http://localhost:8000/agent/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Implement a Singleton logger class","unit":"class"}'

# Fix only
curl -X POST http://localhost:8000/agent/fix \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"factorial of n","python_code":"def fac(n): return n","runtime":"AssertionError"}'
```

Optional env vars:

| Variable | Default | Purpose |
|----------|---------|---------|
| `MODEL_ID` | local `models/qwen_multitask/merged` or Hub `Saikrishna2511/qwen-multitask` | Fine-tuned multitask model (codegen, Ask answers, planner when set to `ft`) |
| `JUDGE_MODEL_ID` | `Qwen/Qwen2.5-1.5B-Instruct` | Separate judge LLM (`ft` reuses codegen) |
| `ASK_MODEL_ID` | `Qwen/Qwen2.5-1.5B-Instruct` | Ask Agent Q&A prose model (`ft` reuses fine-tuned codegen) |
| `ASK_PLANNER_MODEL_ID` | `Qwen/Qwen2.5-1.5B-Instruct` | Intent/retrieval planner for Ask Agent |
| `RAG_MIN_SCORE` | `0.35` | Minimum cosine score for repo RAG chunks |
| `RAG_WEAK_SCORE` | `0.55` | Below this, Ask Agent retries overview retrieval or reports low confidence |

Rebuild a repo index after index-builder changes (or when `.py`/`.java` duplicate stubs skew retrieval):

```bash
python scripts/build_repo_index.py --repo-root /path/to/your/repo
```

LangGraph CLI registers four graphs in [`langgraph.json`](langgraph.json):

| Graph | Module | Purpose |
|-------|--------|---------|
| `codegen_agent` | `agent/graph.py` | NL→Java→Python codegen + execute + judge + fix loop |
| `ask_agent` | `agent/ask_graph.py` | Repo Q&A with planner + RAG retrieval |
| `code_agent` | `agent/code_graph.py` | NL→Python/Java generation and Java→Python migration |
| `debug_agent` | `agent/debug_graph.py` | Scan, diagnose, and fix Python files |

View and debug in **LangGraph Studio**:

```bash
pip install -U "langgraph-cli[inmem]"
cp .env.example .env   # set MODEL_ID and optional LANGSMITH_* keys
langgraph dev
```

Open the Studio URL printed in the terminal (typically `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`) and select a graph.

Sample Studio inputs:

```json
{"nl_prompt": "Write a palindrome checker", "max_retries": 3, "unit": "function"}
```

```json
{"user_message": "How does routing work?", "history": [], "session_state": {}, "repo_root": "/path/to/repo", "max_files": 20, "rag_top_k": 5}
```

```json
{"user_message": "python: reverse a string", "history": [], "session_state": {}, "repo_root": "/path/to/repo", "max_retries": 3, "max_files": 20}
```

```json
{"user_message": "scan", "history": [], "session_state": {}, "repo_root": "/path/to/repo", "max_files": 20, "max_retries": 3}
```

Enable LangSmith tracing by setting `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` in `.env`.

Agent vs single-shot eval:

```bash
python evaluation/run_agent_eval.py --limit 5
```

### 4. Build RAG Index & Start API

```bash
python inference/rag_pipeline.py --task nl2py --build-index
python inference/rag_pipeline.py --task java2py --build-index
uvicorn inference.api:app --host 0.0.0.0 --port 8000
```

Single-shot **NL → Java → Python** (no agent loop):

```bash
curl -X POST http://localhost:8000/nl2java2py \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Write a function that checks if a string is a palindrome"}'
```

### 5. Run Evaluation

```bash
docker build -t code-sandbox sandbox/

python evaluation/run_eval.py --task nl2py --split test --max-samples 100
python evaluation/run_eval.py --task java2py --split test --max-samples 100
python evaluation/run_multitask_eval.py
python evaluation/run_baseline_qwen.py
python evaluation/run_agent_eval.py --limit 5
```

### 6. Run Tests

```bash
pytest tests/ -v
```

## Deploy to Hugging Face

```bash
.venv/bin/pip install -r requirements-deploy.txt
hf auth login

.venv/bin/python scripts/deploy_to_hf.py --hardware cpu-basic
```

Space source: `deploy/hf_space/`. Set `MODEL_ID` in Space Settings if it was not applied automatically.

## Run Gradio Locally

```bash
source .venv/bin/activate
pip install -r requirements-deploy.txt
python scripts/run_local_gradio.py
```

Open **http://127.0.0.1:7860**. On Apple Silicon, inference uses MPS automatically.

```bash
# Hub model instead of local weights
python scripts/run_local_gradio.py --model-id Saikrishna2511/qwen-multitask

# Different port
python scripts/run_local_gradio.py --port 7861
```

Smoke-test Space handlers without loading the model:

```bash
python scripts/smoke_test_space.py
```

## API Endpoints

| Method | Path               | Body (summary)                                      | Response                                      |
|--------|--------------------|-----------------------------------------------------|-----------------------------------------------|
| POST   | `/nl2java2py`      | `{"prompt": "..."}`                                 | `java_code` + `python_code`                   |
| POST   | `/nl2py`           | `{"query": "...", "use_rag": true}`                 | Python code                                   |
| POST   | `/java2py`         | `{"java_code": "...", "use_rag": true}`             | Python code                                   |
| POST   | `/code2doc`        | `{"python_code": "..."}`                            | Documentation                                 |
| POST   | `/comments`        | `{"python_code": "..."}`                            | Commented Python                              |
| POST   | `/agent/solve`     | `{"prompt": "...", "max_retries": 3}`               | codes + judge + trace (full loop)             |
| POST   | `/agent/generate`  | `{"prompt": "...", "unit": "function\|class"}`      | Java + Python (no execute)                    |
| POST   | `/agent/fix`       | `{"prompt": "...", "python_code": "...", ...}`      | Fixed Python + AST info                       |
| GET    | `/agent/problems`  | —                                                   | Problem-pack list                             |
| GET    | `/health`          | —                                                   | status, `model_path`, `agent_ready`           |

## Datasets

| Dataset      | Task              | Source / notes                                      |
|--------------|-------------------|-----------------------------------------------------|
| AVATAR-TC    | Java2Py (Stage 1) | Bundled under `data/raw/avatar_tc`                  |
| MBPP         | NL2Py             | HuggingFace `mbpp` (default NL2Py source)           |
| DocuMint     | Code2Doc          | HuggingFace `documint/DocuMint` (no local folder)   |
| CoDocBench   | Java2Py           | `data/raw/codocbench` via `download.sh` (optional)  |
| Spider/Bird  | (unused)          | Opt-in only: `DOWNLOAD_SQL=1` + `preprocess_nl2py.py --include-sql` |
| CodeParrot   | Both (legacy)     | HuggingFace `codeparrot/github-code`                |

## Evaluation Metrics

- **BLEU / BERTScore** — natural language similarity
- **CodeBLEU / CodeBERTScore** — code similarity vs ground truth
- **Execution Accuracy** — sandbox pass rate on test cases
- **Agent eval** — judge-YES rate vs single-shot pipeline (`evaluation/run_agent_eval.py`)

## References

- [Qwen2.5-Coder-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct)
- [Saikrishna2511/qwen-multitask](https://huggingface.co/Saikrishna2511/qwen-multitask)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [CoDocBench](https://github.com/kunpai/codocbench)
- [Spider](https://yale-lily.github.io/spider/)
- [BirdBench](https://bird-bench.github.io/)
- [CodeBLEU](https://arxiv.org/abs/2009.10297)
- [CodeBERTScore](https://arxiv.org/abs/2302.05527)
