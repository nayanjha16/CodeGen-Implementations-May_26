"""Reusable, model-agnostic helper functions (seeding, GPU logging, memory)."""
import gc
import random
from datetime import datetime

import numpy as np
import torch

from utils.logger import logger


def set_global_seed(seed: int) -> None:
    """Seed Python, NumPy, PyTorch and (if importable) HF Transformers RNGs."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    try:
        from transformers import set_seed as hf_set_seed
        hf_set_seed(seed)
    except Exception:
        pass
    logger.info("Global seed set to %d", seed)


def get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def get_run_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def log_gpu_info(tag: str = "") -> None:
    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        allocated = torch.cuda.memory_allocated() / 1e9
        reserved = torch.cuda.memory_reserved() / 1e9
        total = torch.cuda.get_device_properties(0).total_memory / 1e9
        logger.info(
            "GPU [%s] %s | %.2f GB allocated, %.2f GB reserved, %.1f GB total",
            tag, name, allocated, reserved, total,
        )
    else:
        logger.warning("CUDA not available - running on CPU (training will be very slow).")


def free_memory(tag: str = "") -> None:
    """Run GC and empty the CUDA cache. Callers should ``del`` their own
    large objects (models/tensors) before calling this."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    log_gpu_info(tag or "after free_memory")
