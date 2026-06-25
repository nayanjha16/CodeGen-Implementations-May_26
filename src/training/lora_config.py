"""Build PEFT LoRA configuration from project YAML."""

from __future__ import annotations

from typing import Any

from peft import LoraConfig, TaskType

from src.utils.config import get_lora_config


def build_lora_config(config: dict[str, Any] | None = None) -> LoraConfig:
    """Return a `LoraConfig` using verified `target_modules` from config."""
    lora_cfg = get_lora_config(config)
    target_modules = list(lora_cfg.get("target_modules") or [])
    if not target_modules:
        raise ValueError("lora.target_modules is empty in config.")

    return LoraConfig(
        r=int(lora_cfg.get("r", 16)),
        lora_alpha=int(lora_cfg.get("lora_alpha", 32)),
        lora_dropout=float(lora_cfg.get("lora_dropout", 0.05)),
        bias=str(lora_cfg.get("bias", "none")),
        target_modules=target_modules,
        task_type=TaskType.CAUSAL_LM,
    )
