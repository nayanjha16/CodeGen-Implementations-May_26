"""Small-sample paired uncertainty estimates for RAG comparisons."""

from __future__ import annotations

import random
from typing import Dict, Iterable, List


def paired_bootstrap_delta(
    without_rag: Iterable[float],
    with_rag: Iterable[float],
    samples: int = 2000,
    seed: int = 42,
) -> Dict[str, float | int | None]:
    before: List[float] = list(without_rag)
    after: List[float] = list(with_rag)
    if len(before) != len(after):
        raise ValueError(
            f"paired_bootstrap_delta: without_rag has {len(before)} values but "
            f"with_rag has {len(after)} -- both must be the same length and "
            "paired by row."
        )
    if not before:
        return {"n": 0, "delta": None, "ci95_low": None, "ci95_high": None}
    deltas = [a - b for a, b in zip(after, before, strict=True)]
    rng = random.Random(seed)
    means = []
    n = len(deltas)
    for _ in range(samples):
        means.append(sum(deltas[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    low = means[int(0.025 * (samples - 1))]
    high = means[int(0.975 * (samples - 1))]
    return {
        "n": n,
        "delta": round(sum(deltas) / n, 6),
        "ci95_low": round(low, 6),
        "ci95_high": round(high, 6),
    }
