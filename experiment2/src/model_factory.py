import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM
from peft import LoraConfig, get_peft_model, TaskType, PeftModel

from src.config import MODELS, get_device_settings
from src.logger import pipeline_logger


def load_model(model_type: str, checkpoint_path: str = None, mode: str = "train", load_base_only: bool = False):
    """
    Load (model, tokenizer) for the given model_type.

    Args:
        model_type:     "codegen" or "codet5"
        checkpoint_path: path to a saved LoRA adapter directory.
                         None  -> inject fresh LoRA layers for training.
                         str   -> load saved adapter for inference.
        mode:           "train" or "infer".
                        Affects CodeGen tokenizer padding side:
                        right-padding for training, left-padding for inference.
        load_base_only:  If True, returns the raw base model without any LoRA wrapping
                         (essential for unified training scripts handling custom adapters).

    Returns:
        (model, tokenizer)
    """
    cfg    = MODELS[model_type]
    dev    = get_device_settings()
    device = dev["device"]

    is_codegen = (model_type == "codegen")
    dtype      = dev["codegen_dtype"] if is_codegen else dev["codet5_dtype"]

    pipeline_logger.info("model_init", "load_start", stats={
        "model_type": model_type,
        "model_id": cfg["model_id"],
        "mode": mode,
        "device": device,
        "dtype": str(dtype),
        "checkpoint_path": checkpoint_path,
        "load_base_only": load_base_only
    })
    print(f"[model_factory] {model_type} | mode={mode} | device={device} | dtype={dtype}")

    # -----------------------------------------------------------------
    # Tokenizer Configuration
    # -----------------------------------------------------------------
    tokenizer = AutoTokenizer.from_pretrained(cfg["model_id"], additional_special_tokens=[])

    if is_codegen:
        # Left-pad for batched inference; right-pad during training
        tokenizer.padding_side = "left" if mode == "infer" else "right"
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

    pipeline_logger.info("model_init", "tokenizer_loaded", stats={
        "model_id": cfg["model_id"],
        "vocab_size": tokenizer.vocab_size,
        "padding_side": tokenizer.padding_side,
        "pad_token": tokenizer.pad_token
    })

    # -----------------------------------------------------------------
    # Base Model Extraction
    # -----------------------------------------------------------------
    load_kwargs = {"torch_dtype": dtype}  # Kept as standard torch_dtype to bypass signature mismatch crashes
    if device == "cuda":
        load_kwargs["device_map"] = "auto"

    load_kwargs["use_safetensors"] = False

    if is_codegen:
        base_model = AutoModelForCausalLM.from_pretrained(cfg["model_id"], **load_kwargs)
        # Sync the model configuration token IDs with the modified tokenizer values
        if tokenizer.pad_token_id is not None:
            base_model.config.pad_token_id = tokenizer.pad_token_id
    else:
        base_model = AutoModelForSeq2SeqLM.from_pretrained(cfg["model_id"], **load_kwargs)

    total_params = sum(p.numel() for p in base_model.parameters())
    pipeline_logger.info("model_init", "base_model_loaded", stats={
        "model_id": cfg["model_id"],
        "total_params": total_params,
        "total_params_M": round(total_params / 1e6, 1),
        "device": device,
        "dtype": str(dtype)
    })

    # Short-circuit and return immediately if the script wants manual LoRA execution
    if load_base_only:
        pipeline_logger.info("model_init", "base_only_return", stats={"reason": "load_base_only=True"})
        print("[model_factory] Returning raw base model context. LoRA injection bypassed.")
        return base_model, tokenizer

    # -----------------------------------------------------------------
    # LoRA / PEFT Orchestration Layer
    # -----------------------------------------------------------------
    task_type = TaskType.CAUSAL_LM if is_codegen else TaskType.SEQ_2_SEQ_LM

    if checkpoint_path and os.path.exists(checkpoint_path):
        # Explicitly flag whether the adapter layer should accept weight adjustments
        model = PeftModel.from_pretrained(base_model, checkpoint_path, is_trainable=(mode == "train"))
        pipeline_logger.info("model_init", "adapter_loaded_from_checkpoint", stats={
            "checkpoint_path": checkpoint_path,
            "is_trainable": (mode == "train")
        })
        print(f"[model_factory] Loaded active adapter checkpoint from: {checkpoint_path}")
    else:
        lora_cfg = LoraConfig(
            r              = cfg["lora_r"],
            lora_alpha     = cfg["lora_alpha"],
            lora_dropout   = cfg["lora_dropout"],
            target_modules = cfg["lora_targets"],
            bias           = "none",
            task_type      = task_type,
        )
        model = get_peft_model(base_model, lora_cfg)
        model.print_trainable_parameters()

        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        pipeline_logger.info("model_init", "fresh_lora_injected", stats={
            "lora_r": cfg["lora_r"],
            "lora_alpha": cfg["lora_alpha"],
            "lora_dropout": cfg["lora_dropout"],
            "target_modules": cfg["lora_targets"],
            "trainable_params": trainable_params,
            "trainable_params_M": round(trainable_params / 1e6, 3),
            "trainable_pct": round(trainable_params / total_params * 100, 3)
        })
        print(f"[model_factory] Injecting factory LoRA adapters targeting: {cfg['lora_targets']}")

    if device == "cpu":
        model = model.to("cpu")

    return model, tokenizer