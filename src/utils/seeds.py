"""Reproducibility seed utilities."""

from __future__ import annotations

import random
from typing import Any

import numpy as np


def set_seeds(config: dict[str, Any] | None = None, seeds: dict[str, int] | None = None) -> None:
    """Set random seeds for random, numpy, and torch."""
    if seeds is None:
        seeds = (config or {}).get("seeds", {})

    random_seed = seeds.get("random", 42)
    numpy_seed = seeds.get("numpy", 42)
    torch_seed = seeds.get("torch", 42)

    random.seed(random_seed)
    np.random.seed(numpy_seed)

    try:
        import torch

        torch.manual_seed(torch_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(torch_seed)
    except ImportError:
        pass
