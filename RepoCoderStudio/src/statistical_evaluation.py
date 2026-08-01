"""Deterministic confidence intervals and paired RAG effect estimates."""

from __future__ import annotations

import math
import random
from typing import Dict, Iterable, Optional


def mean(values: Iterable[float]) -> Optional[float]:
    values = list(values)
    return sum(values) / len(values) if values else None


def bootstrap_ci(
    values: Iterable[float],
    confidence: float = 0.95,
    resamples: int = 2000,
    seed: int = 42,
) -> Dict[str, Optional[float]]:
    values = [float(value) for value in values]
    if not values:
        return {"mean": None, "lower": None, "upper": None, "n": 0}
    if len(values) == 1:
        return {"mean": values[0], "lower": values[0], "upper": values[0], "n": 1}
    rng = random.Random(seed)
    samples = []
    for _ in range(max(100, resamples)):
        samples.append(sum(rng.choice(values) for _ in values) / len(values))
    samples.sort()
    alpha = (1.0 - confidence) / 2.0
    lower_index = max(0, int(math.floor(alpha * len(samples))))
    upper_index = min(len(samples) - 1, int(math.ceil((1.0 - alpha) * len(samples))) - 1)
    return {
        "mean": mean(values),
        "lower": samples[lower_index],
        "upper": samples[upper_index],
        "n": len(values),
    }


def paired_rag_effect(
    no_rag: Iterable[float],
    with_rag: Iterable[float],
    confidence: float = 0.95,
    resamples: int = 2000,
    seed: int = 42,
) -> Dict[str, object]:
    no_rag = list(no_rag)
    with_rag = list(with_rag)
    if len(no_rag) != len(with_rag):
        # zip() would otherwise silently drop the longer list's tail instead
        # of surfacing a caller bug (e.g. one side filtered, the other not).
        raise ValueError(
            f"paired_rag_effect: no_rag has {len(no_rag)} values but with_rag "
            f"has {len(with_rag)} -- both must be the same length and paired "
            "by row."
        )
    deltas = [float(rag) - float(base) for base, rag in zip(no_rag, with_rag, strict=True)]
    interval = bootstrap_ci(deltas, confidence, resamples, seed)
    wins = sum(delta > 0 for delta in deltas)
    ties = sum(delta == 0 for delta in deltas)
    losses = sum(delta < 0 for delta in deltas)
    interval.update(
        {
            "wins": wins,
            "ties": ties,
            "losses": losses,
            "win_rate": wins / len(deltas) if deltas else None,
            "interpretation": (
                "positive_ci" if interval["lower"] is not None and interval["lower"] > 0
                else "negative_ci" if interval["upper"] is not None and interval["upper"] < 0
                else "inconclusive"
            ),
        }
    )
    return interval
