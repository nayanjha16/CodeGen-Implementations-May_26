from text2sql.models.base import StubRunner
from text2sql.evaluate.llm_judge import judge_score, judge_cell

def test_parses_rating_from_output():
    runner = StubRunner(responses=["Rating: 4\nThe query is mostly correct."])
    score = judge_score("question?", "SELECT a FROM t", "SELECT a FROM t", runner)
    assert score == 4

def test_clamps_out_of_range():
    runner = StubRunner(responses=["Rating: 9"])
    assert judge_score("q", "x", "y", runner) == 5

def test_defaults_to_one_when_unparseable():
    runner = StubRunner(responses=["no number here"])
    assert judge_score("q", "x", "y", runner) == 1

def test_judge_cell_averages_over_sample_limit():
    # limit=2 -> only first two rows scored: (5 + 3) / 2 = 4.0
    runner = StubRunner(responses=["Rating: 5", "Rating: 3", "Rating: 1"])
    pe = [{"question": "q", "pred": "p", "gold": "g"} for _ in range(3)]
    assert judge_cell(pe, runner, limit=2) == 4.0

def test_judge_cell_empty_returns_none():
    # empty per_example short-circuits to None without ever calling the runner
    assert judge_cell([], StubRunner(responses=["unused"]), limit=5) is None
