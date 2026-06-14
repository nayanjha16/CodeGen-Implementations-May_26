"""Configuration loading utilities."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from src.utils.paths import get_project_root


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

    datasets_cfg = _ensure_dict(config, "datasets")
    spider_cfg = _ensure_dict(datasets_cfg, "spider")
    bird_cfg = _ensure_dict(datasets_cfg, "bird")
    spider_cfg["cache_dir"] = os.environ.get("SPIDER_DATA_DIR", "data/spider")
    spider_cfg["repo_url"] = os.environ.get("SPIDER_REPO_URL")
    spider_cfg["dataset_url"] = os.environ.get("SPIDER_DATASET_URL")
    bird_cfg["cache_dir"] = os.environ.get("BIRD_DATA_DIR", "data/bird")
    bird_cfg["dataset_url"] = os.environ.get("BIRD_DATASET_URL")
    config["data_dir"] = os.environ.get("DATA_DIR", "data")

    eval_cfg = _ensure_dict(config, "evaluation")
    eval_cfg["bertscore_model"] = os.environ.get("BERTSCORE_MODEL_NAME")
    eval_cfg["qwen_evaluator_model"] = os.environ.get("QWEN_EVALUATOR_MODEL_NAME")

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


def get_qwen_evaluator_model_name(config: dict[str, Any] | None = None) -> str:
    """Return the configured Qwen evaluator model name from env/config."""
    _load_env()
    if config is None:
        config = load_config()
    name = (
        os.environ.get("QWEN_EVALUATOR_MODEL_NAME")
        or config.get("evaluation", {}).get("qwen_evaluator_model")
    )
    return name or "Qwen/Qwen2.5-0.5B-Instruct"


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


def get_spider_repo_url(config: dict[str, Any] | None = None) -> str:
    """Return Spider repository archive URL from env/config."""
    _load_env()
    if config is None:
        config = load_config()
    url = config.get("datasets", {}).get("spider", {}).get("repo_url") or os.environ.get(
        "SPIDER_REPO_URL"
    )
    if not url:
        return _require_env("SPIDER_REPO_URL")
    return url


def get_spider_dataset_url(config: dict[str, Any] | None = None) -> str:
    """Return Spider full dataset mirror URL from env/config."""
    _load_env()
    if config is None:
        config = load_config()
    url = config.get("datasets", {}).get("spider", {}).get("dataset_url") or os.environ.get(
        "SPIDER_DATASET_URL"
    )
    if not url:
        return _require_env("SPIDER_DATASET_URL")
    return url


def get_bird_dataset_url(config: dict[str, Any] | None = None) -> str:
    """Return BIRD dataset archive URL from env/config."""
    _load_env()
    if config is None:
        config = load_config()
    url = config.get("datasets", {}).get("bird", {}).get("dataset_url") or os.environ.get(
        "BIRD_DATASET_URL"
    )
    if not url:
        return _require_env("BIRD_DATASET_URL")
    return url
