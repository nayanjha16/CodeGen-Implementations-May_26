"""Tests for streamlined evaluation metrics."""

from __future__ import annotations

from src.evaluation.metrics import EvaluationMetrics


def test_exact_match_normalizes_whitespace():
    metrics = EvaluationMetrics()
    predicted = "select name from singer;"
    reference = "SELECT name FROM singer"
    assert metrics.exact_match(predicted, reference) is True


def test_evaluate_all_returns_canonical_keys():
    metrics = EvaluationMetrics()
    result = metrics.evaluate_all(
        ["SELECT 1"],
        ["SELECT 1"],
        [{"db_id": "concert_singer", "dataset": "spider"}],
    )
    assert set(result.keys()) == {
        "execution_accuracy",
        "exact_match",
        "structural_similarity",
    }
