"""Embedding-based semantic similarity for documentation evaluation."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

import numpy as np

logger = logging.getLogger("codegen")


@lru_cache(maxsize=1)
def _load_embedding_model(model_name: str) -> tuple[Any, Any]:
    from transformers import AutoModel, AutoTokenizer

    from src.models.model_loader import ensure_model_cached, is_model_cached

    model_path = ensure_model_cached(model_name, causal=False)
    resolved = str(model_path) if is_model_cached(model_path) else model_name
    tokenizer = AutoTokenizer.from_pretrained(resolved)
    model = AutoModel.from_pretrained(resolved)
    model.eval()
    return tokenizer, model


def _mean_pool(last_hidden_state: Any, attention_mask: Any) -> Any:
    import torch

    mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
    summed = torch.sum(last_hidden_state * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts


def _encode_text(text: str, *, model_name: str) -> np.ndarray:
    import torch

    from src.utils.device import resolve_device

    tokenizer, model = _load_embedding_model(model_name)
    device = resolve_device()
    model.to(device)

    encoded = tokenizer(
        text,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt",
    )
    encoded = {key: value.to(device) for key, value in encoded.items()}

    with torch.no_grad():
        outputs = model(**encoded)
        pooled = _mean_pool(outputs.last_hidden_state, encoded["attention_mask"])
        vector = pooled[0].cpu().numpy()

    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def cosine_similarity(predicted: str, reference: str, *, model_name: str) -> float:
    """Return cosine similarity between two documentation texts."""
    pred = (predicted or "").strip()
    ref = (reference or "").strip()
    if not pred or not ref:
        return 0.0

    try:
        pred_vec = _encode_text(pred, model_name=model_name)
        ref_vec = _encode_text(ref, model_name=model_name)
        score = float(np.dot(pred_vec, ref_vec))
        return max(0.0, min(1.0, score))
    except Exception as exc:
        logger.warning("Embedding similarity failed (%s); returning 0.0", exc)
        return 0.0


def embedding_similarity_batch(
    predictions: list[str],
    references: list[str],
    *,
    model_name: str,
) -> float:
    if not predictions:
        return 0.0
    scores = [
        cosine_similarity(pred, ref, model_name=model_name)
        for pred, ref in zip(predictions, references)
    ]
    return sum(scores) / len(scores)
