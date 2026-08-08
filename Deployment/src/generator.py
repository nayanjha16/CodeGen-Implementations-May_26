"""Batched text generation for the student (plan §9 two-stage inference).

Greedy/beam decoding on MPS. Prompts are left-padded so the generated span can be
sliced off by prompt length uniformly; only the completion is decoded and
returned. ``generate_and_extract`` layers ``processor`` on top to return clean
queries per task.
"""

from __future__ import annotations

import logging

import torch

from . import config
from .device import get_device
from . import processor

log = logging.getLogger(__name__)


def generate(
    model,
    tokenizer,
    prompts: list[str],
    max_new_tokens: int | None = None,
    num_beams: int | None = None,
) -> list[str]:
    """Generate completions for a batch of prompts; return decoded completion text."""
    if not prompts:
        return []
    infer = config.CONFIG.infer
    max_new_tokens = max_new_tokens or infer.max_new_tokens
    num_beams = num_beams if num_beams is not None else infer.num_beams
    device = get_device()

    prev_side = tokenizer.padding_side
    tokenizer.padding_side = "left"  # so completion slice is uniform across the batch
    try:
        enc = tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=config.CONFIG.model.max_len,
        ).to(device)
        model.eval()
        with torch.no_grad():
            out = model.generate(
                **enc,
                max_new_tokens=max_new_tokens,
                num_beams=num_beams,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )
    finally:
        tokenizer.padding_side = prev_side

    gen = out[:, enc["input_ids"].shape[1]:]
    return tokenizer.batch_decode(gen, skip_special_tokens=True)


def generate_and_extract(
    model,
    tokenizer,
    prompts: list[str],
    task: str,
    max_new_tokens: int | None = None,
    num_beams: int | None = None,
) -> list[tuple[str | None, str]]:
    """Generate, then extract ``(analysis, query)`` per completion for ``task``."""
    completions = generate(model, tokenizer, prompts, max_new_tokens, num_beams)
    return [processor.extract(c, task) for c in completions]
