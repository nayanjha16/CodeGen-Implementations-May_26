"""Resolve the best LoRA adapter directory for a checkpoint version."""

from __future__ import annotations

import re
from pathlib import Path

from codegen_api import INTENTS

_CHECKPOINT_RE = re.compile(r"^checkpoint-(\d+)$")


def is_adapter_dir(path: Path) -> bool:
    """Return True when ``path`` contains PEFT adapter files."""
    return (path / "adapter_config.json").is_file()


def _checkpoint_step(path: Path) -> int:
    match = _CHECKPOINT_RE.match(path.name)
    return int(match.group(1)) if match else -1


def resolve_best_adapter(task_dir: Path) -> Path:
    """Pick the best adapter under a task directory.

    Preference order:
        1. Task root (trainer writes ``load_best_model_at_end`` here)
        2. Highest-numbered ``checkpoint-*`` folder that has adapter weights
    """
    task_dir = Path(task_dir)
    if not task_dir.is_dir():
        raise FileNotFoundError(f"Adapter task directory not found: {task_dir}")

    if is_adapter_dir(task_dir):
        return task_dir

    checkpoints = sorted(
        (
            p
            for p in task_dir.iterdir()
            if p.is_dir() and _CHECKPOINT_RE.match(p.name)
        ),
        key=_checkpoint_step,
        reverse=True,
    )
    for candidate in checkpoints:
        if is_adapter_dir(candidate):
            return candidate

    raise FileNotFoundError(
        f"No adapter_config.json under {task_dir} "
        "(checked task root and checkpoint-* folders)."
    )


def resolve_version_adapters(
    checkpoints_root: str,
    version: str,
    adapter_names: dict[str, str] | None = None,
) -> dict[str, Path]:
    """Map each intent to its best adapter path for ``version``."""
    version_dir = Path(checkpoints_root) / version
    if not version_dir.is_dir():
        raise FileNotFoundError(f"Checkpoint version not found: {version_dir}")

    names = adapter_names or {intent: intent for intent in INTENTS}
    resolved: dict[str, Path] = {}
    for intent in INTENTS:
        folder_name = names.get(intent, intent)
        task_dir = version_dir / folder_name
        resolved[intent] = resolve_best_adapter(task_dir)
    return resolved
