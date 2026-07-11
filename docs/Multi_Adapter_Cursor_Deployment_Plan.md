# Deployment Plan: Multi-Adapter AI Service for Cursor IDE

## Objective

Deploy a single CodeGen base model with three LoRA adapters and expose an
**OpenAI-compatible** API that:

1. Detects the user's intent from natural language (no task keys required).
2. Uses schema already present in the prompt (MVP).
3. Prefixes the prompt with the training task tag.
4. Hot-swaps the matching LoRA adapter.
5. Returns the generated response for Cursor / any OpenAI-compatible client.

**Implementation lives in:** [`hf-deploy/`](../hf-deploy/)

------------------------------------------------------------------------

# Decisions (MVP / Capstone)

| Topic | Decision |
| --- | --- |
| Schema | Included in the user prompt |
| Multi-step asks | Not supported (one intent per request) |
| Adapter selection | Best adapter for `manifest.yaml` → `checkpoint_version` (task root preferred) |
| Adapter switching | PEFT `set_adapter` hot-swap |
| Latency | Acceptable for demo |
| Cursor API | OpenAI-compatible `POST /v1/chat/completions` |
| Intent classifier | Rules fast-path + MiniLM embeddings; low confidence → clarify |

------------------------------------------------------------------------

# High-Level Architecture

``` text
Cursor IDE (OpenAI-compatible base URL)
    │
POST /v1/chat/completions
    │
FastAPI Gateway (local or Hugging Face Space)
    │
Intent Classifier (rules → embeddings → clarify)
    │
Prompt Builder (Task: <intent>)
    │
Adapter Router (set_adapter)
    │
CodeGen Base + Selected LoRA
    │
Response (+ codegen_routing metadata)
```

------------------------------------------------------------------------

# Components

## 1. Cursor Integration

Configure Cursor with:

- Base URL: `http://localhost:8000/v1` (or your Space URL + `/v1`)
- Model: `codegen-multi-adapter`

Example body:

``` json
{
  "model": "codegen-multi-adapter",
  "messages": [
    {
      "role": "user",
      "content": "Write a SQL query to list customers.\n\nSchema:\ncustomers(id, name)\n\nSQL:"
    }
  ]
}
```

Optional override: `"intent": "text2sql"` skips classification.

------------------------------------------------------------------------

## 2. Intent Classifier

Supported tasks:

- TEXT2SQL (`text2sql`)
- SQL2NOSQL (`sql2nosql`)
- NOSQL2DOC (`nosql2doc`)
- CLARIFY (confidence below threshold)

Examples the classifier handles:

- "write a sql query to …"
- "generate a sql query …"
- "convert sql query to nosql …"
- "generate documentation …"

Output (also returned as `codegen_routing`):

``` json
{
  "intent": "sql2nosql",
  "confidence": 0.91,
  "method": "rules"
}
```

------------------------------------------------------------------------

## 3. Schema Retrieval

**MVP:** schema is part of the prompt. No server-side project filesystem access.

Future: Cursor-side tool extracts schema and injects it into the message.

------------------------------------------------------------------------

## 4. Prompt Builder

Adds the training prefix when missing:

``` text
Task: text2sql

<user content including schema>
```

------------------------------------------------------------------------

## 5. Adapter Router

| Intent | Adapter |
| --- | --- |
| text2sql | text2sql |
| sql2nosql | sql2nosql |
| nosql2doc | nosql2doc |

Load base once; `load_adapter` ×3; `set_adapter(intent)` per request.

Best path for version `v3`:

`models/checkpoints/v3/<task>/` (falls back to highest `checkpoint-*`).

------------------------------------------------------------------------

## 6. Hugging Face Artifacts

Publish selected version only (see `hf-deploy/publish/push_adapters.py`):

- `codegen-350M-text2sql-lora`
- `codegen-350M-sql2nosql-lora`
- `codegen-350M-nosql2doc-lora`
- Space / API: `codegen-multi-adapter-api`

Pin version in `hf-deploy/manifest.yaml` → `checkpoint_version`.

------------------------------------------------------------------------

## 7. Project Structure

``` text
hf-deploy/
  manifest.yaml
  requirements.txt
  Dockerfile
  publish/push_adapters.py
  hf_deploy/
    api/app.py
    classifier/
    adapters/
    prompt/
  tests/
```

------------------------------------------------------------------------

# API Flow

``` text
Receive /v1/chat/completions
      │
Intent Detection (or override)
      │
Clarify? ──yes──► clarification message
      │ no
Build Task-prefixed prompt
      │
set_adapter + Generate
      │
Return OpenAI-style response
```

------------------------------------------------------------------------

# Development Roadmap

## Phase 1 — Done in `hf-deploy/`

- Manifest + best-adapter resolver
- Intent classifier (rules + embeddings)
- Multi-adapter router
- OpenAI-compatible FastAPI
- Publish script (dry-run / upload)
- Unit tests (no GPU required)

## Phase 2

- Publish v3 adapters to Hub
- Deploy Space / run local server for Cursor

## Phase 3

- Validation layer (SQL / Mongo / docs)
- Streaming responses
- Metrics / feedback loop

------------------------------------------------------------------------

# Why This Architecture

- One base model in memory
- Small adapter storage
- Natural-language routing (no task keys)
- OpenAI-compatible → easy Cursor wiring
- Version pin via manifest
- Modular and demo-friendly for a capstone
