import pytest

from src.evaluation_statistics import paired_bootstrap_delta


def test_paired_bootstrap_reports_positive_lift():
    result = paired_bootstrap_delta([0.1, 0.2, 0.3], [0.2, 0.4, 0.5], samples=200)
    assert result["n"] == 3
    assert result["delta"] > 0


def test_paired_bootstrap_allows_two_empty_arms():
    result = paired_bootstrap_delta([], [])
    assert result == {
        "n": 0,
        "delta": None,
        "ci95_low": None,
        "ci95_high": None,
    }


def test_paired_bootstrap_rejects_mismatched_arms():
    with pytest.raises(ValueError, match="both must be the same length"):
        paired_bootstrap_delta([0.1, 0.2], [0.3])
