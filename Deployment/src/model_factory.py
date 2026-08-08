"""Model + tokenizer construction: base CodeGen on MPS/bf16 with LoRA (plan §3).

Everything loads on ``mps`` in ``bfloat16`` via ``src.device`` — never gate on
CUDA (SPEC hard rules). LoRA (PEFT) targets CodeGen's projection names from
``config.ModelConfig.lora_target_modules``; changing the base model requires
changing those names too.

Three entry points:
- ``create_model()`` — fresh base + freshly-injected LoRA adapter (Pass 1).
- ``load_adapter(path, trainable=…)`` — base + an existing adapter, either as a
  resumable trainable model (Pass 2 arms resume from Pass 1) or eval-only (inference).
"""

from __future__ import annotations

import logging

import torch
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from . import config
from .device import get_device, get_dtype

log = logging.getLogger(__name__)


def load_tokenizer(base_model: str | None = None):
    """Load the tokenizer; ensure a pad token exists (CodeGen has none)."""
    name = base_model or config.CONFIG.model.base_model
    tok = AutoTokenizer.from_pretrained(name)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
        log.info("tokenizer had no pad_token; set pad_token = eos_token (%r)", tok.eos_token)
    return tok


def load_base_model(base_model: str | None = None):
    """Load the base causal LM on the resolved device in bf16."""
    name = base_model or config.CONFIG.model.base_model
    device, dtype = get_device(), get_dtype()
    log.info("loading base model %s (device=%s dtype=%s)", name, device.type, dtype)
    model = AutoModelForCausalLM.from_pretrained(name, dtype=dtype)
    model.to(device)
    # Keep the pad token consistent with the tokenizer default (eos). Some configs
    # (e.g. CodeGen on transformers 5.x) don't define pad_token_id at all.
    if getattr(model.config, "pad_token_id", None) is None:
        model.config.pad_token_id = model.config.eos_token_id
    return model


def _lora_config() -> LoraConfig:
    m = config.CONFIG.model
    return LoraConfig(
        r=m.lora_r,
        lora_alpha=m.lora_alpha,
        lora_dropout=m.lora_dropout,
        target_modules=list(m.lora_target_modules),
        bias="none",
        task_type="CAUSAL_LM",
    )


def log_trainable_params(model) -> tuple[int, int]:
    """Log and return (trainable, total) parameter counts."""
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    log.info(
        "trainable params: %s / %s (%.2f%%)",
        f"{trainable:,}", f"{total:,}", 100.0 * trainable / max(total, 1),
    )
    return trainable, total


def create_model(base_model: str | None = None):
    """Fresh base + newly-injected LoRA adapter (Pass 1 training)."""
    base = load_base_model(base_model)
    model = get_peft_model(base, _lora_config())
    log_trainable_params(model)
    return model


def load_adapter(adapter_path, base_model: str | None = None, trainable: bool = False):
    """Load base + an existing LoRA adapter.

    ``trainable=True`` returns a resumable model (Pass 2 resumes Pass 1's adapter);
    ``trainable=False`` returns an eval-only model for inference.
    """
    base = load_base_model(base_model)
    model = PeftModel.from_pretrained(base, str(adapter_path), is_trainable=trainable)
    if trainable:
        log_trainable_params(model)
    else:
        model.eval()
    return model


def free_model(model) -> None:
    """Release a model and empty the MPS cache (teacher/student memory discipline)."""
    del model
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
