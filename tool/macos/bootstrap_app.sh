#!/usr/bin/env bash
# Point CodeGen.app's MacOS/CodeGen symlink at the ai conda Python interpreter.
set -euo pipefail

MACOS_DIR="$(cd "$(dirname "$0")/CodeGen.app/Contents/MacOS" && pwd)"
TARGET="$MACOS_DIR/CodeGen"

if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found; cannot wire CodeGen.app to the ai environment." >&2
  exit 1
fi

PYTHON="$(conda run -n ai which python)"
ln -sf "$PYTHON" "$TARGET"
