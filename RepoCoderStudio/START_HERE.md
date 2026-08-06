# RepoCoder Studio — Start Here

This folder is the consolidated capstone submission through Stage 5. It
contains the source code, cached datasets, two executed notebooks, trained
adapters, repository/corpus indexes, saved evaluation evidence, Gradio UI,
FastAPI application and Docker/GCP deployment files.

## If you are reviewing the project

Follow this order; no GPU run is required:

1. Read [`RepoCoderStudio_Implementation_Report.md`](../RepoCoderStudio_Implementation_Report.md) (one level up, alongside this repo's other top-level docs).
2. Open `notebooks/RepoCoderStudio_Fast_Corrected_Retrain.ipynb` to see the
   Combined Stage, Stage 4 and original Stage 5 execution.
3. Open `notebooks/RepoCoderStudio_RAG_Augmented_Retrain.ipynb` to see the final
   RAG-aware v1.2 correction and its two successful grounding checks.
4. Inspect `outputs/evaluation` and `outputs/reports` for the machine-readable
   evidence behind the report.

## If you only want to demonstrate the UI

Do **not** retrain. Upload this complete folder to Google Drive at exactly:

```text
MyDrive/RepoCoderStudio
```

Open `notebooks/RepoCoderStudio_RAG_Augmented_Retrain.ipynb` in Colab and use a
T4 GPU. If this is a fresh runtime, run Step 1a once and allow the automatic
restart. After reconnection, run from Step 1b onward in order. The training
cell validates and reuses the packaged v1.2 adapter instead of retraining it.
The final cell launches Gradio and prints a new temporary `gradio.live` URL.

## If you want a complete fresh reproduction

Run the two notebooks in this exact order:

1. `RepoCoderStudio_Fast_Corrected_Retrain.ipynb`
2. `RepoCoderStudio_RAG_Augmented_Retrain.ipynb`

The first notebook builds the source-of-truth corpus, evaluation artifacts and
Stage 4/5 indexes. The second consumes those artifacts and trains the final
grounded RAG-aware adapter. Full cell-by-cell directions are in `RUNBOOK.md`.

## If you want to deploy

The final serving identity is:

```text
Base model       : Qwen/Qwen2.5-Coder-0.5B-Instruct
Adapter          : RepoCoderStudio_RAGAware_LoRA_v1_2
Prompt contract  : rag_prompt_contract_v1.2
Training manifest: training_manifest_rag_v1.2
Context budget   : 2000 characters
```

For a local check:

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:8000` and `/api/health`. For GCP Artifact Registry and
Cloud Run, follow Part E of `RUNBOOK.md`; its commands are copyable and use the
same v1.2 adapter and retrieval settings.

## What is optional

- AWS EC2/Docker functional checking is optional and only enriches the report.
- Gradio is optional when deploying the FastAPI browser application.
- The expensive extended/adaptive RAG and external-generation cells can be run
  later without rebuilding the earlier saved stages.

