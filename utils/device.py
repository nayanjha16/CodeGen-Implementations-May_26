"""PyTorch device utilities with Apple Silicon (MPS) support."""

from __future__ import annotations

import platform

import torch


def is_mps_available() -> bool:
    """Return True when PyTorch can use the Mac GPU (Metal / MPS)."""
    return (
        hasattr(torch.backends, "mps")
        and torch.backends.mps.is_built()
        and torch.backends.mps.is_available()
    )


def _mps_supports_bf16() -> bool:
    if not is_mps_available():
        return False
    if hasattr(torch.backends.mps, "is_macos_or_newer"):
        return torch.backends.mps.is_macos_or_newer(14, 0)
    return False


def get_best_device(requested: str | None = None) -> str:
    """
    Resolve the best available device.

    Priority: explicit request > CUDA > MPS (Mac GPU) > CPU.
    Use requested='auto' or None for automatic selection.
    """
    if requested and requested not in ("auto", ""):
        if requested == "mps" and not is_mps_available():
            raise RuntimeError(
                "MPS was requested but is not available. "
                "Requires Apple Silicon and a PyTorch build with MPS support."
            )
        if requested == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is not available.")
        return requested

    if torch.cuda.is_available():
        return "cuda"
    if is_mps_available():
        return "mps"
    return "cpu"


def get_inference_dtype(device: str) -> torch.dtype:
    """Pick a safe dtype for inference on the given device."""
    if device == "cuda":
        return torch.float16
    if device == "mps":
        return torch.bfloat16 if _mps_supports_bf16() else torch.float32
    return torch.float32


def get_training_precision(device: str) -> dict[str, bool]:
    """
    Return fp16/bf16 flags for HuggingFace Trainer on the given device.

    MPS does not support fp16 training reliably; use bf16 on macOS 14+.
    """
    if device == "cuda":
        return {"fp16": True, "bf16": False}
    if device == "mps":
        if _mps_supports_bf16():
            return {"fp16": False, "bf16": True}
        return {"fp16": False, "bf16": False}
    return {"fp16": False, "bf16": False}


def describe_device(device: str) -> str:
    """Human-readable device description for logging."""
    if device == "mps":
        chip = platform.processor() or "Apple Silicon"
        return f"mps ({chip})"
    if device == "cuda" and torch.cuda.is_available():
        return f"cuda ({torch.cuda.get_device_name(0)})"
    if device == "cuda":
        return "cuda"
    return "cpu"


def apply_mac_training_overrides(config: dict, device: str) -> dict:
    """Adjust training config for Apple Silicon when using MPS."""
    if device != "mps":
        return config

    updated = dict(config)
    precision = get_training_precision(device)
    updated["fp16"] = precision["fp16"]
    updated["bf16"] = precision["bf16"]

    # MPS unified memory is smaller than datacenter GPUs
    if updated.get("per_device_train_batch_size", 8) > 4:
        updated["per_device_train_batch_size"] = 4
    if updated.get("per_device_eval_batch_size", 8) > 4:
        updated["per_device_eval_batch_size"] = 4
    if updated.get("gradient_accumulation_steps", 4) < 8:
        updated["gradient_accumulation_steps"] = 8

    return updated
