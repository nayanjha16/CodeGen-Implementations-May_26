"""Shared utilities."""

from utils.device import (
    describe_device,
    get_best_device,
    get_inference_dtype,
    get_training_precision,
    is_mps_available,
)

__all__ = [
    "describe_device",
    "get_best_device",
    "get_inference_dtype",
    "get_training_precision",
    "is_mps_available",
]
