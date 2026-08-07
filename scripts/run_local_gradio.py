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


def _load_project_env() -> None:
    """Load repo .env so LangSmith tracing works outside langgraph dev."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.is_file():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path, override=False)
    except ImportError:
        pass


_load_project_env()

# Shared resolver: local models/qwen_multitask/merged → Saikrishna2511/qwen-multitask
sys.path.insert(0, str(PROJECT_ROOT))
from inference.generator import HF_FT_MODEL, local_merged_path, resolve_codegen_model_id  # noqa: E402


def resolve_model_id(explicit: str | None) -> str:
    """CLI wrapper around shared FT model resolution."""
    # Ignore ambient MODEL_ID when choosing the launch default so --model-id /
    # local merged / Hub FT take precedence unless the user set --model-id.
    if explicit:
        return resolve_codegen_model_id(explicit=explicit)
    saved = os.environ.pop("MODEL_ID", None)
    try:
        return resolve_codegen_model_id()
    finally:
        if saved is not None:
            os.environ["MODEL_ID"] = saved


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local Gradio multitask demo")
    parser.add_argument(
        "--model-id",
        default=None,
        help=(
            "Model path or Hugging Face repo id "
            f"(default: local merged, else {HF_FT_MODEL})"
        ),
    )
    parser.add_argument("--port", type=int, default=7860, help="Gradio server port")
    args = parser.parse_args()

    if not SPACE_DIR.exists():
        print(f"Space app not found: {SPACE_DIR}", file=sys.stderr)
        return 1

    model_id = resolve_model_id(args.model_id)
    merged = local_merged_path()
    if model_id == str(merged.resolve()) and not merged.exists():
        print(f"Local model not found at {merged}", file=sys.stderr)
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
