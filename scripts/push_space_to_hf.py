#!/usr/bin/env python3
"""Create and push the Gradio Space to Hugging Face Hub.

Bundles deploy/hf_space plus the agent/inference/utils/data packages the UI
imports, so Space matches local Gradio (scripts/run_local_gradio.py).
"""

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

# Packages required by deploy/hf_space/app.py agent tabs.
BUNDLE_DIRS = (
    "agent",
    "inference",
    "utils",
    "data",
)

IGNORE_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".DS_Store",
}
IGNORE_FILE_SUFFIXES = (".pyc", ".pyo", ".DS_Store")

# Keep Space payload small: skip raw/processed datasets under data/.
DATA_SKIP_DIR_NAMES = {"raw", "processed"}


def patch_readme(readme_path: Path, model_id: str, space_id: str) -> None:
    text = readme_path.read_text()
    text = text.replace("Qwen/Qwen2.5-Coder-0.5B-Instruct", model_id)
    text = text.replace("your-username/qwen-multitask", model_id)
    text = text.replace("your-username/qwen-multitask-demo", space_id)
    readme_path.write_text(text)


def _should_skip(path: Path, *, under_data: bool) -> bool:
    if path.name in IGNORE_DIR_NAMES or path.name.endswith(IGNORE_FILE_SUFFIXES):
        return True
    if under_data and path.is_dir() and path.name in DATA_SKIP_DIR_NAMES:
        return True
    return False


def _copy_package(src: Path, dst: Path, *, under_data: bool = False) -> None:
    if not src.exists():
        raise FileNotFoundError(f"Missing package to bundle: {src}")
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if _should_skip(item, under_data=under_data):
            continue
        target = dst / item.name
        if item.is_dir():
            _copy_package(item, target, under_data=under_data or src.name == "data")
        else:
            shutil.copy2(item, target)


def stage_space(staging: Path) -> None:
    """Copy Space UI + vendorized repo packages into staging."""
    shutil.copytree(
        SPACE_DIR,
        staging,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".DS_Store"),
    )
    for name in BUNDLE_DIRS:
        _copy_package(PROJECT_ROOT / name, staging / name, under_data=(name == "data"))
    # Ensure data.scripts is importable on Space.
    scripts_init = staging / "data" / "scripts" / "__init__.py"
    scripts_init.parent.mkdir(parents=True, exist_ok=True)
    if not scripts_init.exists():
        scripts_init.write_text('"""Data preprocessing and shared prompt templates."""\n')


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
    try:
        api.repo_info(repo_id=args.space_id, repo_type="space")
        print(f"Space already exists: https://huggingface.co/spaces/{args.space_id}")
    except Exception:
        try:
            api.create_repo(
                repo_id=args.space_id,
                repo_type="space",
                space_sdk="gradio",
                private=args.private,
                exist_ok=True,
            )
            print(f"Space repo ready: https://huggingface.co/spaces/{args.space_id}")
        except Exception as exc:
            print(
                f"Could not create Space {args.space_id}: {exc}\n"
                "If the Space already exists, upload will still be attempted.",
                file=sys.stderr,
            )

    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp) / "space"
        stage_space(staging)
        patch_readme(staging / "README.md", args.model_id, args.space_id)

        print("Staging contents:")
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                print(f"  {path.relative_to(staging)}")

        api.upload_folder(
            folder_path=str(staging),
            repo_id=args.space_id,
            repo_type="space",
            commit_message="Deploy latest Gradio Space with agent packages",
            ignore_patterns=["**/__pycache__/**", "**/*.pyc", "**/.DS_Store"],
            # Replace stale remote files (old thin Space without agent/).
            delete_patterns=["**"],
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

    try:
        api.restart_space(args.space_id)
        print("Requested Space restart")
    except Exception as exc:
        print(f"Warning: could not restart Space automatically ({exc}).", file=sys.stderr)

    print(f"Space deployed: https://huggingface.co/spaces/{args.space_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
