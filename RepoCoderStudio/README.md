# RepoCoder Studio

RepoCoder Studio is a bilingual, repository-aware code-generation capstone. It
supports six transformations across natural language, Python and Java, then
adds repository retrieval so generated code can follow project-specific APIs,
constants and business rules.

The submitted project covers:

- **Combined Stage (Stages 1–3):** corpus construction, validation, six-task
  dataset creation, baseline evaluation and completion-only LoRA fine-tuning;
- **Stage 4:** Python/Java repository parsing, FAISS indexing, hybrid retrieval,
  cross-encoder reranking, dependency expansion and retrieval evaluation;
- **Stage 5:** repository and validated-corpus RAG, retrieval gating,
  baseline/fine-tuned × no-RAG/RAG comparisons, output validation, Gradio and
  FastAPI interfaces, and isolated functional-evaluation support.

## Start here

Choose the document that matches what you need:

| Goal | Open |
|---|---|
| Understand the project and results | [`RepoCoderStudio_Implementation_Report.md`](../RepoCoderStudio_Implementation_Report.md) |
| Review the submission quickly | [`START_HERE.md`](START_HERE.md) |
| Reproduce, reopen the UI, or deploy | [`RUNBOOK.md`](RUNBOOK.md) |
| Inspect the original corrected full run | [`notebooks/RepoCoderStudio_Fast_Corrected_Retrain.ipynb`](notebooks/RepoCoderStudio_Fast_Corrected_Retrain.ipynb) |
| Inspect the final RAG-aware extension | [`notebooks/RepoCoderStudio_RAG_Augmented_Retrain.ipynb`](notebooks/RepoCoderStudio_RAG_Augmented_Retrain.ipynb) |

## Canonical submitted models

Two adapters are intentionally retained:

| Adapter | Purpose |
|---|---|
| `RepoCoderStudio_FastCorrected_LoRA_v1_0` | Combined-stage model used for the six-task baseline-versus-fine-tuned evaluation |
| `RepoCoderStudio_RAGAware_LoRA_v1_2` | Final serving model, trained with grounded RAG-formatted examples |

The deployable Gradio/FastAPI path uses
`outputs/adapters/RepoCoderStudio_RAGAware_LoRA_v1_2`.

## Verified headline evidence

- The corrected 20-example-per-task comparison improved five primary task
  metrics and preserved the sixth.
- Python-to-Java compile success improved from **40% to 85%**.
- Stage 4 retrieval achieved **97% recall@5** on the hand-labelled evaluation
  set; cross-encoder reranking reached **0.980 MRR** in the saved ablation.
- RepoBench-R top-3 retrieval reached **0.83 for Python** and **0.90 for Java**.
- The final v1.2 adapter passed the two focused repository-grounding checks:
  exact LedgerFlow email-regex recovery and exact transfer-policy rule recovery.

These claims are backed by machine-readable files in `outputs/evaluation` and
`outputs/reports`. The targeted v1.2 checks demonstrate the corrected RAG
behaviour; they are not presented as a new broad six-task statistical study.

## Project layout

```text
RepoCoderStudio/
├── app/                    FastAPI service and browser UI
├── datasets/               downloaded/cached dataset material
├── notebooks/              full-run and RAG-aware notebooks
├── outputs/                adapters, indexes, evaluation and reports
├── repo_explorer_data/     LedgerFlow and public AWS S3 demo repositories
├── scripts/                indexing, smoke-test and Docker-eval tools
├── src/                    training, generation, retrieval and validation code
├── tests/                  focused unit tests
├── Dockerfile              inference container used for local/GCP deployment
├── docker-compose.yml      local deployment
├── START_HERE.md            short reviewer/operator guide
└── RUNBOOK.md              exact reproduction and deployment sequence
```

## Fastest local deployment

Docker must be installed and running. From this directory:

```bash
cp .env.example .env
docker compose up --build
```

On Windows PowerShell, replace the first command with:

```powershell
Copy-Item .env.example .env
```

Open `http://localhost:8000`, then check
`http://localhost:8000/api/health`. The health response must name
`RepoCoderStudio_RAGAware_LoRA_v1_2` and report real, loaded repository and
corpus indexes.

## Important operating notes

- Run the notebooks in their documented order. The RAG-aware notebook is an
  add-on and intentionally reuses artifacts made by the corrected full run.
- The packaged adapter and indexes allow review, UI launch and deployment
  without retraining.
- Docker functional verification is optional reporting evidence. It does not
  gate model generation, Gradio, FastAPI or Cloud Run deployment.
- The service loads multiple CPU inference models. Cold start and generation
  are slower than a GPU notebook; the runbook therefore uses one concurrent
  request and an extended Cloud Run timeout.
- Do not rename the top-level `RepoCoderStudio` folder when using the supplied
  Colab notebooks; their default Drive path is
  `/content/drive/MyDrive/RepoCoderStudio`.

