# RepoCoder Studio — Start Here

This is the consolidated, executed capstone submission for the Combined Stage
(Stages 1–3), Stage 4 and Stage 5. It contains the source code, complete
dataset cache, checkpoints, final LoRA adapter, evaluation outputs, repository
indexes, executed notebook, Gradio interface, FastAPI browser application and
deployment files.

## For mentor review

1. Read `RepoCoderStudio_Implementation_Report.md`.
2. Open `notebooks/RepoCoderStudio_Fast_Corrected_Retrain.ipynb` to inspect
   the executed cells and outputs.
3. Review the machine-readable evidence under `outputs/evaluation` and
   `outputs/reports`.
4. Use `RUNBOOK.md` only when reproducing the full Colab/Docker workflow.

## To reopen the Gradio demonstration

Place this folder at:

```text
/content/drive/MyDrive/RepoCoderStudio
```

Run the dependency installation and environment verification cells in a fresh
Colab runtime, then run the final Gradio launch cell. The serving loader uses
the saved adapter and Stage 4/5 indexes; it does not retrain the model or rerun
evaluation. In an already-running notebook session, the same cell reuses the
models and indexes already in memory.

## To build the deployable application

The Docker build context must be this project root. Required runtime artifacts
are already present under:

```text
outputs/adapters/
outputs/approved_corpus/
outputs/corpus_index/
outputs/repositories/
repo_explorer_data/
```

Build and test locally:

```bash
docker build -t repocoder-studio .
docker run --rm -p 8000:8000 --name repocoder-studio repocoder-studio
```

Then open `http://localhost:8000` and verify
`http://localhost:8000/api/health`.

For GCP Cloud Run, push the image to Artifact Registry and deploy it with
adequate memory and startup time for the baseline model, LoRA model, embedding
model and cross-encoder. The container already honours Cloud Run's `PORT`
environment variable and runs as a non-root user.

## Canonical model

```text
Base model: Qwen/Qwen2.5-Coder-0.5B-Instruct
Adapter: outputs/adapters/RepoCoderStudio_FastCorrected_LoRA_v1_0
```

Do not replace the canonical adapter with an intermediate checkpoint.
