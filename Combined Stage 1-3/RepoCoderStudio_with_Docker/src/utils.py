"""
============================================================
RepoCoder Studio
utils.py
============================================================

Shared utility functions used across the project.
"""

import hashlib
import json
import random
import time
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, List


def now_timestamp() -> str:
    """Returns a compact timestamp for run IDs and artifact names."""
    return time.strftime("%Y%m%d_%H%M%S")


def sha1_text(text: str) -> str:
    """Creates a deterministic SHA1 hash for a text value."""
    return hashlib.sha1((text or "").encode("utf-8", errors="ignore")).hexdigest()


def stable_id(prefix: str, *parts: str, length: int = 16) -> str:
    """Creates a deterministic ID from multiple text parts."""
    joined = "::".join(str(p or "") for p in parts)
    return f"{prefix}_{sha1_text(joined)[:length]}"


def dataclass_to_dict(obj: Any) -> Dict[str, Any]:
    """Converts a dataclass object into a dictionary."""
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, dict):
        return obj
    raise TypeError(f"Expected dataclass or dict, got: {type(obj)}")


def safe_preview(text: str, max_chars: int = 300) -> str:
    """Returns a shortened preview of long text for logs/reports."""
    text = str(text or "")
    return text if len(text) <= max_chars else text[:max_chars] + "..."


def normalize_whitespace(text: str) -> str:
    """Normalizes whitespace while preserving readable text."""
    return " ".join(str(text or "").split())


def ensure_non_empty(value: str, name: str):
    """Raises an assertion error if a required string is empty."""
    assert value is not None and str(value).strip(), f"{name} must not be empty"


def write_json(path: Path, data: Dict[str, Any]):
    """Writes dictionary data to JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path) -> Dict[str, Any]:
    """Reads JSON as a dictionary."""
    assert path.exists(), f"JSON file not found: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def set_random_seed(seed: int):
    """Sets Python, NumPy, and Torch seeds where available."""
    random.seed(seed)

    try:
        import numpy as np
        np.random.seed(seed)
    except Exception:
        pass

    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass
