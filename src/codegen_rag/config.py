"""Typed configuration loading for the CodeGen capstone project.

All YAML files under ``configs/`` are loaded and merged into strongly typed
pydantic models so that the rest of the codebase never touches raw dicts.
Call :func:`load_settings` once per process (it is cached) and pass the
returned :class:`Settings` object down to every module.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


def _find_project_root(start: Path | None = None) -> Path:
    """Walk upward from ``start`` until a directory containing ``configs/`` is found.

    Falls back to the current working directory if no marker is found, which
    keeps this working both in Colab (``/content/...``) and locally.
    """
    here = start or Path(__file__).resolve()
    for parent in [here, *here.parents]:
        if (parent / "configs" / "config.yaml").exists():
            return parent
    return Path.cwd()


PROJECT_ROOT = _find_project_root()
CONFIGS_DIR = PROJECT_ROOT / "configs"


def _load_yaml(name: str) -> dict[str, Any]:
    path = CONFIGS_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"Expected config file at {path}. Are you running from the "
            f"project root ({PROJECT_ROOT})?"
        )
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


class PathsConfig(BaseModel):
    data_raw: str = "data/raw"
    data_processed: str = "data/processed"
    data_interim: str = "data/interim"
    checkpoints: str = "checkpoints"
    logs: str = "logs"
    results: str = "results"
    faiss_index: str = "faiss_index"


class BaseModelConfig(BaseModel):
    name: str = "Salesforce/codegen-350M-multi"
    revision: str = "main"
    max_length: int = 512
    device_map: str = "auto"


class UpperBoundLLMConfig(BaseModel):
    primary: str = "claude-sonnet-4-20250514"
    fallback_order: list[str] = Field(default_factory=list)
    max_tokens: int = 1024
    temperature: float = 0.2


class NewLanguageConfig(BaseModel):
    name: str = "rust"
    file_extension: str = ".rs"
    huggingface_filter: str = "Rust"


class WandbConfig(BaseModel):
    enabled: bool = False
    project: str = "codegen-rag-capstone"
    entity: str | None = None


class LoggingConfig(BaseModel):
    level: str = "INFO"
    log_to_file: bool = True
    tensorboard: bool = True
    wandb: WandbConfig = Field(default_factory=WandbConfig)


class ProjectConfig(BaseModel):
    name: str = "codegen-rag-capstone"
    seed: int = 42
    drive_subdir: str = "CodeGen_Capstone"


class Settings(BaseModel):
    """Top-level settings object composed from all YAML config files."""

    project: ProjectConfig = Field(default_factory=ProjectConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    base_model: BaseModelConfig = Field(default_factory=BaseModelConfig)
    upper_bound_llm: UpperBoundLLMConfig = Field(default_factory=UpperBoundLLMConfig)
    new_language: NewLanguageConfig = Field(default_factory=NewLanguageConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    data: dict[str, Any] = Field(default_factory=dict)
    model: dict[str, Any] = Field(default_factory=dict)
    training: dict[str, Any] = Field(default_factory=dict)

    root_dir: Path = Field(default=PROJECT_ROOT)

    model_config = {"arbitrary_types_allowed": True}

    def resolve_path(self, relative: str) -> Path:
        """Resolve a path relative to the project root, creating parents if needed."""
        full = self.root_dir / relative
        full.parent.mkdir(parents=True, exist_ok=True)
        return full

    def path_for(self, key: str) -> Path:
        """Resolve one of the named entries in ``paths`` (e.g. 'checkpoints')."""
        relative = getattr(self.paths, key)
        full = self.root_dir / relative
        full.mkdir(parents=True, exist_ok=True)
        return full


@lru_cache(maxsize=1)
def load_settings() -> Settings:
    """Load and merge all YAML configs into a single cached :class:`Settings`."""
    core = _load_yaml("config.yaml")
    data_cfg = _load_yaml("data_config.yaml")
    model_cfg = _load_yaml("model_config.yaml")
    training_cfg = _load_yaml("training_config.yaml")

    settings = Settings(
        project=ProjectConfig(**core.get("project", {})),
        paths=PathsConfig(**core.get("paths", {})),
        base_model=BaseModelConfig(**core.get("base_model", {})),
        upper_bound_llm=UpperBoundLLMConfig(**core.get("upper_bound_llm", {})),
        new_language=NewLanguageConfig(**core.get("new_language", {})),
        logging=LoggingConfig(**core.get("logging", {})),
        data=data_cfg,
        model=model_cfg,
        training=training_cfg,
        root_dir=PROJECT_ROOT,
    )
    return settings


def get_secret(name: str, default: str | None = None) -> str | None:
    """Fetch a secret from env vars, falling back to Colab userdata if available."""
    value = os.environ.get(name, default)
    if value is not None:
        return value
    try:
        from google.colab import userdata  # type: ignore

        return userdata.get(name)
    except Exception:
        return default
