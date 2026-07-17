"""PEFT LoRA configuration for codegen-350M-multi fine-tuning."""

from typing import Any, cast

from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM

BASE_MODEL = "Salesforce/codegen-350M-multi"

# CodeGen uses GPT-NeoX architecture; target attention + MLP projections
LORA_TARGET_MODULES = [
    "query_key_value",
    "dense",
    "dense_h_to_4h",
    "dense_4h_to_h",
]

# Qwen2.5 (Llama-style) attention + MLP projection module names
QWEN_TARGET_MODULES = [
    "q_proj",
    "k_proj",
    "v_proj",
    "o_proj",
    "gate_proj",
    "up_proj",
    "down_proj",
]


def get_lora_config(
    r: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.05,
    target_modules: list[str] | None = None,
) -> LoraConfig:
    return LoraConfig(
        r=r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=target_modules or LORA_TARGET_MODULES,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )


def load_base_model(model_name: str = BASE_MODEL, device: str | None = None):
    """Load base model onto the best available device (CUDA > MPS > CPU)."""
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

    from utils.device import get_best_device, get_inference_dtype

    resolved_device = get_best_device(device)
    dtype = get_inference_dtype(resolved_device)
    # HF from_pretrained returns a dynamic union the type-checker cannot
    # reconcile with nn.Module's .to(); cast to Any (same pattern as
    # inference/generator.py) to avoid a false-positive type error.
    model: Any = cast(
        Any,
        AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=dtype,
        ),
    )
    if resolved_device != "cpu":
        model = model.to(resolved_device)
    return model


def apply_lora(model, lora_config: LoraConfig | None = None):
    config = lora_config or get_lora_config()
    model = get_peft_model(model, config)
    model.print_trainable_parameters()
    return model
