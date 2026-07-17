"""Local Hugging Face embedding model cache for schema selection."""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from tool.config import TOOL_DIR

LOCAL_DIR = TOOL_DIR / ".local"
DEFAULT_MODELS_DIR = LOCAL_DIR / "models"


def model_slug(model_name: str) -> str:
    """Convert a HuggingFace model id to a safe local directory name."""
    return re.sub(r"[^\w.\-]+", "__", model_name.replace("/", "__"))


def get_embedding_cache_dir() -> Path:
    """Return the directory used for persisted embedding model snapshots."""
    env = os.getenv("SCHEMA_EMBEDDING_CACHE_DIR", "").strip()
    if env:
        path = Path(env)
        return path if path.is_absolute() else TOOL_DIR / path
    return DEFAULT_MODELS_DIR


def get_embedding_model_dir(model_name: str) -> Path:
    """Return the on-disk path for a cached embedding model."""
    return get_embedding_cache_dir() / model_slug(model_name)


def is_embedding_model_cached(model_name: str) -> bool:
    """Return True when a complete local snapshot exists for the model."""
    cache_dir = get_embedding_model_dir(model_name)
    if not (cache_dir / "config.json").exists():
        return False
    if not (cache_dir / "modules.json").exists():
        return False
    weight_files = list(cache_dir.glob("*.safetensors")) + list(cache_dir.glob("pytorch_model*.bin"))
    return bool(weight_files)


def configure_hf_cache() -> Path:
    """Point Hugging Face libraries at a tool-local cache directory."""
    hf_home = LOCAL_DIR / "huggingface"
    hf_home.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("HF_HOME", str(hf_home))
    os.environ.setdefault("HF_HUB_CACHE", str(hf_home / "hub"))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(hf_home / "transformers"))
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(hf_home / "sentence_transformers"))
    get_embedding_cache_dir().mkdir(parents=True, exist_ok=True)
    return hf_home


def ensure_embedding_model_cached(model_name: str) -> Path:
    """Download the model once and persist a local snapshot for offline reuse."""
    cache_dir = get_embedding_model_dir(model_name)
    if is_embedding_model_cached(model_name):
        return cache_dir

    cache_dir.mkdir(parents=True, exist_ok=True)
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    model.save(str(cache_dir))
    (cache_dir / ".downloaded").touch()
    return cache_dir


@lru_cache(maxsize=2)
def load_sentence_model(model_name: str) -> Any:
    """Load a sentence-transformers model from the local cache without hub access."""
    cache_dir = ensure_embedding_model_cached(model_name)
    from sentence_transformers import SentenceTransformer

    previous_offline = os.environ.get("HF_HUB_OFFLINE")
    os.environ["HF_HUB_OFFLINE"] = "1"
    try:
        return SentenceTransformer(str(cache_dir), local_files_only=True)
    finally:
        if previous_offline is None:
            os.environ.pop("HF_HUB_OFFLINE", None)
        else:
            os.environ["HF_HUB_OFFLINE"] = previous_offline
