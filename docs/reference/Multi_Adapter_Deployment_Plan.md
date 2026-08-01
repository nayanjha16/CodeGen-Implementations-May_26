# Multi-Adapter Deployment Plan

Single **CodeGen-350M-multi** base model with three LoRA adapters, exposed as an **OpenAI-compatible** API for the AI Database Agent and Cursor.

**Implementation:** [`fastapi-deploy/`](../../fastapi-deploy/) (`codegen_api` package)  
**Production URL:** `https://codegen-api-161349047936.asia-south2.run.app`  
**Active version:** **v3** (`fastapi-deploy/manifest.yaml` → `checkpoint_version: v3`)

**Related:** [fastapi-deploy/README.md](../../fastapi-deploy/README.md) · [evaluation-and-deploy-runbook.md](evaluation-and-deploy-runbook.md) · [version-tracker.md](version-tracker.md)

---

## Objective

1. Load one base model + three LoRA adapters (text2sql, sql2nosql, nosql2doc).
2. Route each request to the correct adapter (classifier or explicit `intent`).
3. Prefix prompts with the training task tag (`Task: text2sql`, etc.).
4. Serve `/v1/chat/completions` for the agent and any OpenAI client.

---

## Architecture

```text
Client (agent / Cursor / curl)
    │
POST /v1/chat/completions  (+ optional "intent" override)
    │
FastAPI — fastapi-deploy/codegen_api/api/app.py
    │
Intent classifier (rules → embeddings → clarify)
    │
Prompt builder (Task: <intent>)
    │
Adapter router — PEFT set_adapter hot-swap
    │
CodeGen-350M-multi + selected LoRA
    │
OpenAI-style response (+ codegen_routing metadata)
```

**Agent path:** `agent/clients/codegen_client.py` → Cloud Run URL from `agent/.env` (`CODEGEN_API_URL`). The agent passes **explicit `intent`** so routing is deterministic during demos.

---

## MVP decisions

| Topic | Decision |
|-------|----------|
| Deploy target | **Google Cloud Run** (`asia-south2`) |
| Package | `fastapi-deploy/codegen_api` |
| Adapter weights | Loaded from **Hub** at container start (`adapter_source: hub` on deploy) |
| Schema | Client includes schema in the user message (agent schema tool builds DDL) |
| Multi-step | One intent per request |
| Classifier | Rules fast-path + MiniLM embeddings; low confidence → clarify |
| Production adapters | LoRA **v3** on `codegenstudio` Hub |

---

## Hub repositories

| Task | Hub repo |
|------|----------|
| text2sql | `codegenstudio/codegen-350M-text2sql-lora` |
| sql2nosql | `codegenstudio/codegen-350M-sql2nosql-lora` |
| nosql2doc | `codegenstudio/codegen-350M-nosql2doc-lora` |

Publish after training:

```powershell
$env:PYTHONPATH = "fastapi-deploy"
python fastapi-deploy/publish/push_adapters.py --version v3 --dry-run
python fastapi-deploy/publish/push_adapters.py --version v3
```

---

## Project layout

```text
fastapi-deploy/
  manifest.yaml              # checkpoint_version, adapters, generation, classifier
  Dockerfile
  entrypoint.sh
  publish/push_adapters.py
  infra/cloudrun/deploy.py   # cross-platform Cloud Run deploy
  codegen_api/
    api/app.py               # FastAPI + /v1/chat/completions
    classifier/
    adapters/router.py       # PEFT hot-swap
    prompt/builder.py
  tests/
```

---

## API usage

### Health

```text
GET /health
```

Expect `"status":"ok"`, `"checkpoint_version":"v3"`, adapters loaded. Cold start after idle can take **45–60+ s** (`CLOUD_RUN_MIN_INSTANCES=0`).

### Chat completions

```text
POST /v1/chat/completions
```

```json
{
  "model": "codegen-text2sql",
  "intent": "text2sql",
  "messages": [
    {
      "role": "user",
      "content": "Schema:\nCREATE TABLE \"Customer\" (...);\n\nQuestion: How many customers?"
    }
  ]
}
```

Model IDs: `codegen-text2sql`, `codegen-sql2nosql`, `codegen-nosql2doc`, or `codegen-multi-adapter`.

### Cursor IDE (optional)

- Base URL: `<cloud-run-url>/v1`
- Model: `codegen-multi-adapter`

---

## Deploy flow

1. Train LoRA → checkpoints under `models/checkpoints/vN/` (see [version-tracker.md](version-tracker.md) for v1–v3 hyperparameters)
2. Eval on gold set — see [version-tracker.md](version-tracker.md)
3. Publish adapters to Hub (`push_adapters.py`)
4. Set `checkpoint_version: vN` in `manifest.yaml`
5. Deploy: `python fastapi-deploy/infra/cloudrun/deploy.py`
6. Verify `/health` and a sample `/v1/chat/completions` call
7. Point agent `CODEGEN_API_URL` at the service URL

Details: [evaluation-and-deploy-runbook.md](evaluation-and-deploy-runbook.md) Phase 9–10.

---

## Integration with AI Database Agent

| Agent component | API role |
|-----------------|----------|
| `tools/schema_tool.py` | Builds schema DDL in prompt (no server-side schema DB) |
| `clients/codegen_client.py` | HTTP to `/v1/chat/completions` with `intent` |
| `tools/execution_tool.py` | Runs SQL against TEND Postgres / Mongo |
| `orchestrator/` (Ollama) | Intent fallback + NL summary — **does not** generate SQL |

Agent never loads torch/PEFT locally; all generation goes through Cloud Run.

---

## Status

| Phase | Status |
|-------|--------|
| Multi-adapter FastAPI (`codegen_api`) | Done |
| Intent classifier + prompt builder | Done |
| Hub publish script | Done |
| Cloud Run deploy (`deploy.py`) | Done |
| LoRA v3 in production | Done |
| Agent wired to Cloud Run | Done |
| Web UI demo (`agent/web`) | Done |

Optional later: streaming, validation middleware, `MIN_INSTANCES=1` for faster cold start.
