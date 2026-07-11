# Hugging Face Multi-Adapter Deployment

Capstone package: **Salesforce/codegen-350M-multi** + three LoRA adapters, with an OpenAI-compatible FastAPI gateway.

- Classifies natural-language intent (no task keys like `text2sql` required)
- Hot-swaps the matching LoRA adapter
- Expects **schema inside the user prompt** (MVP)

## What is already on Hugging Face

These are **model repos** (adapter weights only), not a running API:

| Task | Hub repo |
| --- | --- |
| text2sql | https://huggingface.co/care2achieve/codegen-350M-text2sql-lora |
| sql2nosql | https://huggingface.co/care2achieve/codegen-350M-sql2nosql-lora |
| nosql2doc | https://huggingface.co/care2achieve/codegen-350M-nosql2doc-lora |

The **API server** lives in this folder. You run it locally, or optionally deploy it as a Hugging Face Space.

## Important: local uvicorn ≠ Hugging Face Space

```bash
export HF_DEPLOY_ADAPTER_SOURCE=hub
export HF_ORG=care2achieve
PYTHONPATH=hf-deploy uvicorn hf_deploy.api.app:app --host 0.0.0.0 --port 8000
```

This command:

| Does | Does not |
| --- | --- |
| Starts the API on **your machine** (`localhost:8000`) | Create or start a Hugging Face Space |
| Can download adapters from the Hub | Host anything on `*.hf.space` |

**Hub** here means “load weights from Hugging Face.”  
**Space** means “host the API on Hugging Face’s servers.”

---

## Run the API

### A. Local weights (fastest for Cursor)

Uses `models/checkpoints/v3/` (`adapter_source: local` in `manifest.yaml`):

```bash
pip install -r hf-deploy/requirements.txt
cd /path/to/CodeGen-Implementations-May_26
PYTHONPATH=hf-deploy uvicorn hf_deploy.api.app:app --host 0.0.0.0 --port 8000
```

### B. Local API + Hub weights

Same local server, but adapters are pulled from `care2achieve/codegen-350M-*-lora`:

```bash
export HF_DEPLOY_ADAPTER_SOURCE=hub
export HF_ORG=care2achieve
PYTHONPATH=hf-deploy uvicorn hf_deploy.api.app:app --host 0.0.0.0 --port 8000
```

First start downloads the base model + three adapters.

### Endpoints (A or B)

| | |
| --- | --- |
| Health | http://localhost:8000/health |
| Chat | `POST http://localhost:8000/v1/chat/completions` |
| Models | `GET http://localhost:8000/v1/models` |
| Cursor base URL | `http://localhost:8000/v1` |
| Cursor model | `codegen-multi-adapter` |

### C. Hugging Face Space (hosted API)

Space id: **`care2achieve/codegen-multi-adapter`**

```bash
PYTHONPATH=hf-deploy python hf-deploy/publish/push_space.py --dry-run
PYTHONPATH=hf-deploy python hf-deploy/publish/push_space.py
```

After the Docker build finishes:

| | |
| --- | --- |
| Space page | https://huggingface.co/spaces/care2achieve/codegen-multi-adapter |
| API base | `https://care2achieve-codegen-multi-adapter.hf.space/v1` |
| Cursor model | `codegen-multi-adapter` |

**Note (2026):** Hugging Face requires **PRO** to host Docker/Gradio Spaces on free CPU
([subscribe](https://huggingface.co/pro)). Without PRO, `push_space.py` returns HTTP 402.

Until PRO is enabled, use **Option A or B** (local API). Adapters are already on the Hub;
only the *hosted* API needs a Space.

---

## Intents

| User says (examples) | Intent | Adapter |
| --- | --- | --- |
| write / generate a SQL query | `text2sql` | text2sql |
| convert SQL to Mongo / NoSQL | `sql2nosql` | sql2nosql |
| generate documentation | `nosql2doc` | nosql2doc |

Ambiguous prompts return a clarification message (no generation).  
Optional request field `"intent": "text2sql"` skips the classifier.

## Example request

```bash
curl http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "codegen-multi-adapter",
    "messages": [
      {
        "role": "user",
        "content": "Write a SQL query to list customer names.\n\nSchema:\ncustomers(id, name)\n\nSQL:"
      }
    ]
  }'
```

Response includes `codegen_routing` (intent, confidence, method).

## Config

| Setting | Where | Notes |
| --- | --- | --- |
| `checkpoint_version` | `manifest.yaml` | e.g. `v3` |
| `adapter_source` | `manifest.yaml` or `HF_DEPLOY_ADAPTER_SOURCE` | `local` or `hub` |
| `HF_ORG` | env / `hub.org` | `care2achieve` |
| `HF_TOKEN` | repo `.env` | needed to **publish**; public adapters load without it |

## Publish adapters again

```bash
PYTHONPATH=hf-deploy python hf-deploy/publish/push_adapters.py --dry-run
PYTHONPATH=hf-deploy python hf-deploy/publish/push_adapters.py --version v3
```

Uploads to `care2achieve/codegen-350M-*-lora` with a Hub-valid model card.

## Layout

```text
hf-deploy/
  manifest.yaml
  requirements.txt
  Dockerfile                 # for Space (Option C)
  .env.example
  publish/push_adapters.py
  hf_deploy/
    api/app.py               # OpenAI-compatible FastAPI
    classifier/              # rules + embeddings
    adapters/                # resolve + PEFT hot-swap
    prompt/
  tests/
```

## Tests

```bash
PYTHONPATH=hf-deploy pytest hf-deploy/tests -q
```

Unit tests do not need GPU or model weights.
