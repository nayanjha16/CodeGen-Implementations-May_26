#!/usr/bin/env python3
"""Upload the merged qwen_multitask checkpoint to Hugging Face Hub."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models" / "qwen_multitask" / "merged"
MODEL_CARD_TEMPLATE = PROJECT_ROOT / "deploy" / "model_card" / "README.md"
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from hf_auth import require_hf_auth


def build_model_card(repo_id: str, space_id: str | None, card_path: Path) -> str:
    template = card_path.read_text()
    space_url = (
        f"https://huggingface.co/spaces/{space_id}"
        if space_id
        else "https://huggingface.co/spaces (set --space-id to link your demo)"
    )
    return (
        template.replace("{repo_id}", repo_id)
        .replace("{space_url}", space_url)
        .replace("{model_url}", f"https://huggingface.co/{repo_id}")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload a merged model checkpoint to HF Hub")
    parser.add_argument(
        "--repo-id",
        required=True,
        help="Hugging Face model repo id, e.g. username/qwen-multitask",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=DEFAULT_MODEL_DIR,
        help="Path to merged checkpoint directory",
    )
    parser.add_argument(
        "--model-card",
        type=Path,
        default=MODEL_CARD_TEMPLATE,
        help="Path to model card README template",
    )
    parser.add_argument(
        "--space-id",
        default=None,
        help="Optional Space repo id for cross-linking, e.g. username/qwen-multitask-demo",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create/upload to a private model repo",
    )
    parser.add_argument(
        "--create-repo",
        action="store_true",
        help="Create the HF repo if it does not exist",
    )
    args = parser.parse_args()

    require_hf_auth()

    model_dir = args.model_dir.resolve()
    if not model_dir.exists():
        print(f"Model directory not found: {model_dir}", file=sys.stderr)
        return 1
    if not (model_dir / "model.safetensors").exists() and not (model_dir / "pytorch_model.bin").exists():
        print(f"No weights found in {model_dir}", file=sys.stderr)
        return 1

    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("Install huggingface_hub: pip install huggingface_hub", file=sys.stderr)
        return 1

    api = HfApi()
    if args.create_repo:
        api.create_repo(
            repo_id=args.repo_id,
            repo_type="model",
            private=args.private,
            exist_ok=True,
        )
        print(f"Repo ready: https://huggingface.co/{args.repo_id}")

    staging = PROJECT_ROOT / ".hf_upload_staging"
    if staging.exists():
        shutil.rmtree(staging)
    shutil.copytree(model_dir, staging)

    card_path = args.model_card.resolve()
    if not card_path.exists():
        print(f"Model card not found: {card_path}", file=sys.stderr)
        return 1
    card_text = build_model_card(args.repo_id, args.space_id, card_path)
    (staging / "README.md").write_text(card_text)

    print(f"Uploading {staging} -> {args.repo_id} ...")
    api.upload_folder(
        folder_path=str(staging),
        repo_id=args.repo_id,
        repo_type="model",
    )
    shutil.rmtree(staging)
    print(f"Upload complete: https://huggingface.co/{args.repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
