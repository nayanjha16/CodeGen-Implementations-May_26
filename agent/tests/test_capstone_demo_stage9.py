"""Stage 9 unit tests — capstone demo script (no live API/DB)."""

from __future__ import annotations

from agent.scripts.run_capstone_demo import (
    CAPSTONE_SCENARIOS,
    DEFAULT_IDS,
    DemoScenario,
    _select_scenarios,
)


def test_default_scenario_ids_exist() -> None:
    ids = {s.id for s in CAPSTONE_SCENARIOS}
    for scenario_id in DEFAULT_IDS:
        assert scenario_id in ids


def test_select_reliable_only() -> None:
    class Args:
        reliable_only = True
        ids = None

    selected = _select_scenarios(Args())
    assert all(s.reliable for s in selected)
    assert any(s.id == "D3" for s in selected)
    assert not any(s.id == "D2" for s in selected)


def test_sql2nosql_scenario_message() -> None:
    scenario = DemoScenario(
        "S1",
        "count",
        "sql2nosql",
        sql='SELECT COUNT(*) FROM "Customer"',
    )
    assert "Convert this SQL" in scenario.user_message()
    assert "Customer" in scenario.user_message()
