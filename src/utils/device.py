"""PyTorch device selection utilities."""

from __future__ import annotations

import logging
from typing import Final

logger = logging.getLogger(__name__)

_DIRECTML_ALIASES: Final[frozenset[str]] = frozenset({"dml", "directml"})


def directml_available() -> bool:
    """Return True when torch-directml is installed and reports a usable device."""
    try:
        import torch_directml
    except ImportError:
        return False
    return bool(torch_directml.is_available())


def resolve_directml_device() -> str:
    """Return the DirectML device string (typically ``privateuseone:0``)."""
    import torch_directml

    return str(torch_directml.device())


def is_directml_device(device: str) -> bool:
    """Return True when *device* refers to a DirectML / PrivateUse1 backend."""
    return device.lower().startswith("privateuseone")


def is_cpu_device(device: str) -> bool:
    """Return True when *device* is CPU."""
    return device.lower() == "cpu"


def supports_dataloader_pin_memory(device: str) -> bool:
    """Return True when PyTorch dataloader pin_memory is supported for *device*."""
    lowered = device.lower()
    return lowered == "cuda" or lowered.startswith("cuda:")


def normalize_device_request(device: str) -> str:
    """Normalize user-facing device aliases to concrete torch device strings."""
    lowered = device.strip().lower()
    if lowered in _DIRECTML_ALIASES:
        if directml_available():
            return resolve_directml_device()
        logger.warning("DirectML requested but torch-directml is not available; using CPU.")
        return "cpu"
    if lowered == "auto":
        return "auto"
    return device.strip()


def resolve_device(device: str = "auto") -> str:
    """Return the best available device: cuda, mps, directml, then cpu."""
    normalized = normalize_device_request(device)
    if normalized != "auto":
        return normalized

    try:
        import torch
    except ImportError:
        return "cpu"

    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    if directml_available():
        return resolve_directml_device()
    return "cpu"
