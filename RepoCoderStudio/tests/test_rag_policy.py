from src.rag_policy import select_adaptive_rag_policy


def _rows(task_id, values, rag_used=False):
    return [
        {
            "task_id": task_id,
            "corpus_id": f"{task_id}-{index}",
            "primary_success": value,
            "rouge_l": value,
            "rag_used": rag_used,
        }
        for index, value in enumerate(values)
    ]


def test_validation_policy_selects_positive_arm_and_disables_regression():
    no_rag = _rows("T1", [0] * 20) + _rows("T2", [1] * 20)
    top1 = _rows("T1", [1] * 20, True) + _rows("T2", [0] * 20, True)
    top2 = _rows("T1", [1] * 15 + [0] * 5, True) + _rows(
        "T2", [1] * 10 + [0] * 10, True
    )

    policy, report = select_adaptive_rag_policy(
        no_rag,
        {1: top1, 2: top2},
        min_delta=0.01,
        bootstrap_samples=500,
        tasks=("T1", "T2"),
    )

    assert policy == {"T1": 1, "T2": 0}
    assert report.loc[report["selected"], "task_id"].tolist() == ["T1"]
    decisions = report.groupby("task_id")["policy_decision"].first().to_dict()
    assert decisions == {"T1": "enabled", "T2": "disabled"}
    selected = report.loc[report["selected"]].iloc[0]
    assert selected["delta_ci_lower"] > 0
    assert selected["selection_stability"] >= 0.70


def test_validation_policy_requires_actual_context_use():
    no_rag = _rows("T1", [0] * 20)
    apparent_gain_without_context = _rows("T1", [1] * 20, False)

    policy, report = select_adaptive_rag_policy(
        no_rag,
        {1: apparent_gain_without_context},
        min_delta=0.01,
        min_rag_use_rate=0.5,
        bootstrap_samples=500,
        tasks=("T1",),
    )

    assert policy == {"T1": 0}
    assert report.iloc[0]["policy_decision"] == "disabled"
    assert report.iloc[0]["selection_reason"] == "insufficient_context_use"


def test_validation_policy_marks_unstable_result_inconclusive():
    no_rag = _rows("T1", [0, 1] * 10)
    unstable = _rows("T1", [1, 0] * 10, True)

    policy, report = select_adaptive_rag_policy(
        no_rag,
        {1: unstable},
        min_delta=0.01,
        bootstrap_samples=1000,
        bootstrap_seed=7,
        tasks=("T1",),
    )

    assert policy == {"T1": 0}
    assert report.iloc[0]["policy_decision"] == "inconclusive"
    assert report.iloc[0]["selection_reason"] == (
        "unstable_or_imprecise_validation_evidence"
    )
    assert report.iloc[0]["delta_ci_lower"] < 0
    assert report.iloc[0]["delta_ci_upper"] > 0


def test_bootstrap_selection_is_deterministic_for_fixed_seed():
    no_rag = _rows("T1", [0] * 12 + [1] * 8)
    top1 = _rows("T1", [1] * 14 + [0] * 6, True)
    top2 = _rows("T1", [1] * 13 + [0] * 7, True)

    first_policy, first_report = select_adaptive_rag_policy(
        no_rag,
        {1: top1, 2: top2},
        bootstrap_samples=500,
        bootstrap_seed=123,
        tasks=("T1",),
    )
    second_policy, second_report = select_adaptive_rag_policy(
        no_rag,
        {1: top1, 2: top2},
        bootstrap_samples=500,
        bootstrap_seed=123,
        tasks=("T1",),
    )

    assert first_policy == second_policy
    columns = [
        "top_k",
        "delta_ci_lower",
        "delta_ci_upper",
        "positive_lift_probability",
        "selection_stability",
        "policy_decision",
    ]
    assert first_report[columns].equals(second_report[columns])
