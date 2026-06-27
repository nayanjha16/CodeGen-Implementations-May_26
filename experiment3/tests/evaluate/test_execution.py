import pytest
from pathlib import Path
from text2sql.evaluate.execution import ex_match, ts_match, ves_score

DB = Path(__file__).parents[1] / "data" / "fixtures" / "spider_mini" / "database" / "concert_singer" / "concert_singer.sqlite"

def test_ex_match_true_for_equivalent_results():
    assert ex_match("SELECT count(*) FROM singer", "SELECT COUNT(*) FROM singer", DB, benchmark="spider") is True

def test_ex_match_false_for_different_results():
    assert ex_match("SELECT count(*) FROM singer", "SELECT name FROM singer", DB, benchmark="spider") is False

def test_ex_match_order_insensitive():
    a = "SELECT name FROM singer ORDER BY name ASC"
    b = "SELECT name FROM singer ORDER BY name DESC"
    assert ex_match(a, b, DB, benchmark="spider") is True  # same rows, different order

def test_ex_match_false_on_invalid_sql():
    assert ex_match("SELECT nonexistent FROM nope", "SELECT count(*) FROM singer", DB, benchmark="spider") is False

def test_spider_preserves_duplicates():
    # gold returns two rows; pred collapses to one -> NOT a match under Spider multiset semantics
    pred = "SELECT DISTINCT 1 FROM singer"
    gold = "SELECT 1 FROM singer"
    assert ex_match(pred, gold, DB, benchmark="spider") is False

def test_bird_ignores_duplicates():
    # the SAME case IS a match under BIRD set-of-rows semantics
    pred = "SELECT DISTINCT 1 FROM singer"
    gold = "SELECT 1 FROM singer"
    assert ex_match(pred, gold, DB, benchmark="bird") is True

def test_ves_zero_when_incorrect():
    assert ves_score("SELECT name FROM singer", "SELECT count(*) FROM singer", DB, benchmark="spider") == 0.0

def test_ves_positive_when_correct():
    assert ves_score("SELECT count(*) FROM singer", "SELECT count(*) FROM singer", DB, benchmark="spider") > 0.0


def test_ts_match_requires_all_dbs():
    # same DB twice -> all hold; identical query matches itself
    assert ts_match("SELECT count(*) FROM singer", "SELECT count(*) FROM singer",
                    [DB, DB], benchmark="spider") is True
    # a wrong prediction fails the suite
    assert ts_match("SELECT name FROM singer", "SELECT count(*) FROM singer",
                    [DB, DB], benchmark="spider") is False


def test_unknown_benchmark_raises():
    with pytest.raises(ValueError):
        ex_match("SELECT count(*) FROM singer", "SELECT count(*) FROM singer",
                 DB, benchmark="spdier")
