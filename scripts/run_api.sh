#!/usr/bin/env bash
# Start FastAPI server
set -euo pipefail

cd "$(dirname "$0")/.."

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "Starting CodeGen API on ${HOST}:${PORT}"
uvicorn src.api.main:app --host "$HOST" --port "$PORT" --reload
