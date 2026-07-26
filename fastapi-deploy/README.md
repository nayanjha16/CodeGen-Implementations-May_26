# fastapi-deploy (codegen-api)

A self-contained **FastAPI** serving package for the fine-tuned CodeGen stack:
**`Salesforce/codegen-350M-multi`** + three LoRA adapters, behind an
**OpenAI-compatible** API. This is the **Capstone FastAPI Tool** that the
AI Database Agent (see `agent/doc/agent.md`) calls to generate SQL / NoSQL / docs.

- Classifies the natural-language request (no task keywords required)
- Hot-swaps the matching LoRA adapter (one base model in memory)
- Expects the **schema inside the user prompt** (MVP)
- Works with Cursor / any OpenAI client via `/v1/chat/completions`

---

## Folder naming (important)

Two folders, two different roles:

| Folder | Role |
| --- | --- |
| `fastapi-deploy/` (hyphen) | The **deployment bundle** — Dockerfile, manifest, requirements, infra, publish, tests, this README. |
| `fastapi-deploy/codegen_api/` (underscore) | The **importable Python package** — the actual app code. |

Python import names cannot contain hyphens, so the package uses an underscore.
That is why the run target is `codegen_api.api.app:app`.

```text
fastapi-deploy/
  manifest.yaml              # model + adapter + generation + classifier config
  requirements.txt
  entrypoint.sh              # container launcher (runs INSIDE the Linux image)
  Dockerfile                 # single image for Cloud Run / local Docker
  cloudbuild.yaml            # Cloud Build definition
  .dockerignore
  .gitignore
  .env                       # local app config, auto-loaded (gitignored)
  publish/
    push_adapters.py         # push ANY version of adapters to the Hub
  infra/cloudrun/
    deploy.py                # single cross-platform deploy (Windows/macOS/Linux)
    env.example              # copy to deploy.env (gitignored)
  codegen_api/
    __init__.py              # paths, INTENTS, CLARIFY_INTENT
    config.py                # load_manifest + CODEGEN_* env overrides
    classifier/              # rules fast-path + optional embeddings
    prompt/                  # Task: tag prompt builder + clarify message
    adapters/                # checkpoint resolution + PEFT hot-swap router
    api/                     # OpenAI-compatible schemas + FastAPI app
  tests/
    test_classifier.py
```

---

## Adapters on the Hugging Face Hub

Cloud Run loads adapters from **`codegenstudio`** at container startup (no
weights baked into the Docker image). Hub repo names are **fixed**; publishing a
new training run **updates the same repos** with new weights.

| Task | Hub repo |
| --- | --- |
| text2sql | `codegenstudio/codegen-350M-text2sql-lora` |
| sql2nosql | `codegenstudio/codegen-350M-sql2nosql-lora` |
| nosql2doc | `codegenstudio/codegen-350M-nosql2doc-lora` |

The active checkpoint version (e.g. v2, v3) is tracked in `manifest.yaml`
(`checkpoint_version`) and shown in `/health`. After you fine-tune a new version,
follow [After fine-tuning: publish and redeploy](#after-fine-tuning-publish-and-redeploy).

---

## Understanding the API

### Root URL (`GET /`) — landing page, not chat

Opening the Cloud Run URL in a browser (e.g. `https://codegen-api-….run.app/`)
returns a small JSON index — **this is normal**:

```json
{
  "model": "codegen-multi-adapter",
  "docs": "/docs",
  "health": "/health",
  "openai_base_url": "/v1",
  "chat": "/v1/chat/completions"
}
```

| Path | Purpose |
| --- | --- |
| `/docs` | Swagger UI — try `POST /v1/chat/completions` in the browser |
| `/health` | Service status, loaded adapters, `checkpoint_version` |
| `/v1/chat/completions` | **Inference** — must be called with `POST` + JSON body |

### OpenAI-compatible chat (`POST /v1/chat/completions`)

This API uses the **OpenAI Chat Completions** shape (not custom routes like
`/generate/sql` from the agent spec). Any OpenAI client — Cursor, Python SDK,
the future Database Agent — uses base URL `<service-url>/v1`.

**Request flow:**

```
Client POST /v1/chat/completions
    → read latest user message from messages[]
    → classifier picks task (or intent override)
    → hot-swap LoRA adapter (text2sql | sql2nosql | nosql2doc)
    → return OpenAI-style choices[].message.content
```

**Classifier routing** (when `intent` is not set):

1. `Task: <intent>` tag at the start of the message (training format)
2. Regex keyword rules (e.g. “write sql”, “convert to mongo”)
3. Embedding similarity fallback
4. If confidence is too low → **clarify** message asking the user to specify the task

**Agent / production tip:** pass `"intent": "text2sql"` (or `"model": "codegen-text2sql"`)
so routing is deterministic and the classifier never returns clarify.

### Schema goes inside the user message

There is **no separate `schema` JSON field**. Put schema, question, and SQL/NoSQL
context in `messages[].content`, same as training and eval:

```text
Task: text2sql

Schema:
CREATE TABLE singer (
    singer_id REAL PRIMARY KEY,
    name TEXT,
    ...
);

Question:
How many singers do we have?
```

The API adds the `Task:` prefix automatically when you pass `"intent": "text2sql"`.

### Example request (Cloud Run or local)

**bash:**

```bash
curl -X POST "https://codegen-api-161349047936.asia-south2.run.app/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "codegen-text2sql",
    "intent": "text2sql",
    "messages": [
      {
        "role": "user",
        "content": "Schema:\nCREATE TABLE singer (singer_id REAL PRIMARY KEY, name TEXT);\n\nQuestion: How many singers do we have?"
      }
    ]
  }'
```

**PowerShell:**

```powershell
curl.exe -X POST "https://codegen-api-161349047936.asia-south2.run.app/v1/chat/completions" `
  -H "Content-Type: application/json" `
  -d '{\"model\":\"codegen-text2sql\",\"intent\":\"text2sql\",\"messages\":[{\"role\":\"user\",\"content\":\"Schema:\nCREATE TABLE singer (...);\n\nQuestion: How many singers?\"}]}'
```

The response includes `codegen_routing` (intent, confidence, adapter id) for debugging.

---

## Run locally

Adapter source is `local` by default (uses `models/checkpoints/v2/`).

### Windows PowerShell

```powershell
cd C:\Users\Bhavani\Documents\Codegen\Latest\CodeGen-Implementations-May_26
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH = "fastapi-deploy"
uvicorn codegen_api.api.app:app --host 0.0.0.0 --port 8000
```

### macOS / Linux

```bash
pip install -r fastapi-deploy/requirements.txt
cd /path/to/CodeGen-Implementations-May_26
PYTHONPATH=fastapi-deploy uvicorn codegen_api.api.app:app --host 0.0.0.0 --port 8000
```

To load from the Hub instead of local files:

```
CODEGEN_ADAPTER_SOURCE=hub   HF_ORG=codegenstudio
```

### Endpoints

| | |
| --- | --- |
| Landing | http://localhost:8000/ |
| Interactive docs | http://localhost:8000/docs |
| Health | http://localhost:8000/health |
| Chat | `POST http://localhost:8000/v1/chat/completions` |
| Models | `GET http://localhost:8000/v1/models` |
| Cursor base URL | `http://localhost:8000/v1` |
| Cursor model | `codegen-multi-adapter` |

### Example request

```bash
curl http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
      {"role": "user", "content": "Write a SQL query to list customer names.\n\nSchema:\ncustomers(id, name)\n\nSQL:"}
    ]
  }'
```

The response includes a `codegen_routing` block (intent, confidence, adapter).
Pass `"intent": "text2sql"` to skip the classifier.

---

## Deploy to Google Cloud Run

HTTPS is included automatically (`*.run.app`). The container pulls adapters from
the Hub at startup — see [After fine-tuning: publish and redeploy](#after-fine-tuning-publish-and-redeploy)
when you promote a new checkpoint version. **One deploy script works on every OS.**

### 0. One-time prerequisites

1. Install the Google Cloud CLI:
   - **Windows:** `winget install Google.CloudSDK` (or the installer at
     https://cloud.google.com/sdk/docs/install)
   - **macOS:** `brew install --cask google-cloud-sdk`
2. `gcloud auth login`
3. Enable the APIs (once per project):

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

### 1. Set your project (once)

`deploy.env` is already created for your project
(`project-27004230-e72b-42bc-8ed`, region `asia-south2`). It is gitignored.
On a new machine, copy `env.example` to `deploy.env` and set `GCP_PROJECT_ID`.

### 2. Deploy (same command everywhere)

```bash
python fastapi-deploy/infra/cloudrun/deploy.py
```

The script: creates the Artifact Registry repo (if missing) → builds the image
via Cloud Build → deploys to Cloud Run → prints the HTTPS URL. Save that URL as
`CLOUD_RUN_SERVICE_URL` in `deploy.env`. Use `<url>/v1` as the base URL for
Cursor or the Agent — **do not commit the URL**.

### Optional: test the exact image locally with Docker first

```bash
docker build -t codegen-api fastapi-deploy
docker run --rm -p 8080:8080 codegen-api
# then open http://localhost:8080/health
```

---

## Start / stop / cost (Cloud Run)

Your service is deployed with **`CLOUD_RUN_MIN_INSTANCES=0`** (see
`infra/cloudrun/deploy.env`). That means Cloud Run **scales to zero** when there
is no traffic — you do not need to manually stop it for normal day-to-day use.

Live URL (also saved in `deploy.env` as `CLOUD_RUN_SERVICE_URL`):

`https://codegen-api-161349047936.asia-south2.run.app`

| Endpoint | URL |
| --- | --- |
| Health | `<url>/health` |
| Swagger docs | `<url>/docs` |
| OpenAI base (Cursor / Agent) | `<url>/v1` |
| Model name | `codegen-multi-adapter` |

### Option 1 — Do nothing (recommended for daily use)

**When:** You are not using the API for hours or days, but will use it again soon.

**What happens:**
- Cloud Run automatically stops the container after idle time.
- You pay **no CPU/RAM** while scaled to zero.
- Small costs may still apply (Artifact Registry image storage, build logs).

**What you do:** Nothing. Leave the service deployed.

**Tradeoff:** The first request after idle is a **cold start** — the container
must load the base model and Hub adapters from Hugging Face. Expect **1–3+ minutes**
before `/health` returns `"status":"ok"`. Send chat requests only after health
is OK.

### Option 2 — Wake it when you need it (no redeploy)

**When:** You want to use the API again after it has been idle.

**What you do:** Just call the service — there is no separate “start” command.

1. Open or request: `https://codegen-api-161349047936.asia-south2.run.app/health`
2. Wait until the response shows `"status":"ok"` and `"loaded": true`.
3. Use the API normally (`/v1/chat/completions`, Cursor with base URL `<url>/v1`, etc.).

**PowerShell example:**

```powershell
Invoke-WebRequest "https://codegen-api-161349047936.asia-south2.run.app/health" -UseBasicParsing
```

**curl example:**

```bash
curl https://codegen-api-161349047936.asia-south2.run.app/health
```

Cloud Run starts the container on the first request automatically.

### Option 3 — Fully stop (maximum savings / no public access)

Use this only for **long breaks** (weeks/months) or when you want to guarantee
no one can call the service.

#### 3a — Delete the Cloud Run service

Removes the live URL. You must redeploy to bring it back.

```powershell
gcloud run services delete codegen-api --region asia-south2
```

Confirm when prompted. To start again later:

```powershell
python fastapi-deploy/infra/cloudrun/deploy.py
```

The script rebuilds (if needed), redeploys, and prints a new URL — update
`CLOUD_RUN_SERVICE_URL` in `deploy.env`.

#### 3b — Keep the service, block public access

The service stays deployed but unauthenticated callers cannot reach it.

**GCP Console:** Cloud Run → `codegen-api` → **Security** → remove
**Allow unauthenticated invocations** (or adjust IAM).

**CLI (remove public invoke):**

```powershell
gcloud run services remove-iam-policy-binding codegen-api `
  --region asia-south2 `
  --member="allUsers" `
  --role="roles/run.invoker"
```

To allow public access again:

```powershell
gcloud run services add-iam-policy-binding codegen-api `
  --region asia-south2 `
  --member="allUsers" `
  --role="roles/run.invoker"
```

### Quick reference

| Goal | Action |
| --- | --- |
| Save compute while idle | **Option 1** — already automatic (`min-instances=0`) |
| Use the API again | **Option 2** — hit `/health`, then call `/v1/...` |
| Long pause, delete service | **Option 3a** — `gcloud run services delete ...` |
| Long pause, block traffic | **Option 3b** — remove `allUsers` invoker binding |
| Bring back after delete | `python fastapi-deploy/infra/cloudrun/deploy.py` |

---

## After fine-tuning: publish and redeploy

Use this checklist whenever you finish a new LoRA training run (e.g. v3, v4)
and want Cloud Run to serve it. **Run your eval first** (e.g. 50-sample gold
validation) and only publish when you are satisfied with metrics.

### End-to-end workflow

| Step | What | Why |
| --- | --- | --- |
| **0** | Fine-tune → `models/checkpoints/<version>/<task>/` | Adapters must exist locally |
| **1** | Eval locally (`run_baseline_eval.py --adapter-run <version> --max-samples 50`) | Confirm quality before overwriting Hub |
| **2** | Dry-run publish | Verify paths and Hub repo mapping |
| **3** | Publish to Hub | Updates `codegenstudio/codegen-350M-*-lora` weights |
| **4** | Set `checkpoint_version` in `manifest.yaml` | `/health` and docs show correct version |
| **5** | Redeploy Cloud Run | New revision pulls updated Hub adapters at startup |
| **6** | Verify `/health` + test `/docs` | Confirm `"checkpoint_version"` and a sample SQL call |

### Step 0 — Local checkpoints

After training, each task should have adapter files under:

```text
models/checkpoints/<version>/text2sql/adapter_config.json
models/checkpoints/<version>/sql2nosql/adapter_config.json
models/checkpoints/<version>/nosql2doc/adapter_config.json
```

Example eval before publish (from repo root):

```powershell
python scripts/run_baseline_eval.py --adapter-run v3 --max-samples 50
```

Compare `results/.../metrics.json` against the previous version (baseline-v2,
lora-v2, etc.) before pushing to Hub.

### Step 2 — Dry-run (no upload)

**bash:**

```bash
PYTHONPATH=fastapi-deploy python fastapi-deploy/publish/push_adapters.py --version v3 --dry-run
```

**Windows PowerShell:**

```powershell
cd C:\Users\Bhavani\Documents\Codegen\Latest\CodeGen-Implementations-May_26
$env:PYTHONPATH = "fastapi-deploy"
python fastapi-deploy/publish/push_adapters.py --version v3 --dry-run
```

Expected output maps each task folder → `codegenstudio/codegen-350M-<task>-lora`.

### Step 3 — Publish to Hugging Face Hub

Auth once: `hf auth login` (or set `HF_TOKEN` / pass `--token`).

**bash:**

```bash
PYTHONPATH=fastapi-deploy python fastapi-deploy/publish/push_adapters.py --version v3
```

**Windows PowerShell:**

```powershell
$env:PYTHONPATH = "fastapi-deploy"
python fastapi-deploy/publish/push_adapters.py --version v3
```

This uploads `models/checkpoints/v3/<task>/` into the **same Hub repo names** used
by Cloud Run. Previous weights in those repos are replaced.

### Step 4 — Update manifest

Edit `fastapi-deploy/manifest.yaml`:

```yaml
checkpoint_version: v3   # was v2
```

Optional env override at deploy time: `CODEGEN_CHECKPOINT_VERSION=v3`.

### Step 5 — Redeploy Cloud Run

From repo root (same on Windows, macOS, Linux):

```powershell
python fastapi-deploy/infra/cloudrun/deploy.py
```

The script rebuilds the image (includes updated `manifest.yaml`), deploys to
Cloud Run, and prints the HTTPS URL. Update `CLOUD_RUN_SERVICE_URL` in
`infra/cloudrun/deploy.env` if the URL changes.

Cloud Run container env (set by `deploy.py` / Dockerfile):

- `CODEGEN_ADAPTER_SOURCE=hub` — pull adapters from Hugging Face, not local disk
- `HF_ORG=codegenstudio`
- `CODEGEN_EAGER_LOAD=true` — load model + adapters at startup

**Cold start:** first request after idle may take **1–3+ minutes** while the
container downloads the base model and Hub adapters. Hit `/health` until
`"status":"ok"` and `"loaded": true` before sending chat requests.

### Step 6 — Verify

1. **Health:** `<url>/health` → `"checkpoint_version": "v3"`, adapters list Hub ids
2. **Docs:** `<url>/docs` → try `POST /v1/chat/completions` with `"intent": "text2sql"`
3. **Optional:** re-run a small smoke eval pointing at the Cloud URL (agent tool will use this later)

### Quick reference (copy-paste)

Replace `v3` with your new version tag:

```powershell
# From repo root — after eval looks good
$env:PYTHONPATH = "fastapi-deploy"
python fastapi-deploy/publish/push_adapters.py --version v3 --dry-run
python fastapi-deploy/publish/push_adapters.py --version v3
# Edit manifest.yaml: checkpoint_version: v3
python fastapi-deploy/infra/cloudrun/deploy.py
curl.exe "<your-cloud-run-url>/health"
```

### Publish adapters (script reference)

`publish/push_adapters.py` is version-agnostic — pass any `--version` that exists
under `models/checkpoints/`. Flags: `--org`, `--token`, `--private`, `--dry-run`.

---

## Configuration

| Setting | Manifest key | Env override | Default |
| --- | --- | --- | --- |
| Base model | `base_model` | `CODEGEN_BASE_MODEL` | `Salesforce/codegen-350M-multi` |
| Checkpoint version | `checkpoint_version` | `CODEGEN_CHECKPOINT_VERSION` | `v2` |
| Adapter source | `adapter_source` | `CODEGEN_ADAPTER_SOURCE` | `local` |
| Checkpoints root | `checkpoints_root` | `CODEGEN_CHECKPOINTS_ROOT` | `models/checkpoints` |
| Eager load | `eager_load` | `CODEGEN_EAGER_LOAD` | `true` |
| Device | `device` | `CODEGEN_DEVICE` | `auto` |
| Confidence floor | `classifier.confidence_threshold` | `CODEGEN_CONFIDENCE_THRESHOLD` | `0.45` |
| Hub org | `hub.org` | `HF_ORG` | `codegenstudio` |

`adapter_source`:
- `local` — load from `models/checkpoints/<version>/<task>/`
- `hub` — load `codegenstudio/codegen-350M-<task>-lora`

---

## Cross-platform notes (Windows today, Mac tomorrow)

- `entrypoint.sh` runs **inside the Linux container**, so it works no matter
  what your host OS is — you never run it directly on Windows.
- Deploying is a **single Python file** (`deploy.py`) that runs identically on
  Windows, macOS, and Linux — no separate `.sh` / `.ps1` scripts to maintain.
- For local dev, the run commands above cover both PowerShell and bash.

---

## Tests

```bash
pip install pytest
PYTHONPATH=fastapi-deploy pytest fastapi-deploy/tests -q
```

Unit tests cover intent classification and prompt formatting — no GPU or model
weights required.