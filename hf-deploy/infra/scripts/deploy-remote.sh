#!/usr/bin/env bash
# Run on the Oracle VM (or via GitHub Actions SSH) to update the API.
set -euo pipefail

REPO_DEST="${REPO_DEST:-/opt/codegen}"
REPO_BRANCH="${REPO_BRANCH:-main}"
VENV_PATH="${VENV_PATH:-/opt/codegen/venv}"
HF_DEPLOY_DIR="${HF_DEPLOY_DIR:-${REPO_DEST}/hf-deploy}"
SERVICE_NAME="${SERVICE_NAME:-hf-deploy}"

cd "${REPO_DEST}"
git fetch origin "${REPO_BRANCH}"
git checkout "${REPO_BRANCH}"
git pull --ff-only origin "${REPO_BRANCH}"

"${VENV_PATH}/bin/pip" install -r "${HF_DEPLOY_DIR}/requirements.txt"

sudo systemctl restart "${SERVICE_NAME}"
sudo systemctl is-active --quiet "${SERVICE_NAME}"

echo "Deploy complete. Checking health..."
curl -fsS "http://127.0.0.1:8000/health" || curl -fsS "http://127.0.0.1/health"
echo
