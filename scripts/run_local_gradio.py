#!/usr/bin/env python3
"""Launch the Gradio demo locally using the merged qwen_multitask checkpoint."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPACE_DIR = PROJECT_ROOT / "deploy" / "hf_space"
DEFAULT_LOCAL = PROJECT_ROOT / "models" / "qwen_multitask" / "merged"
HF_DEFAULT = "Saikrishna2511/qwen-multitask"


def resolve_model_id(explicit: str | None) -> str:
    if explicit:
        return explicit
    if DEFAULT_LOCAL.exists():
        return str(DEFAULT_LOCAL.resolve())
    return HF_DEFAULT


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local Gradio multitask demo")
    parser.add_argument(
        "--model-id",
        default=None,
        help="Model path or Hugging Face repo id (default: local merged checkpoint)",
    )
    parser.add_argument("--port", type=int, default=7860, help="Gradio server port")
    args = parser.parse_args()

    if not SPACE_DIR.exists():
        print(f"Space app not found: {SPACE_DIR}", file=sys.stderr)
        return 1

    model_id = resolve_model_id(args.model_id)
    if model_id == str(DEFAULT_LOCAL.resolve()) and not DEFAULT_LOCAL.exists():
        print(f"Local model not found at {DEFAULT_LOCAL}", file=sys.stderr)
        return 1

    env = os.environ.copy()
    env["MODEL_ID"] = model_id
    env["GRADIO_SERVER_PORT"] = str(args.port)
    # So deploy/hf_space/app.py can import the project-level `agent` package
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        str(PROJECT_ROOT) if not existing else f"{PROJECT_ROOT}{os.pathsep}{existing}"
    )

    print(f"Model: {model_id}")
    print(f"UI:    http://127.0.0.1:{args.port}")
    print("Press Ctrl+C to stop.\n")

    try:
        subprocess.run(
            [sys.executable, "app.py"],
            cwd=str(SPACE_DIR),
            env=env,
            check=True,
        )
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
