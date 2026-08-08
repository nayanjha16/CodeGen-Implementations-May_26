"""Device and dtype selection for Apple Silicon (MPS) — portable for serving.

The training pipeline runs on the Mac's GPU via PyTorch's MPS backend — student
training and teacher inference alike. On the Mac ``torch.cuda.is_available()`` is
always False (see plan.md §2), so the ordering below resolves to **exactly** the
original MPS/CPU behaviour there.

Ordering is a strict superset added for the deployment/serving path (the model
UI must run on a Linux server that is CUDA-GPU or CPU-only, neither of which is
MPS): **CUDA → MPS → CPU**. CUDA is only ever selected when it is actually present
(i.e. on the server), never on the Mac, so no Mac run changes. This is the *safe*
form of CUDA-awareness the original hard rule guarded against: it never falls
through to CPU while a GPU (MPS) is available — MPS still strictly beats CPU.
"""

from __future__ import annotations

import logging
import os

import torch

logger = logging.getLogger(__name__)


def get_device() -> torch.device:
    """Return the compute device: ``cuda`` (server GPU) → ``mps`` (Mac) → ``cpu``.

    On the Mac CUDA is unavailable, so this returns ``mps`` exactly as before.
    """
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def get_dtype() -> torch.dtype:
    """Return the training/inference dtype.

    bf16 on a GPU (CUDA or Apple MPS). fp16 is numerically unstable on MPS; fp32
    doubles memory for no gain. On CPU fall back to fp32.
    """
    if torch.cuda.is_available() or torch.backends.mps.is_available():
        return torch.bfloat16
    return torch.float32


def enable_mps_cpu_fallback() -> None:
    """Allow ops MPS hasn't implemented to fall back to CPU instead of crashing.

    A silent CPU fallback is the most common cause of an inexplicably slow run,
    so callers should also watch for the warning this enables (log noise is the
    point — see ``warn_if_cpu_fallback``).
    """
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")


def describe() -> str:
    """One-line summary for startup logs (plan.md §13)."""
    dev = get_device()
    dt = get_dtype()
    mps = torch.backends.mps.is_available()
    cuda = torch.cuda.is_available()
    return (
        f"device={dev.type} dtype={str(dt).replace('torch.', '')} "
        f"cuda_available={cuda} mps_available={mps} torch={torch.__version__}"
    )
