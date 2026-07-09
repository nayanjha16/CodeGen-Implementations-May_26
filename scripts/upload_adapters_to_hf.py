#!/usr/bin/env python3
"""Upload LoRA adapter checkpoints to the Hugging Face Hub."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.training.tasks import TRAINING_TASKS
from src.utils.paths import get_models_checkpoints_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Upload task LoRA adapters from models/checkpoints/<run>/ to Hugging Face.",
    )
    parser.add_argument(
        "--run",
        "--version",
        dest="run",
        required=True,
        help="Checkpoint run folder under models/checkpoints/ (e.g. v3).",
    )
    parser.add_argument(
        "--repo-id",
        required=True,
        help="Target Hugging Face model repo (e.g. your-username/codegen-lora-v3).",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        choices=sorted(TRAINING_TASKS),
        default=list(sorted(TRAINING_TASKS)),
        help="Tasks to upload (default: all three).",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create/use a private Hub repository.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print upload plan without pushing to the Hub.",
    )
    return parser


def _hub_token() -> str:
    import os

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not token:
        raise ValueError(
            "HF_TOKEN is not set. Add it to Kaggle secrets or export it locally."
        )
    return token


def upload_adapters(
    *,
    run: str,
    repo_id: str,
    tasks: tuple[str, ...],
    private: bool = False,
    dry_run: bool = False,
) -> dict[str, str]:
    """Upload adapter folders and return mapping task -> Hub path."""
    from huggingface_hub import HfApi, create_repo

    run_dir = get_models_checkpoints_dir() / run
    if not run_dir.is_dir():
        raise FileNotFoundError(f"Checkpoint run not found: {run_dir}")

    missing = [task for task in tasks if not (run_dir / task).is_dir()]
    if missing:
        raise FileNotFoundError(
            f"Missing adapter directories for: {', '.join(missing)} under {run_dir}"
        )

    if dry_run:
        print(f"Would create repo: {repo_id} (private={private})")
        for task in tasks:
            print(f"  would upload: {run_dir / task} -> {repo_id}/{task}/")
        summary = run_dir.glob("training_summary_*.json")
        for path in sorted(summary):
            print(f"  would upload: {path.name} -> {repo_id}/")
        return {task: f"{repo_id}/{task}" for task in tasks}

    token = _hub_token()
    api = HfApi(token=token)
    create_repo(repo_id, repo_type="model", private=private, exist_ok=True)

    uploaded: dict[str, str] = {}
    for task in tasks:
        adapter_dir = run_dir / task
        print(f"Uploading {adapter_dir} -> {repo_id}/{task}/")
        api.upload_folder(
            folder_path=str(adapter_dir),
            path_in_repo=task,
            repo_id=repo_id,
            repo_type="model",
            commit_message=f"Upload {task} LoRA adapter ({run})",
        )
        uploaded[task] = f"{repo_id}/{task}"

    manifest = {
        "checkpoint_run": run,
        "repo_id": repo_id,
        "tasks": list(tasks),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "hub_paths": uploaded,
    }
    manifest_path = run_dir / "hf_upload_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    for summary_path in sorted(run_dir.glob("training_summary_*.json")):
        api.upload_file(
            path_or_fileobj=str(summary_path),
            path_in_repo=summary_path.name,
            repo_id=repo_id,
            repo_type="model",
            commit_message=f"Upload training summary ({run})",
        )

    readme = run_dir / "README.md"
    if not readme.exists():
        readme.write_text(
            "\n".join(
                [
                    f"# LoRA adapters — {run}",
                    "",
                    f"Base model and training config are documented in the main project.",
                    "",
                    "## Tasks",
                    "",
                    *[f"- `{task}/` — {repo_id}/{task}" for task in tasks],
                    "",
                    f"Uploaded at: {manifest['uploaded_at']}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
    api.upload_file(
        path_or_fileobj=str(readme),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="model",
        commit_message=f"Upload adapter README ({run})",
    )

    print(f"Upload complete: https://huggingface.co/{repo_id}")
    print(f"Manifest: {manifest_path}")
    return uploaded


def main() -> int:
    args = build_parser().parse_args()
    upload_adapters(
        run=args.run,
        repo_id=args.repo_id,
        tasks=tuple(args.tasks),
        private=args.private,
        dry_run=args.dry_run,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
