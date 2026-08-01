"""Base model loading and LoRA adapter configuration (Unsloth 4-bit)."""
from typing import Sequence

from config.config import CFG
from utils.helpers import log_gpu_info
from utils.logger import logger


def load_base_model(model_name: str = CFG.MODEL_NAME, max_seq_length: int = CFG.MAX_LENGTH, load_in_4bit: bool = True):
    """Load a 4-bit base (or already fine-tuned/merged) model + tokenizer via Unsloth."""
    from unsloth import FastLanguageModel

    logger.info("Loading model '%s' (max_seq_length=%d, 4bit=%s) ...",
                model_name, max_seq_length, load_in_4bit)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        load_in_4bit=load_in_4bit,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    logger.info("Model loaded. EOS token id=%s", tokenizer.eos_token_id)
    log_gpu_info("after model load")
    return model, tokenizer


def configure_lora(
    base_model,
    r: int = CFG.LORA_R,
    lora_alpha: int = CFG.LORA_ALPHA,
    lora_dropout: float = CFG.LORA_DROPOUT,
    bias: str = CFG.LORA_BIAS,
    target_modules: Sequence[str] = CFG.LORA_TARGET_MODULES,
    max_seq_length: int = CFG.MAX_LENGTH,
    random_state: int = CFG.SEED,
):
    """Attach a LoRA adapter to `base_model` and log trainable parameters."""
    from unsloth import FastLanguageModel

    logger.info("Configuring LoRA (r=%d, alpha=%d, dropout=%s) ...",
                r, lora_alpha, lora_dropout)
    peft_model = FastLanguageModel.get_peft_model(
        base_model,
        r=r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        bias=bias,
        target_modules=list(target_modules),
        use_gradient_checkpointing="unsloth",
        max_seq_length=max_seq_length,
        random_state=random_state,
    )
    peft_model.print_trainable_parameters()
    return peft_model


def load_finetuned_model(repo_or_path: str, max_seq_length: int = CFG.MAX_LENGTH):
    """Load an already fine-tuned / merged model for inference (no LoRA attached)."""
    return load_base_model(model_name=repo_or_path, max_seq_length=max_seq_length, load_in_4bit=True)
