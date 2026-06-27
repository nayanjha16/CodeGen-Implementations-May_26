"""pass@k estimator (Chen et al. 2021, "Evaluating Large Language Models Trained on Code").

The unbiased estimator answers: if we sample n completions per problem and c of them pass,
what is the probability that at least one of a random k-subset passes?

    pass@k = 1 - C(n-c, k) / C(n, k)

computed in the numerically stable product form. Requires n >= k.
"""
from __future__ import annotations

import itertools
from typing import Iterable, List, Union

import numpy as np


def _estimator(n: int, c: int, k: int) -> float:
    """Unbiased pass@k for a single problem: n samples, c correct, subset size k."""
    if n < k:
        raise ValueError(f"pass@{k} needs n>=k, got n={n}, k={k}")
    if n - c < k:
        # every k-subset must contain at least one correct sample
        return 1.0
    return 1.0 - float(np.prod(1.0 - k / np.arange(n - c + 1, n + 1)))


def pass_at_k(
    num_samples: Union[int, Iterable[int]],
    num_correct: Iterable[int],
    k: int,
) -> float:
    """Mean pass@k over a set of problems.

    num_samples: int (same n for all problems) or per-problem list of n.
    num_correct: per-problem count of passing samples (c).
    """
    correct = list(num_correct)
    if isinstance(num_samples, int):
        samples = [num_samples] * len(correct)
    else:
        samples = list(num_samples)
    if len(samples) != len(correct):
        raise ValueError("num_samples and num_correct length mismatch")
    return float(np.mean([_estimator(n, c, k) for n, c in zip(samples, correct)]))


if __name__ == "__main__":
    # quick self-check; the proper assertions live in tests/test_passk.py
    print("pass@1 (n=5,c=2):", round(_estimator(5, 2, 1), 4))
    print("pass@5 (n=10,c=1):", round(_estimator(10, 1, 5), 4))
