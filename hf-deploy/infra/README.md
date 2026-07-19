# Google Cloud Run deployment for hf-deploy

Deploy the multi-adapter FastAPI API on **Google Cloud Run**. HTTPS is included automatically — no domain required (`https://***.run.app`).

## Architecture

```text
Your laptop (or GitHub Actions)
   │
   ├── gcloud builds submit  →  Artifact Registry (Docker image)
   └── gcloud run deploy   →  Cloud Run service
                                  │
                                  ▼
                             FastAPI container (port 8080)
                                  │
                             https://***.run.app  (TLS built-in)
```

## Why Cloud Run vs Oracle

| | Cloud Run | Oracle VM |
|---|-----------|-----------|
| HTTPS | Automatic `https://***.run.app` | Needs domain + Caddy |
| Ops | No VM/SSH/Ansible | Terraform + Ansible + systemd |
| Scale | Scales to zero | Always-on VM |
| Cost | Free tier + pay per use | Always Free tier |

## Prerequisites

1. [Google Cloud account](https://cloud.google.com/free)
2. A GCP project with billing enabled (free tier still applies)
3. [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed locally
4. Enable APIs (deploy script uses these):

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

## 1. One-time setup

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

Copy and edit env (default region: **Hyderabad** / `asia-south2`):

```bash
cd hf-deploy/infra/cloudrun
cp env.example env.sh
# Edit GCP_PROJECT_ID, region, etc.
source env.sh
```

## 2. Deploy (from your laptop)

```bash
chmod +x deploy.sh
source env.sh   # if not already sourced this shell
./deploy.sh
```

First deploy builds the image, pushes to Artifact Registry, and creates the Cloud Run service. Model download from Hugging Face happens on container startup (can take several minutes).

After deploy, save the service URL in **`env.sh`** only (gitignored — never commit it):

```bash
export CLOUD_RUN_SERVICE_URL="https://***.asia-south2.run.app"
```

`deploy.sh` prints the URL and tries to append/update `CLOUD_RUN_SERVICE_URL` in your local `env.sh`.

Verify (uses env, not a hardcoded URL):

```bash
source env.sh
curl -sS "${CLOUD_RUN_SERVICE_URL}/health"
```

Cursor base URL: `${CLOUD_RUN_SERVICE_URL}/v1` (model: `codegen-multi-adapter`).

---

## Redeploy cheat sheet

Run from repo root unless noted.

### A. You changed `hf-deploy` code (API, classifier, prompts, `requirements.txt`, `manifest.yaml`)

```bash
# Optional but recommended
PYTHONPATH=hf-deploy pytest hf-deploy/tests -q

cd hf-deploy/infra/cloudrun
source env.sh
./deploy.sh

# Verify (no URL in repo — read from env.sh)
source env.sh
curl -sS "${CLOUD_RUN_SERVICE_URL}/health"
```

`./deploy.sh` rebuilds the Docker image, pushes it, and rolls out a new Cloud Run revision (~10 min).

### B. You published new adapter weights to Hugging Face Hub

Hub weights are **not** in the Docker image — the container pulls them at startup from `care2achieve/codegen-350M-*-lora`.

```bash
# 1. Upload new checkpoints to Hub
PYTHONPATH=hf-deploy python hf-deploy/publish/push_adapters.py --version v3

# 2. If checkpoint version changed, update hf-deploy/manifest.yaml (checkpoint_version)
# 3. Redeploy so the new manifest is baked in and containers restart
cd hf-deploy/infra/cloudrun
source env.sh
./deploy.sh
```

If you overwrote weights in the **same** Hub repos and did **not** change `manifest.yaml` or code, force a restart without a full rebuild:

```bash
source env.sh
gcloud run deploy "${SERVICE_NAME}" \
  --image "${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${AR_REPO}/${SERVICE_NAME}:latest" \
  --region "${GCP_REGION}" \
  --project "${GCP_PROJECT_ID}"
```

A full `./deploy.sh` is simpler and always safe.

### C. One-time setup already done?

Next time you usually only need:

```bash
cd hf-deploy/infra/cloudrun
source env.sh
./deploy.sh
```

Ensure `gcloud auth login` is still valid if deploy fails with auth errors.

### D. Optional — GitHub Actions instead of local deploy

Push to `main` with changes under `hf-deploy/` (after setting `GCP_PROJECT_ID`, `GCP_SA_KEY` secrets).

---

Output includes (URL shown only in your terminal / `env.sh` — **never commit**):

```text
Deployed: https://***.asia-south2.run.app
Health:   ${CLOUD_RUN_SERVICE_URL}/health
Cursor:   ${CLOUD_RUN_SERVICE_URL}/v1
```

## 3. Verify

```bash
source env.sh
curl -sS "${CLOUD_RUN_SERVICE_URL}/health" | jq .
```

Cursor settings (store URL locally — **do not commit**):

| Field | Value |
|-------|-------|
| Base URL | `${CLOUD_RUN_SERVICE_URL}/v1` from `env.sh` or `hf-deploy/.env` |
| Model | `codegen-multi-adapter` |

## Keep the URL private (billing / abuse)

The service URL is **not** stored in the git repo. Keep it only in:

| File | Gitignored |
|------|------------|
| `hf-deploy/infra/cloudrun/env.sh` | yes |
| `hf-deploy/.env` | yes |

Hiding the URL reduces casual discovery, but the service is still **publicly callable** while `--allow-unauthenticated` is set (required for Cursor without GCP identity tokens).

To limit unexpected GCP charges:

1. Set **budget alerts** in GCP Console → Billing → Budgets
2. Keep `CLOUD_RUN_MAX_INSTANCES=1` in `env.sh` (already default in `env.example`)
3. Do not paste the URL in README, issues, or public chat
4. Optional: remove `--allow-unauthenticated` in `deploy.sh` if you add an API-key gate in FastAPI later

---

## 4. Optional — GitHub Actions CD

Add repository secrets:

| Secret | Description |
|--------|-------------|
| `GCP_PROJECT_ID` | GCP project id |
| `GCP_SA_KEY` | JSON key for a deploy service account |
| `GCP_REGION` | e.g. `asia-south2` / Hyderabad (optional) |
| `CLOUD_RUN_SERVICE` | e.g. `codegen-api` (optional) |

Service account needs roles: `Cloud Run Admin`, `Cloud Build Editor`, `Artifact Registry Writer`, `Service Account User`.

Push to `main` with changes under `hf-deploy/` triggers test + deploy.

## Environment in the container

| Variable | Value |
|----------|-------|
| `HF_DEPLOY_ADAPTER_SOURCE` | `hub` |
| `HF_ORG` | `care2achieve` |
| `HF_DEPLOY_DEVICE` | `cpu` |
| `HF_DEPLOY_EAGER_LOAD` | `true` |
| `PORT` | `8080` (set by Cloud Run) |

## Sizing notes

Default in `deploy.sh`: **8 GiB RAM**, **2 CPU**. The 350M model + PyTorch needs this on CPU. Reduce only if you switch to lazy loading (`HF_DEPLOY_EAGER_LOAD=false`).

Startup probe allows ~6 minutes for first model download. Cold starts after scale-to-zero will be slow.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Container failed to start | `gcloud run services logs read SERVICE --region REGION` |
| `failed to load /entrypoint.sh: no such file or directory` | Windows CRLF in `entrypoint.sh` — pull latest `Dockerfile.cloudrun` (strips `\r` on build) and redeploy |
| More gcloud detail in terminal | `export VERBOSE=1` then `./deploy.sh` |
| Watch container startup live | `gcloud run services logs tail SERVICE --region REGION` (second terminal) |
| OOM / exit 137 | Increase `--memory` to `8Gi` or `16Gi` |
| Startup timeout | Increase startup probe `failureThreshold` in `deploy.sh` |
| 403 on curl | Ensure `--allow-unauthenticated` or pass identity token |

## Tear down

```bash
source env.sh
gcloud run services delete "${SERVICE_NAME}" --region "${GCP_REGION}"
gcloud artifacts docker images delete "${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${AR_REPO}/${SERVICE_NAME}:latest"
```

## Layout

```text
hf-deploy/
├── Dockerfile.cloudrun          # Cloud Run image
├── cloudbuild.yaml              # Cloud Build config
├── .dockerignore
└── infra/
    ├── README.md                # this file
    └── cloudrun/
        ├── deploy.sh            # local deploy script
        └── env.example
```

## Deprecated: Oracle Cloud

Oracle Terraform/Ansible files remain under `infra/terraform/` and `infra/ansible/` for reference but are **not maintained**. See [oracle/README.md](oracle/README.md).
