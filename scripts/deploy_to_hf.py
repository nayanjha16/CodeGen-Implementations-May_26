#!/usr/bin/env python3
"""Upload model and Gradio Space to Hugging Face Hub."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from hf_auth import require_hf_auth


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy qwen_multitask model + Gradio Space")
    parser.add_argument("--username", default="Saikrishna2511", help="Hugging Face username or org")
    parser.add_argument(
        "--model-repo",
        default="qwen-multitask",
        help="Model repo name (default: qwen-multitask)",
    )
    parser.add_argument(
        "--space-repo",
        default="qwen-multitask-demo",
        help="Space repo name (default: qwen-multitask-demo)",
    )
    parser.add_argument("--private", action="store_true", help="Private model + Space repos")
    parser.add_argument(
        "--hardware",
        default="cpu-basic",
        help="Space hardware (cpu-basic, t4-small, etc.)",
    )
    parser.add_argument(
        "--skip-model",
        action="store_true",
        help="Skip model upload (Space only)",
    )
    parser.add_argument(
        "--skip-space",
        action="store_true",
        help="Skip Space push (model only)",
    )
    args = parser.parse_args()

    logged_in_as = require_hf_auth()
    if args.username != logged_in_as:
        print(
            f"Warning: --username {args.username} differs from logged-in account {logged_in_as}.",
            file=sys.stderr,
        )

    model_id = f"{args.username}/{args.model_repo}"
    space_id = f"{args.username}/{args.space_repo}"
    private_flag = ["--private"] if args.private else []

    if not args.skip_model:
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "upload_model_to_hf.py"),
            "--repo-id",
            model_id,
            "--space-id",
            space_id,
            "--create-repo",
            *private_flag,
        ]
        print("Uploading model...")
        subprocess.run(cmd, check=True)

    if not args.skip_space:
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "push_space_to_hf.py"),
            "--space-id",
            space_id,
            "--model-id",
            model_id,
            "--hardware",
            args.hardware,
            *private_flag,
        ]
        print("Pushing Space...")
        subprocess.run(cmd, check=True)

    print(f"\nModel: https://huggingface.co/{model_id}")
    print(f"Space: https://huggingface.co/spaces/{space_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
