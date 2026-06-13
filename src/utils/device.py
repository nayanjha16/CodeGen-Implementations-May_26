"""PyTorch device selection utilities."""

from __future__ import annotations


def resolve_device(device: str = "auto") -> str:
    """Return the best available device: cuda, then mps, then cpu."""
    if device != "auto":
        return device

    try:
        import torch
    except ImportError:
        return "cpu"

    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"
