#!/usr/bin/env bash
# Launch the desktop app through the macOS bundle so Dock/menu show CodeGen.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MACOS_DIR="$(cd "$(dirname "$0")/CodeGen.app/Contents/MacOS" && pwd)"

"$ROOT/tool/macos/bootstrap_app.sh"
exec "$MACOS_DIR/CodeGen" "$ROOT/tool/app.py" "$@"
