"""Verify LoRA adapter artifacts under models/checkpoints/."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.models.model_loader import is_adapter_dir
from src.training.tasks import TRAINING_TASKS
from src.utils.config import get_adapter_path, get_adapter_run, load_config

REQUIRED_ADAPTER_FILES = ("adapter_config.json", "adapter_model.safetensors")


@dataclass
class AdapterVerifyResult:
    """Outcome of verifying one task adapter directory."""

    task: str
    adapter_path: Path
    ok: bool
    missing_files: tuple[str, ...]
    metadata: dict[str, Any] | None
    errors: tuple[str, ...]


def verify_adapter_dir(
    task: str,
    adapter_path: str | Path | None = None,
    *,
    config: dict[str, Any] | None = None,
    require_metadata: bool = True,
) -> AdapterVerifyResult:
    """Check that a task adapter dir has required PEFT files and optional metadata."""
    cfg = config or load_config()
    path = Path(adapter_path) if adapter_path is not None else get_adapter_path(task, cfg)
    errors: list[str] = []
    missing: list[str] = []

    if not path.exists():
        errors.append(f"directory does not exist: {path}")
    elif not is_adapter_dir(path):
        errors.append(f"missing adapter_config.json in {path}")

    for name in REQUIRED_ADAPTER_FILES:
        if not (path / name).is_file():
            missing.append(name)

    metadata: dict[str, Any] | None = None
    metadata_path = path / "run_metadata.json"
    if require_metadata and not metadata_path.is_file():
        missing.append("run_metadata.json")
    elif metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    ok = not errors and not missing
    return AdapterVerifyResult(
        task=task,
        adapter_path=path,
        ok=ok,
        missing_files=tuple(missing),
        metadata=metadata,
        errors=tuple(errors),
    )


def verify_all_adapters(
    tasks: tuple[str, ...] | None = None,
    *,
    config: dict[str, Any] | None = None,
    run: str | None = None,
    require_metadata: bool = True,
) -> dict[str, AdapterVerifyResult]:
    """Verify adapter directories for each training task under the given run folder."""
    task_list = tasks or tuple(sorted(TRAINING_TASKS))
    resolved_run = run if run is not None else get_adapter_run(config)
    return {
        task: verify_adapter_dir(
            task,
            adapter_path=get_adapter_path(task, config, run=resolved_run),
            config=config,
            require_metadata=require_metadata,
        )
        for task in task_list
    }
