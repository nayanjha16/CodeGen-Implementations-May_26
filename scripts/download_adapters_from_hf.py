#!/usr/bin/env python3
"""Download LoRA adapters from the Hugging Face Hub into models/checkpoints/."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.training.tasks import TRAINING_TASKS
from src.utils.paths import get_models_checkpoints_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download task LoRA adapters from a Hugging Face model repo.",
    )
    parser.add_argument(
        "--repo-id",
        required=True,
        help="Source Hugging Face model repo (e.g. your-username/codegen-lora-v3).",
    )
    parser.add_argument(
        "--run",
        "--version",
        dest="run",
        required=True,
        help="Local checkpoint run folder under models/checkpoints/ (e.g. v3).",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        choices=sorted(TRAINING_TASKS),
        default=list(sorted(TRAINING_TASKS)),
        help="Tasks to download (default: all three).",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Optional HF token for private repos (defaults to HF_TOKEN env).",
    )
    return parser


def download_adapters(
    *,
    repo_id: str,
    run: str,
    tasks: tuple[str, ...],
    token: str | None = None,
) -> dict[str, Path]:
    """Download each task adapter into models/checkpoints/<run>/<task>/."""
    from huggingface_hub import snapshot_download

    import os

    resolved_token = token or os.environ.get("HF_TOKEN") or os.environ.get(
        "HUGGING_FACE_HUB_TOKEN"
    )
    run_dir = get_models_checkpoints_dir() / run
    run_dir.mkdir(parents=True, exist_ok=True)

    patterns = [f"{task}/*" for task in tasks]
    print(f"Downloading {repo_id} ({', '.join(tasks)}) -> {run_dir}")
    snapshot_download(
        repo_id=repo_id,
        repo_type="model",
        allow_patterns=patterns,
        local_dir=str(run_dir),
        token=resolved_token,
    )

    downloaded: dict[str, Path] = {}
    for task in tasks:
        target = run_dir / task
        if not (target / "adapter_config.json").is_file():
            raise FileNotFoundError(
                f"Download finished but adapter files are missing in {target}"
            )
        downloaded[task] = target

    print(f"Adapters saved under {run_dir}")
    print("Run local validation with:")
    print(
        f"  python scripts/run_baseline_eval.py --version {run} "
        "--tend-config spider --mlflow"
    )
    return downloaded


def main() -> int:
    args = build_parser().parse_args()
    download_adapters(
        repo_id=args.repo_id,
        run=args.run,
        tasks=tuple(args.tasks),
        token=args.token,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
