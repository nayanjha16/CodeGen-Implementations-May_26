"""Project path helpers for models and datasets."""

from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_project_root() -> Path:
    """Return project root directory."""
    return _PROJECT_ROOT


def _load_env() -> None:
    """Load .env from project root (does not override existing env vars)."""
    load_dotenv(_PROJECT_ROOT / ".env")


def _env_path(key: str, default: str) -> Path:
    _load_env()
    value = os.environ.get(key, default)
    path = Path(value)
    return path if path.is_absolute() else _PROJECT_ROOT / path


def get_models_base_dir() -> Path:
    """Directory for downloaded base models."""
    return _env_path("MODELS_BASE_DIR", "models/base")


def get_models_checkpoints_dir() -> Path:
    """Directory for training checkpoints."""
    return _env_path("MODELS_CHECKPOINTS_DIR", "models/checkpoints")


def get_data_dir() -> Path:
    """Root data directory."""
    return _env_path("DATA_DIR", "data")


def get_spider_data_dir() -> Path:
    """Local Spider dataset directory."""
    return _env_path("SPIDER_DATA_DIR", "data/spider")


def get_bird_data_dir() -> Path:
    """Local BIRD dataset directory."""
    return _env_path("BIRD_DATA_DIR", "data/bird")


def get_results_dir() -> Path:
    """Directory for evaluation output JSON files."""
    return _env_path("RESULTS_DIR", "results")


def model_slug(model_name: str) -> str:
    """Convert a HuggingFace model id to a safe local directory name."""
    return re.sub(r"[^\w.\-]+", "__", model_name.replace("/", "__"))


def get_model_cache_dir(model_name: str) -> Path:
    """Local cache path for a base model."""
    return get_models_base_dir() / model_slug(model_name)


def get_checkpoint_path(checkpoint_name: str) -> Path:
    """Resolve a checkpoint directory under models/checkpoints/."""
    return get_models_checkpoints_dir() / checkpoint_name


def resolve_project_path(path: str | Path) -> Path:
    """Resolve a config path relative to the project root."""
    resolved = Path(path)
    return resolved if resolved.is_absolute() else _PROJECT_ROOT / resolved


def resolve_results_run_dir(name: str | Path) -> Path:
    """Resolve a named evaluation run directory under results/.

    Creates ``results/<name>/`` and returns that path. A ``.json`` suffix on
    ``name`` is ignored so legacy filenames still map to a folder name.
    """
    raw_path = Path(name)
    if raw_path.suffix.lower() == ".json":
        raw_path = raw_path.with_suffix("")
    safe = re.sub(r"[^\w.\-]+", "__", raw_path.name).strip("_") or "eval_run"
    run_dir = get_results_dir() / safe
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def resolve_results_output_path(path: str | Path) -> Path:
    """Resolve an evaluation output path under the project results directory.

    - ``my_eval.json`` -> ``results/my_eval.json``
    - ``data/results/my_eval.json`` -> ``results/my_eval.json`` (legacy redirect)
    - ``results/my_eval.json`` -> unchanged
    """
    resolved = resolve_project_path(path)
    try:
        relative = resolved.relative_to(_PROJECT_ROOT)
    except ValueError:
        return resolved

    parts = relative.parts
    if len(parts) >= 2 and parts[0] == "data" and parts[1] == "results":
        return get_results_dir() / Path(*parts[2:])
    if len(parts) == 1:
        return get_results_dir() / parts[0]
    return resolved


def is_dataset_cached(data_dir: Path) -> bool:
    """Return True when a dataset has been downloaded to the local cache."""
    return (data_dir / ".downloaded").exists()


def is_spider_cached(data_dir: Path) -> bool:
    """Return True when Spider data files exist locally."""
    if not is_dataset_cached(data_dir):
        return False
    if (data_dir / "dev.json").exists() or (data_dir / "train_spider.json").exists():
        return True
    if (data_dir / "spider_data" / "dev.json").exists():
        return True
    return any(
        (path / "dev.json").exists() or (path / "train_spider.json").exists()
        for path in data_dir.glob("spider-*")
    )


def is_bird_cached(data_dir: Path) -> bool:
    """Return True when BIRD data files exist locally."""
    if not is_dataset_cached(data_dir):
        return False
    candidates = [
        data_dir / "DAMO-ConvAI-master" / "bird" / "finetuning",
        data_dir / "bird" / "finetuning",
    ]
    for path in candidates:
        if (path / "dev.json").exists() or (path / "train.json").exists():
            return True
    return any(
        (path / "dev.json").exists() or (path / "train.json").exists()
        for path in data_dir.rglob("finetuning")
    )


def ensure_storage_dirs() -> None:
    """Create standard models/, data/, and results/ directories if missing."""
    for directory in (
        get_models_base_dir(),
        get_models_checkpoints_dir(),
        get_data_dir(),
        get_spider_data_dir(),
        get_bird_data_dir(),
        get_results_dir(),
    ):
        directory.mkdir(parents=True, exist_ok=True)
