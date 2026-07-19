#!/bin/sh
set -e
exec uvicorn hf_deploy.api.app:app --host 0.0.0.0 --port "${PORT:-8080}"
