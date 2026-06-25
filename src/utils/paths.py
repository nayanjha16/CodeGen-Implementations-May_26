"""Project path helpers for models and datasets."""

from __future__ import annotations

import os
import re
from datetime import datetime
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


def ensure_storage_dirs() -> None:
    """Create standard models/ and results/ directories if missing."""
    for directory in (
        get_models_base_dir(),
        get_models_checkpoints_dir(),
        get_results_dir(),
    ):
        directory.mkdir(parents=True, exist_ok=True)


def get_results_dir() -> Path:
    """Directory for evaluation output JSON files."""
    return _env_path("RESULTS_DIR", "results")


def model_slug(model_name: str) -> str:
    """Convert a HuggingFace model id to a safe local directory name."""
    return re.sub(r"[^\w.\-]+", "__", model_name.replace("/", "__"))


def short_model_name(model_id: str) -> str:
    """Use the HuggingFace repo tail as a compact run-name segment."""
    return model_id.rsplit("/", 1)[-1]


def _safe_run_name_segment(value: str, *, fallback: str) -> str:
    safe = re.sub(r"[^\w.\-]+", "__", value.strip()).strip("_")
    return safe or fallback


def build_results_run_name(
    *,
    dataset: str,
    model_name: str,
    when: datetime | None = None,
) -> str:
    """Build ``<dataset>_<model>_<DDMM>_<HHMM>`` for results run folders."""
    stamp = (when or datetime.now()).strftime("%d%m_%H%M")
    dataset_part = _safe_run_name_segment(dataset, fallback="dataset")
    model_part = _safe_run_name_segment(short_model_name(model_name), fallback="model")
    return f"{dataset_part}_{model_part}_{stamp}"


def get_model_cache_dir(model_name: str) -> Path:
    """Local cache path for a base model."""
    return get_models_base_dir() / model_slug(model_name)


def default_adapter_run_name(when: datetime | None = None) -> str:
    """Return DDMM folder name for a checkpoint run when no version/name is supplied."""
    return (when or datetime.now()).strftime("%d%m")


def resolve_adapter_run_name(run: str | None = None, when: datetime | None = None) -> str:
    """Sanitize a checkpoint run segment, defaulting to DDMM when empty."""
    fallback = default_adapter_run_name(when)
    if run is None or not str(run).strip():
        return fallback
    return _safe_run_name_segment(str(run), fallback=fallback)


def get_adapter_checkpoint_path(task: str, run: str | None = None) -> Path:
    """Resolve ``models/checkpoints/<run>/<task>/`` for LoRA adapter output."""
    normalized = task.strip().lower()
    run_name = resolve_adapter_run_name(run)
    return get_models_checkpoints_dir() / run_name / normalized


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


def get_tend_dataset_id() -> str:
    """Hugging Face dataset id for published TEND silver data."""
    _load_env()
    return os.environ.get("TEND_DATASET_ID", "care2achieve/tend")


def get_spider_gold_validation_path() -> Path:
    """Frozen Spider gold validation set used for all baseline evaluation."""
    return _env_path(
        "SPIDER_GOLD_VALIDATION_PATH",
        "data/spider_gold_validation.jsonl",
    )
