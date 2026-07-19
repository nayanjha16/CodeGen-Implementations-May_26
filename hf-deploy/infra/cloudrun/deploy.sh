#!/usr/bin/env bash
# Build and deploy hf-deploy to Google Cloud Run (local or CI).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HF_DEPLOY_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

: "${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
GCP_REGION="${GCP_REGION:-asia-south2}"
SERVICE_NAME="${SERVICE_NAME:-codegen-api}"
AR_REPO="${AR_REPO:-hf-deploy}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

CLOUD_RUN_MEMORY="${CLOUD_RUN_MEMORY:-8Gi}"
CLOUD_RUN_CPU="${CLOUD_RUN_CPU:-2}"
CLOUD_RUN_TIMEOUT="${CLOUD_RUN_TIMEOUT:-900}"
CLOUD_RUN_MIN_INSTANCES="${CLOUD_RUN_MIN_INSTANCES:-0}"
CLOUD_RUN_MAX_INSTANCES="${CLOUD_RUN_MAX_INSTANCES:-3}"
HF_ORG="${HF_ORG:-care2achieve}"

GCLOUD_VERBOSE_FLAG=""
if [[ "${VERBOSE:-0}" == "1" ]] || [[ "${DEPLOY_VERBOSE:-0}" == "1" ]]; then
  export CLOUDSDK_CORE_VERBOSITY="${CLOUDSDK_CORE_VERBOSITY:-debug}"
  GCLOUD_VERBOSE_FLAG="--verbosity=debug"
fi

IMAGE="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${AR_REPO}/${SERVICE_NAME}:${IMAGE_TAG}"

echo "Project:  ${GCP_PROJECT_ID}"
echo "Region:   ${GCP_REGION}"
echo "Service:  ${SERVICE_NAME}"
echo "Image:    ${IMAGE}"
if [[ -n "${GCLOUD_VERBOSE_FLAG}" ]]; then
  echo "Verbose:  on"
fi

echo ">>> Setting gcloud project..."
gcloud config set project "${GCP_PROJECT_ID}" ${GCLOUD_VERBOSE_FLAG:+"${GCLOUD_VERBOSE_FLAG}"}

echo ">>> Checking Artifact Registry repo (${AR_REPO})..."
if ! gcloud artifacts repositories describe "${AR_REPO}" --location="${GCP_REGION}" ${GCLOUD_VERBOSE_FLAG:+"${GCLOUD_VERBOSE_FLAG}"} >/dev/null 2>&1; then
  echo ">>> Creating Artifact Registry repo (${AR_REPO})..."
  gcloud artifacts repositories create "${AR_REPO}" \
    --repository-format=docker \
    --location="${GCP_REGION}" \
    --description="hf-deploy API images" \
    ${GCLOUD_VERBOSE_FLAG:+"${GCLOUD_VERBOSE_FLAG}"}
else
  echo ">>> Artifact Registry repo exists."
fi

echo ">>> Configuring Docker for Artifact Registry..."
gcloud auth configure-docker "${GCP_REGION}-docker.pkg.dev" --quiet

echo ">>> Submitting Cloud Build (Docker image — can take several minutes)..."
gcloud builds submit "${HF_DEPLOY_ROOT}" \
  --config "${HF_DEPLOY_ROOT}/cloudbuild.yaml" \
  --substitutions="_IMAGE=${IMAGE}" \
  ${GCLOUD_VERBOSE_FLAG:+"${GCLOUD_VERBOSE_FLAG}"}

echo ">>> Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}" \
  --region "${GCP_REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --memory "${CLOUD_RUN_MEMORY}" \
  --cpu "${CLOUD_RUN_CPU}" \
  --timeout "${CLOUD_RUN_TIMEOUT}" \
  --min-instances "${CLOUD_RUN_MIN_INSTANCES}" \
  --max-instances "${CLOUD_RUN_MAX_INSTANCES}" \
  --port 8080 \
  --cpu-boost \
  --startup-probe=initialDelaySeconds=30,timeoutSeconds=10,periodSeconds=10,failureThreshold=36,httpGet.path=/health,httpGet.port=8080 \
  --set-env-vars "HF_DEPLOY_ADAPTER_SOURCE=hub,HF_ORG=${HF_ORG},HF_DEPLOY_DEVICE=cpu,HF_DEPLOY_EAGER_LOAD=true,PYTHONPATH=/app" \
  ${GCLOUD_VERBOSE_FLAG:+"${GCLOUD_VERBOSE_FLAG}"}

SERVICE_URL="$(gcloud run services describe "${SERVICE_NAME}" --region "${GCP_REGION}" --format='value(status.url)' ${GCLOUD_VERBOSE_FLAG:+"${GCLOUD_VERBOSE_FLAG}"})"
ENV_FILE="${SCRIPT_DIR}/env.sh"
if [[ -f "${ENV_FILE}" ]]; then
  if grep -q '^export CLOUD_RUN_SERVICE_URL=' "${ENV_FILE}"; then
    python3 - <<PY
from pathlib import Path
import re
path = Path("${ENV_FILE}")
text = path.read_text()
text = re.sub(
    r'^export CLOUD_RUN_SERVICE_URL=.*$',
    'export CLOUD_RUN_SERVICE_URL="${SERVICE_URL}"',
    text,
    count=1,
    flags=re.M,
)
path.write_text(text)
PY
  else
    printf '\nexport CLOUD_RUN_SERVICE_URL="%s"\n' "${SERVICE_URL}" >> "${ENV_FILE}"
  fi
fi
echo
echo "Deployed: ${SERVICE_URL}"
echo "Health:   ${SERVICE_URL}/health"
echo "Cursor:   ${SERVICE_URL}/v1  (model: codegen-multi-adapter)"
echo "(URL saved to env.sh — keep env.sh out of git)"
echo
echo "Runtime logs (second terminal):"
echo "  gcloud run services logs tail ${SERVICE_NAME} --region ${GCP_REGION} --project ${GCP_PROJECT_ID}"
