"""Configuration loading utilities."""

from pathlib import Path
from typing import Any

import yaml


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load YAML configuration with defaults."""
    if config_path is None:
        config_path = Path(__file__).resolve().parents[2] / "configs" / "default.yaml"
    config_path = Path(config_path)

    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_project_root() -> Path:
    """Return project root directory."""
    return Path(__file__).resolve().parents[2]
