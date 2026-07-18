#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found. Activate the ai environment manually, then run: python tool/app.py" >&2
  exit 1
fi

if [[ "$(uname -s)" == "Darwin" ]]; then
  exec "$ROOT/tool/macos/launch_app.sh" "$@"
fi

exec conda run --no-capture-output -n ai python "$ROOT/tool/app.py" "$@"
