"""Validation-only tuning for the adaptive corpus-RAG policy.

The test split must never decide which tasks receive RAG or how many examples
are injected. This module selects that policy from paired validation results,
then the frozen mapping can be applied once to the untouched test split.
"""

from __future__ import annotations

from typing import Dict, Iterable, Mapping, Sequence, Tuple

import numpy as np
import pandas as pd


PRIMARY_METRIC_BY_TASK = {
    "T1": "primary_success",
    "T2": "primary_success",
    "T3": "primary_success",
    "T4": "primary_success",
    "T5": "rouge_l",
    "T6": "rouge_l",
}


def _paired_frame(
    no_rag_rows: Sequence[dict],
    rag_rows: Sequence[dict],
    task_id: str,
) -> pd.DataFrame:
    metric = PRIMARY_METRIC_BY_TASK[task_id]
    left = pd.DataFrame(
        [
            {
                "corpus_id": row.get("corpus_id"),
                "no_rag": row.get(metric),
            }
            for row in no_rag_rows
            if row.get("task_id") == task_id
        ]
    )
    right = pd.DataFrame(
        [
            {
                "corpus_id": row.get("corpus_id"),
                "with_rag": row.get(metric),
                "rag_used": bool(row.get("rag_used")),
            }
            for row in rag_rows
            if row.get("task_id") == task_id
        ]
    )
    if left.empty or right.empty:
        return pd.DataFrame()
    paired = left.merge(right, on="corpus_id", how="inner", validate="one_to_one")
    if len(paired) != len(left) or len(paired) != len(right):
        raise ValueError(
            f"Validation rows for {task_id} are not a complete one-to-one pair: "
            f"no_rag={len(left)}, with_rag={len(right)}, paired={len(paired)}"
        )
    paired["no_rag"] = pd.to_numeric(paired["no_rag"], errors="coerce")
    paired["with_rag"] = pd.to_numeric(paired["with_rag"], errors="coerce")
    paired = paired.dropna(subset=["no_rag", "with_rag"])
    paired["delta"] = paired["with_rag"] - paired["no_rag"]
    return paired


def select_adaptive_rag_policy(
    no_rag_rows: Sequence[dict],
    rag_rows_by_top_k: Mapping[int, Sequence[dict]],
    *,
    min_delta: float = 0.01,
    min_rag_use_rate: float = 0.50,
    bootstrap_samples: int = 2000,
    bootstrap_seed: int = 42,
    confidence_level: float = 0.95,
    min_positive_probability: float = 0.80,
    min_selection_stability: float = 0.70,
    tasks: Iterable[str] = ("T1", "T2", "T3", "T4", "T5", "T6"),
) -> Tuple[Dict[str, int], pd.DataFrame]:
    """Select a stable positive validation arm independently for each task.

    Candidate arms are bootstrapped jointly by ``corpus_id`` so the paired
    no-RAG/top-k comparison is preserved. A task is enabled only when its best
    observed candidate:

    - clears the mean-lift and context-use gates;
    - has a strictly positive lower paired confidence bound;
    - has sufficient probability of clearing ``min_delta``; and
    - wins often enough across joint bootstrap resamples.

    An uncertain task is reported as ``inconclusive`` and conservatively maps
    to ``top_k=0``. ``disabled`` is reserved for evidence whose upper bound is
    below the meaningful-lift threshold (or whose context-use gate fails).
    The returned mapping is safe to freeze and apply to the test split once.
    """

    if bootstrap_samples < 100:
        raise ValueError("bootstrap_samples must be at least 100")
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must be between 0 and 1")
    if not 0.0 <= min_positive_probability <= 1.0:
        raise ValueError("min_positive_probability must be between 0 and 1")
    if not 0.0 <= min_selection_stability <= 1.0:
        raise ValueError("min_selection_stability must be between 0 and 1")

    policy: Dict[str, int] = {}
    report_rows = []
    for task_position, task_id in enumerate(tasks):
        if task_id not in PRIMARY_METRIC_BY_TASK:
            raise ValueError(f"Unsupported task for RAG policy tuning: {task_id}")

        candidates = []
        candidate_frames = {}
        for top_k, rag_rows in sorted(rag_rows_by_top_k.items()):
            if int(top_k) <= 0:
                continue
            paired = _paired_frame(no_rag_rows, rag_rows, task_id)
            if paired.empty:
                continue
            candidate_frames[int(top_k)] = paired.set_index("corpus_id")

        if candidate_frames:
            top_k_values = sorted(candidate_frames)
            reference_ids = list(candidate_frames[top_k_values[0]].index)
            reference_set = set(reference_ids)
            for top_k in top_k_values[1:]:
                candidate_ids = set(candidate_frames[top_k].index)
                if candidate_ids != reference_set:
                    raise ValueError(
                        f"Validation candidate arms for {task_id} do not use "
                        f"the same corpus_id pairs: top_k={top_k}"
                    )
                candidate_frames[top_k] = candidate_frames[top_k].loc[reference_ids]

            n = len(reference_ids)
            rng = np.random.default_rng(bootstrap_seed + task_position)
            sampled_indices = rng.integers(
                0,
                n,
                size=(bootstrap_samples, n),
            )
            bootstrap_by_top_k = {}
            alpha = (1.0 - confidence_level) / 2.0

            for top_k in top_k_values:
                paired = candidate_frames[top_k]
                deltas = paired["delta"].to_numpy(dtype=float)
                rag_used = paired["rag_used"].to_numpy(dtype=float)
                sampled_deltas = deltas[sampled_indices]
                bootstrap_mean_delta = sampled_deltas.mean(axis=1)
                bootstrap_win_rate = (sampled_deltas > 0).mean(axis=1)
                bootstrap_use_rate = rag_used[sampled_indices].mean(axis=1)
                ci_lower, ci_upper = np.quantile(
                    bootstrap_mean_delta,
                    [alpha, 1.0 - alpha],
                )
                bootstrap_by_top_k[top_k] = {
                    "mean_delta": bootstrap_mean_delta,
                    "win_rate": bootstrap_win_rate,
                    "use_rate": bootstrap_use_rate,
                }
                candidates.append(
                    {
                        "top_k": top_k,
                        "n": int(n),
                        "metric": PRIMARY_METRIC_BY_TASK[task_id],
                        "no_rag_mean": float(paired["no_rag"].mean()),
                        "with_rag_mean": float(paired["with_rag"].mean()),
                        "paired_mean_delta": float(deltas.mean()),
                        "paired_win_rate": float((deltas > 0).mean()),
                        "rag_use_rate": float(rag_used.mean()),
                        "delta_ci_lower": float(ci_lower),
                        "delta_ci_upper": float(ci_upper),
                        "positive_lift_probability": float(
                            (bootstrap_mean_delta >= min_delta).mean()
                        ),
                    }
                )

            selection_counts = {top_k: 0 for top_k in top_k_values}
            for sample_index in range(bootstrap_samples):
                eligible_top_k = [
                    top_k
                    for top_k in top_k_values
                    if bootstrap_by_top_k[top_k]["mean_delta"][sample_index]
                    >= min_delta
                    and bootstrap_by_top_k[top_k]["use_rate"][sample_index]
                    >= min_rag_use_rate
                ]
                if not eligible_top_k:
                    continue
                winner = max(
                    eligible_top_k,
                    key=lambda top_k: (
                        bootstrap_by_top_k[top_k]["mean_delta"][sample_index],
                        bootstrap_by_top_k[top_k]["win_rate"][sample_index],
                        -top_k,
                    ),
                )
                selection_counts[winner] += 1

            for row in candidates:
                row["selection_stability"] = float(
                    selection_counts[row["top_k"]] / bootstrap_samples
                )
                row["bootstrap_samples"] = int(bootstrap_samples)
                row["confidence_level"] = float(confidence_level)

        eligible = [
            row
            for row in candidates
            if row["paired_mean_delta"] >= min_delta
            and row["rag_use_rate"] >= min_rag_use_rate
        ]
        best_observed = max(
            eligible,
            key=lambda row: (
                row["paired_mean_delta"],
                row["paired_win_rate"],
                -row["top_k"],
            ),
            default=None,
        )
        stable_eligible = [
            row
            for row in eligible
            if row["delta_ci_lower"] > 0.0
            and row["positive_lift_probability"] >= min_positive_probability
            and row["selection_stability"] >= min_selection_stability
        ]
        best_stable = max(
            stable_eligible,
            key=lambda row: (
                row["paired_mean_delta"],
                row["paired_win_rate"],
                -row["top_k"],
            ),
            default=None,
        )
        enable = best_stable is not None
        selected_top_k = int(best_stable["top_k"]) if enable else 0
        policy[task_id] = selected_top_k

        if enable:
            decision_status = "enabled"
            selection_reason = "stable_positive_validation_lift"
        elif not candidates:
            decision_status = "inconclusive"
            selection_reason = "missing_validation_results"
        elif all(row["rag_use_rate"] < min_rag_use_rate for row in candidates):
            decision_status = "disabled"
            selection_reason = "insufficient_context_use"
        elif all(row["delta_ci_upper"] < min_delta for row in candidates):
            decision_status = "disabled"
            selection_reason = "validation_evidence_below_minimum_lift"
        else:
            decision_status = "inconclusive"
            selection_reason = "unstable_or_imprecise_validation_evidence"

        for row in candidates:
            report_rows.append(
                {
                    "task_id": task_id,
                    **row,
                    "best_observed_candidate": bool(
                        best_observed is not None
                        and row["top_k"] == best_observed["top_k"]
                    ),
                    "selected": row["top_k"] == selected_top_k and selected_top_k > 0,
                    "policy_top_k": selected_top_k,
                    "policy_decision": decision_status,
                    "selection_reason": selection_reason,
                }
            )
        if not candidates:
            report_rows.append(
                {
                    "task_id": task_id,
                    "top_k": None,
                    "n": 0,
                    "metric": PRIMARY_METRIC_BY_TASK[task_id],
                    "no_rag_mean": None,
                    "with_rag_mean": None,
                    "paired_mean_delta": None,
                    "paired_win_rate": None,
                    "rag_use_rate": None,
                    "delta_ci_lower": None,
                    "delta_ci_upper": None,
                    "positive_lift_probability": None,
                    "selection_stability": None,
                    "bootstrap_samples": int(bootstrap_samples),
                    "confidence_level": float(confidence_level),
                    "best_observed_candidate": False,
                    "selected": False,
                    "policy_top_k": 0,
                    "policy_decision": decision_status,
                    "selection_reason": selection_reason,
                }
            )

    return policy, pd.DataFrame(report_rows)
