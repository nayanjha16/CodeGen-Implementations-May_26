"""Path helpers for TEND dataset outputs."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.utils.paths import get_data_dir, get_project_root


def get_tend_output_dir() -> Path:
    """Return ``data/TEND`` output directory, creating it if needed."""
    output_dir = get_data_dir() / "TEND"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def build_output_csv_path(
    dataset: str,
    split: str,
    *,
    suffix: str | None = None,
) -> Path:
    """Build a timestamped CSV path under ``data/TEND``."""
    stamp = datetime.now().strftime("%m%d_%H%M")
    extra = f"_{suffix}" if suffix else ""
    filename = f"{dataset}_{split}{extra}_{stamp}.csv"
    return get_tend_output_dir() / filename


def ensure_project_on_path() -> Path:
    """Ensure project root is importable when running scripts directly."""
    root = get_project_root()
    return root
