#!/usr/bin/env bash
# Start Streamlit UI
set -euo pipefail

cd "$(dirname "$0")/.."

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

PORT="${PORT:-8501}"

echo "Starting CodeGen Streamlit UI on port ${PORT}"
streamlit run apps/streamlit/app.py --server.port "$PORT"
