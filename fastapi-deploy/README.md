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

## Adapters are already on the Hub

All three v2 adapters are public on Hugging Face under **`codegenstudio`**:

| Task | Repo | Version |
| --- | --- | --- |
| text2sql | `codegenstudio/codegen-350M-text2sql-lora` | v2 |
| sql2nosql | `codegenstudio/codegen-350M-sql2nosql-lora` | v2 |
| nosql2doc | `codegenstudio/codegen-350M-nosql2doc-lora` | v2 |

So Cloud Run needs **no baking or publishing** — the container pulls these at
startup. To publish a new version later, see [Publish adapters](#publish-adapters).

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

HTTPS is included automatically (`*.run.app`). The container pulls v2 adapters
from the Hub, so nothing else is needed. **One deploy script works on every OS.**

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
must load the base model and v2 adapters from Hugging Face. Expect **1–3+ minutes**
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

## Publish adapters

The publish script is version-agnostic — pass any `--version`:

```bash
# Preview (no upload)
PYTHONPATH=fastapi-deploy python fastapi-deploy/publish/push_adapters.py --dry-run

# Publish any version
PYTHONPATH=fastapi-deploy python fastapi-deploy/publish/push_adapters.py --version v3
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "fastapi-deploy"
python fastapi-deploy/publish/push_adapters.py --version v3
```

Auth once with `hf auth login`, or set `HF_TOKEN` / pass `--token`. After
publishing a new version, set `CODEGEN_CHECKPOINT_VERSION=<version>` (or edit
`manifest.yaml`) and redeploy.

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