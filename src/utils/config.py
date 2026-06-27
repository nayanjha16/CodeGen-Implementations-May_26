"""Configuration loading utilities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from src.utils.paths import get_checkpoint_path, get_project_root

DEFAULT_TEND_DATASET_ID = "care2achieve/tend"

TRAINING_TASKS = frozenset({"text2sql", "sql2nosql", "nosql2doc"})


def _load_env() -> None:
    """Load environment variables from .env (does not override existing values)."""
    load_dotenv(get_project_root() / ".env")


def _require_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise ValueError(
            f"{key} is not set. Copy .env.example to .env and configure {key}."
        )
    return value


def _ensure_dict(config: dict[str, Any], key: str) -> dict[str, Any]:
    """Return a nested dict section, replacing null YAML values."""
    value = config.get(key)
    if not isinstance(value, dict):
        value = {}
        config[key] = value
    return value


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load YAML configuration merged with environment variables."""
    _load_env()

    if config_path is None:
        config_path = get_project_root() / "configs" / "default.yaml"
    config_path = Path(config_path)

    with open(config_path, encoding="utf-8") as f:
        config: dict[str, Any] = yaml.safe_load(f) or {}

    model_cfg = _ensure_dict(config, "model")
    model_cfg["name"] = os.environ.get("MODEL_NAME", model_cfg.get("name"))
    model_cfg["base_dir"] = os.environ.get("MODELS_BASE_DIR", "models/base")
    model_cfg["checkpoints_dir"] = os.environ.get(
        "MODELS_CHECKPOINTS_DIR", "models/checkpoints"
    )
    if os.environ.get("MODEL_CHECKPOINT"):
        model_cfg["checkpoint"] = os.environ["MODEL_CHECKPOINT"]
    if os.environ.get("MODEL_ADAPTER"):
        model_cfg["adapter"] = os.environ["MODEL_ADAPTER"]

    training_cfg = _ensure_dict(config, "training")
    _ensure_dict(config, "lora")

    datasets_cfg = _ensure_dict(config, "datasets")
    tend_cfg = _ensure_dict(datasets_cfg, "tend")
    tend_cfg["dataset_id"] = os.environ.get(
        "TEND_DATASET_ID", DEFAULT_TEND_DATASET_ID
    )

    eval_cfg = _ensure_dict(config, "evaluation")
    eval_cfg["bertscore_model"] = os.environ.get("BERTSCORE_MODEL_NAME")
    eval_cfg["ollama_base_url"] = os.environ.get("OLLAMA_BASE_URL")
    eval_cfg["ollama_judge_model"] = os.environ.get("OLLAMA_JUDGE_MODEL")
    eval_cfg["judge_hf_model"] = os.environ.get("JUDGE_HF_MODEL")
    eval_cfg["ollama_timeout"] = os.environ.get("OLLAMA_TIMEOUT")

    # Apply model.max_length as default training max_length when not set in YAML.
    if training_cfg.get("max_length") is None:
        training_cfg["max_length"] = model_cfg.get("max_length", 2048)

    return config


def get_model_name(config: dict[str, Any] | None = None) -> str:
    """Return the configured model name from env/config."""
    _load_env()
    if config is None:
        config = load_config()
    name = config.get("model", {}).get("name") or os.environ.get("MODEL_NAME")
    if not name:
        return _require_env("MODEL_NAME")
    return name


def get_ollama_base_url(config: dict[str, Any] | None = None) -> str:
    """Return the configured Ollama base URL from env/config."""
    _load_env()
    if config is None:
        config = load_config()
    return (
        os.environ.get("OLLAMA_BASE_URL")
        or config.get("evaluation", {}).get("ollama_base_url")
        or "http://localhost:11434"
    )


def get_ollama_judge_model(config: dict[str, Any] | None = None) -> str:
    """Return the configured Ollama judge model from env/config."""
    _load_env()
    if config is None:
        config = load_config()
    return (
        os.environ.get("OLLAMA_JUDGE_MODEL")
        or config.get("evaluation", {}).get("ollama_judge_model")
        or "qwen3:4b"
    )


def get_judge_hf_model(config: dict[str, Any] | None = None) -> str | None:
    """Return an explicit Hugging Face judge model id for Ollama fallback."""
    _load_env()
    if config is None:
        config = load_config()
    return (
        os.environ.get("JUDGE_HF_MODEL")
        or config.get("evaluation", {}).get("judge_hf_model")
    )


def get_bertscore_model_name(config: dict[str, Any] | None = None) -> str:
    """Return the configured BERTScore model name from env/config."""
    _load_env()
    if config is None:
        config = load_config()
    name = (
        os.environ.get("BERTSCORE_MODEL_NAME")
        or config.get("evaluation", {}).get("bertscore_model")
    )
    if not name:
        return _require_env("BERTSCORE_MODEL_NAME")
    return name


def get_tend_dataset_id(config: dict[str, Any] | None = None) -> str:
    """Return the configured TEND Hugging Face dataset id."""
    _load_env()
    if config is None:
        config = load_config()
    return (
        os.environ.get("TEND_DATASET_ID")
        or config.get("datasets", {}).get("tend", {}).get("dataset_id")
        or DEFAULT_TEND_DATASET_ID
    )


def get_training_config(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the training section from config with env-aware defaults."""
    if config is None:
        config = load_config()
    return dict(config.get("training", {}))


def get_lora_config(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the LoRA section from config."""
    if config is None:
        config = load_config()
    return dict(config.get("lora", {}))


def get_adapter_name(config: dict[str, Any] | None = None) -> str | None:
    """Return configured adapter task name from env/config, if set."""
    _load_env()
    if config is None:
        config = load_config()
    return os.environ.get("MODEL_ADAPTER") or config.get("model", {}).get("adapter")


def get_adapter_run(config: dict[str, Any] | None = None) -> str | None:
    """Return configured adapter run folder (version/name) from env/config, if set."""
    _load_env()
    if config is None:
        config = load_config()
    return os.environ.get("MODEL_ADAPTER_RUN") or config.get("model", {}).get("adapter_run")


def get_adapter_path(
    task: str,
    config: dict[str, Any] | None = None,
    *,
    run: str | None = None,
) -> Path:
    """Resolve the LoRA adapter directory under ``models/checkpoints/<run>/<task>/``."""
    from src.utils.paths import get_adapter_checkpoint_path

    normalized = task.strip().lower()
    if normalized not in TRAINING_TASKS:
        allowed = ", ".join(sorted(TRAINING_TASKS))
        raise ValueError(f"Unknown training task '{task}'. Expected one of: {allowed}")
    resolved_run = run if run is not None else get_adapter_run(config)
    return get_adapter_checkpoint_path(normalized, resolved_run)
