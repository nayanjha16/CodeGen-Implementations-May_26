# CodeGen: Evaluating and Enhancing Code Language Models with RAG

**Program Synthesis · Documentation Generation · SQL Generation · RAG · Language Extension**

AIML PGCP Capstone — Group 39, Batch 26 (TalentSprint / Accenture)
Mahin Nandipa · Abhinaya Thavishi · Ashu Bagul
Mentors: Pawan Baswani, Nayan Anand · Supervisor: Prof. Anil Neelkanti

## Live demo

**[tableware-exit-cosmos.ngrok-free.dev](https://tableware-exit-cosmos.ngrok-free.dev)**

This is a free-tier ngrok tunnel, so the URL rotates every time the tunnel is restarted —
if the link above is dead, someone needs to re-run `04_checkpoint4_deployment.ipynb` and swap
in the fresh URL it prints. (A free ngrok account gets one reserved static subdomain, which
would make this link permanent — worth setting up before final submission.)

## What this is

An end-to-end evaluation and enhancement of `Salesforce/codegen-350M-multi` (350M params)
against real software-engineering tasks — program synthesis, documentation generation, commit
message generation, PL-to-PL translation, and natural-language-to-SQL — plus a full
Retrieval-Augmented Generation pipeline (dense FAISS + AST + hybrid retrieval) and a fine-tune
extending the model to Rust, a language absent from its original training data. Four model
tiers are compared throughout: the small LM baseline, the fine-tuned Rust model, an upper-bound
LLM (Claude Sonnet 4, with automatic GPT-5 fallback), and the LLM augmented with RAG. The whole
system is deployed behind a FastAPI backend with a Streamlit frontend, containerized with Docker.
See `docs/architecture.md` for diagrams of how all four checkpoints connect end to end.

## Repository layout

```
codegen-rag-capstone/
├── configs/                       # All tunables live here — no magic numbers in code
│   ├── config.yaml                # project/paths/base model/upper-bound LLM/logging
│   ├── data_config.yaml           # dataset sources, split ratios, DB archive URLs
│   ├── model_config.yaml          # per-task generation params, embeddings, LoRA
│   └── training_config.yaml       # Checkpoint 1 (subset/LoRA) + Checkpoint 2 (full) configs
├── src/codegen_rag/
│   ├── config.py                  # typed Settings loader (pydantic) — single source of truth
│   ├── utils/                     # logging, Colab/local env bootstrap, IO helpers, seeding
│   ├── data/                      # downloaders, cleaners/preprocessors, tokenizer utils, Datasets
│   ├── models/                    # codegen-350M-multi wrapper, GenerationConfig, upper-bound LLM client
│   ├── tasks/                     # program synthesis, doc-gen, commit-msg, PL-to-PL translation
│   ├── sql/                       # schema introspection/injection, Spider+BirdBench loaders, SQL task
│   ├── rag/                       # FAISS index, AST retrieval, hybrid fusion, pipeline, top-K experiments,
│   │                               #   RAGAugmentedTask adapter (retrieval-augmented tiers -> comparison_table.csv)
│   ├── evaluation/                # CodeBLEU/BERTScore/execution-accuracy metrics, Evaluator, charts
│   ├── training/                  # LoRA/full fine-tuning trainer + checkpoint resume + disk-safe pruning
│   ├── api/                       # FastAPI app: /generate /document /translate /sql /rag /score /score_sql
│   └── app/                       # Streamlit UI (live per-query scoring, % formatting) + its API client
├── notebooks/
│   ├── 01_checkpoint1_foundation_and_docgen.ipynb
│   ├── 02_checkpoint2_sql_and_full_finetune.ipynb
│   ├── 03_checkpoint3_rag_pipeline.ipynb
│   └── 04_checkpoint4_deployment.ipynb
├── scripts/
│   ├── run_checkpoint1_eval.py    # CLI equivalent of notebook 1
│   └── serve_api.py               # launch FastAPI without Colab
├── tests/                         # 164-test pytest suite — no GPU, network, or model weights needed
├── docker/                        # Dockerfile.api, Dockerfile.streamlit
├── docker-compose.yml
├── docs/architecture.md           # Mermaid system + sequence diagrams
├── requirements.txt
└── pyproject.toml
```

## Project status (checkpoint tracker)

| Checkpoint | Scope | Status |
|---|---|---|
| **1** (Week 2) | Environment, data pipeline, 4 baseline tasks, Rust LoRA on 500-sample subset | **Complete — run** |
| **2** (Week 5) | Full Spider + BirdBench SQL generation, full-corpus Rust fine-tune, TensorBoard/W&B, checkpoint pruning | **Complete — run** |
| **3** (Week 8) | FAISS + AST + hybrid RAG, top-K/dynamic-top-K experiments, Claude Sonnet 4 comparison, charts/report | **Complete — run** |
| **4** (Week 11) | FastAPI (7 endpoints), Streamlit (5 tabs, live scoring), Docker, architecture docs, public demo | **Complete — deployed** |

All four checkpoints have been run end to end in Colab with a GPU and live API keys — the
`comparison_table.csv` results (including the `fine_tuned_rag` tier, see below) come from real
runs, not placeholders.

## Gaps closed beyond the original four checkpoints

An audit against the official project brief found two issues, both now fixed and verified:

- **Checkpoint 4's "fine-tuned model into the RAG system" requirement had no working path.**
  The four-tier comparison function was silently reusing the base model's generate function
  inside its fine-tuned-model branch, and the RAG comparison scored CodeBLEU into a table
  separate from `comparison_table.csv`, so even a correct run never reached the actual
  deliverable. Fixed with an explicit `fine_tuned_generate_fn` parameter (logged warning if
  omitted) and a new `RAGAugmentedTask` adapter that lets any task be retrieval-augmented and
  scored through the same `Evaluator` path as every other tier. The `fine_tuned_rag` row in the
  4-tier comparison table now carries its own real, distinct number.
- **Spider vs. Spider 2.0 citation mismatch.** The brief's reference link points to Spider 2.0;
  the code (verified in `src/codegen_rag/data/downloaders.py`) downloads and evaluates against
  the classic 2018 Spider benchmark, matching this README's own citation below. Documented as a
  near-certain brief reference-list error rather than an implementation gap.

Six regression tests cover the first fix; the suite went from 147 to 153 to 164 as this work and
the live-scoring feature below were added — all passing.

## Live per-query scoring + percentage formatting

Every metric in this project (`exact_match`, `codebleu`, `bertscore_f1`, `execution_accuracy`)
is now shown as a percentage everywhere it's displayed, matching common capstone report
conventions. Beyond the pre-computed dataset-level baseline numbers, the Streamlit demo can also
score **whatever you just generated**: paste an optional reference solution (or gold SQL query)
next to any task's input, and `POST /score` / `POST /score_sql` return instant
CodeBLEU/BERTScore/exact-match/execution-accuracy for that one generation — not a dataset
average, a live n=1 sanity check against your own reference.

## How the checkpoints connect

Each notebook is additive and shares the same `Settings` object, model wrapper, and results
directory, so the pipeline is genuinely one system rather than four disconnected demos:

1. **Checkpoint 1** downloads CoDocBench + a Rust subset, evaluates the base model on four
   tasks, and produces the first LoRA-adapted Rust checkpoint (saved under `checkpoints/rust_lora_subset`).
2. **Checkpoint 2** downloads Spider + BirdBench (with their SQLite database archives),
   evaluates SQL generation with schema injection and real execution accuracy, and replaces the
   subset Rust adapter with a full-corpus fine-tune (`checkpoints/rust_full`), reusing the exact
   same `LoRAFineTuner`/`CheckpointManager` classes with disk-space-safe pruning.
3. **Checkpoint 3** embeds a 2000+ sample corpus (CodeParrot + CoDocBench) with the same
   `CodeGenModel.embed()` used for tasks, builds FAISS + AST indexes, sweeps Top-K/strategy
   combinations, and runs the four-tier comparison — loading the Checkpoint 2 Rust checkpoint
   into the RAG pipeline via `CheckpointManager.find_resume_point("best")` and, since the gap fix
   above, actually generating with that fine-tuned model rather than silently falling back to
   the base model.
4. **Checkpoint 4** wires the same task modules and the same saved FAISS/AST indexes behind
   FastAPI, with Streamlit as a thin HTTP client — nothing is reimplemented, the API layer just
   calls the identical `ProgramSynthesisTask`, `SQLGenerationTask`, and `RAGPipeline` classes
   used in the notebooks — and is exposed publicly via ngrok (see Live demo above).

## Quickstart (Google Colab — recommended)

1. Push this repository to GitHub (or upload the folder to Google Drive).
2. Open `notebooks/01_checkpoint1_foundation_and_docgen.ipynb` in Colab, set `REPO_URL`, Runtime
   > Change runtime type > **GPU**, then **Runtime > Run all**.
3. Repeat for `02_...ipynb`, `03_...ipynb`, `04_...ipynb` in order — each one assumes the
   previous checkpoint's Drive folder (`checkpoints/`, `data/processed/`, `faiss_index/`,
   `results/`) already exists, and everything is idempotent so re-running any notebook is safe.
4. Notebook 4 prints a public ngrok URL at the end — that's the link at the top of this README.

## Quickstart (local / any GPU box)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python scripts/run_checkpoint1_eval.py --install-deps --eval-n 100
```

## Running the full system with Docker

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # optional, only needed for LLM/RAG endpoints
docker compose up --build
# API:       http://localhost:8000/docs
# Streamlit: http://localhost:8501
```

The API container mounts `./data`, `./checkpoints`, `./faiss_index`, and `./results` — run the
notebooks (or `scripts/run_checkpoint1_eval.py`) at least once first so those directories are
populated, since the containers serve trained artifacts rather than training them.

## Running the tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

The test suite (164 tests) covers preprocessing, metrics, SQL schema injection/execution
accuracy, FAISS/AST/hybrid retrieval, the RAG pipeline (including the `RAGAugmentedTask`
adapter), the top-K experiment runner, chart generation, the FastAPI endpoints — including
`/score` and `/score_sql` — (via `TestClient` + dependency overrides), and the Streamlit API
client — using fakes/mocks throughout (`FakeCodeGenModel`, `FakeAPIModel`,
`app.dependency_overrides`) so it needs **no** torch, GPU, network access, downloaded model
weights, or a running server. Runs in under 5 seconds.

## Secrets

Set these as environment variables (locally/Docker) or Colab secrets
(`google.colab.userdata`):

- `ANTHROPIC_API_KEY` — Claude Sonnet 4 upper-bound comparison and `/rag?use_llm=true`
- `OPENAI_API_KEY` — fallback upper-bound LLM (GPT-5 / GPT-4o)
- `WANDB_API_KEY` — optional, only if `logging.wandb.enabled: true` in `configs/config.yaml`
- `NGROK_AUTHTOKEN` — required to expose the Checkpoint 4 demo publicly (free account, see
  Live demo above)

## Team roles

Per the project proposal, all three members share responsibility across research,
implementation, evaluation, deployment, documentation, and testing — checkpoint ownership is
collective, not per-person. Individual contribution detail is documented separately in the
capstone report's Team & Individual Contributions section.

## References

CodeGen (Nijkamp et al., 2022) · Codex (Chen et al., 2021) · CodeBERT (Feng et al., 2020) ·
CoDocBench (Pal et al., 2024) · Spider (Yu et al., 2018) · BirdBench (Li et al., 2024) ·
RAG (Lewis et al., 2020) · ReACC (Lu et al., 2021) · AST retrieval (Jiang et al., 2023) ·
CodeBLEU (Ren et al., 2020) · CodeBERTScore (Zhou et al., 2023) · pass@k (Chen et al., 2021)
