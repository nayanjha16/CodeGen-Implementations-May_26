"""Tokenizer loading and encoding helpers shared by tasks, training, and RAG."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=4)
def load_tokenizer(pretrained_name: str = "Salesforce/codegen-350M-multi"):
    """Load (and cache) the codegen tokenizer, adding a pad token if missing."""
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(pretrained_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def encode_batch(
    texts: list[str],
    tokenizer: Any,
    max_length: int = 512,
    padding: str = "max_length",
    truncation: bool = True,
) -> dict[str, Any]:
    """Tokenize a batch of raw strings into model-ready tensors."""
    return tokenizer(
        texts,
        max_length=max_length,
        padding=padding,
        truncation=truncation,
        return_tensors="pt",
    )


def build_causal_lm_example(
    prompt: str,
    completion: str,
    tokenizer: Any,
    max_length: int = 512,
) -> dict[str, Any]:
    """Build a single (input_ids, attention_mask, labels) example for causal-LM
    fine-tuning where the loss is only computed on the ``completion`` tokens.
    """
    prompt_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    completion_ids = tokenizer(
        completion + tokenizer.eos_token, add_special_tokens=False
    )["input_ids"]

    input_ids = (prompt_ids + completion_ids)[:max_length]
    labels = ([-100] * len(prompt_ids) + completion_ids)[:max_length]

    pad_len = max_length - len(input_ids)
    attention_mask = [1] * len(input_ids) + [0] * pad_len
    input_ids = input_ids + [tokenizer.pad_token_id] * pad_len
    labels = labels + [-100] * pad_len

    import torch

    return {
        "input_ids": torch.tensor(input_ids, dtype=torch.long),
        "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
        "labels": torch.tensor(labels, dtype=torch.long),
    }
