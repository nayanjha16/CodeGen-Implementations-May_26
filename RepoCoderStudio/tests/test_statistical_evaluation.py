from src.statistical_evaluation import bootstrap_ci, paired_rag_effect


def test_bootstrap_ci_is_deterministic_and_bounded():
    first = bootstrap_ci([0, 1, 1, 1], resamples=500, seed=7)
    second = bootstrap_ci([0, 1, 1, 1], resamples=500, seed=7)
    assert first == second
    assert 0 <= first["lower"] <= first["mean"] <= first["upper"] <= 1


def test_paired_effect_reports_wins_and_direction():
    effect = paired_rag_effect([0.1, 0.2, 0.3], [0.2, 0.4, 0.5], resamples=500)
    assert effect["wins"] == 3
    assert effect["losses"] == 0
    assert effect["mean"] > 0
