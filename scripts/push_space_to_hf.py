#!/usr/bin/env python3
"""Create and push the Gradio Space to Hugging Face Hub."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SPACE_DIR = PROJECT_ROOT / "deploy" / "hf_space"
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from hf_auth import require_hf_auth


def patch_readme(readme_path: Path, model_id: str, space_id: str) -> None:
    text = readme_path.read_text()
    text = text.replace("Qwen/Qwen2.5-Coder-0.5B-Instruct", model_id)
    text = text.replace("your-username/qwen-multitask", model_id)
    text = text.replace("your-username/qwen-multitask-demo", space_id)
    readme_path.write_text(text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Push Gradio Space to HF Hub")
    parser.add_argument(
        "--space-id",
        required=True,
        help="Space repo id, e.g. username/qwen-multitask-demo",
    )
    parser.add_argument(
        "--model-id",
        required=True,
        help="Model repo id for README cross-links, e.g. username/qwen-multitask",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create a private Space",
    )
    parser.add_argument(
        "--hardware",
        default="cpu-basic",
        help="Space hardware flavor (cpu-basic, cpu-upgrade, t4-small, etc.)",
    )
    args = parser.parse_args()

    require_hf_auth()

    if not SPACE_DIR.exists():
        print(f"Space source not found: {SPACE_DIR}", file=sys.stderr)
        return 1

    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("Install huggingface_hub: pip install huggingface_hub", file=sys.stderr)
        return 1

    api = HfApi()
    api.create_repo(
        repo_id=args.space_id,
        repo_type="space",
        space_sdk="gradio",
        private=args.private,
        exist_ok=True,
    )
    print(f"Space repo ready: https://huggingface.co/spaces/{args.space_id}")

    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp) / "space"
        shutil.copytree(SPACE_DIR, staging)
        patch_readme(staging / "README.md", args.model_id, args.space_id)

        api.upload_folder(
            folder_path=str(staging),
            repo_id=args.space_id,
            repo_type="space",
        )

    try:
        api.add_space_variable(args.space_id, key="MODEL_ID", value=args.model_id)
        print(f"Set Space variable MODEL_ID={args.model_id}")
    except Exception as exc:
        print(
            f"Warning: could not set MODEL_ID variable automatically ({exc}). "
            "Set it manually in Space Settings -> Repository variables.",
            file=sys.stderr,
        )

    if args.hardware != "cpu-basic":
        try:
            api.request_space_hardware(args.space_id, hardware=args.hardware)
            print(f"Requested Space hardware: {args.hardware}")
        except Exception as exc:
            print(
                f"Warning: could not set hardware to {args.hardware} ({exc}). "
                "Change hardware in Space Settings if needed.",
                file=sys.stderr,
            )

    print(f"Space deployed: https://huggingface.co/spaces/{args.space_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
