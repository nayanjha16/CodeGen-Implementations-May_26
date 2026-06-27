from pathlib import Path
from text2sql.types import Example, GenResult
from text2sql.evaluate.runner import evaluate_results

DB = Path(__file__).parents[1] / "data" / "fixtures" / "spider_mini" / "database" / "concert_singer" / "concert_singer.sqlite"

def test_aggregates_ex_and_bleu():
    ex = Example("concert_singer", "How many singers?", "SELECT count(*) FROM singer")
    results = [GenResult(example=ex, raw_output="SELECT count(*) FROM singer", sql="SELECT count(*) FROM singer")]
    metrics = evaluate_results(results, db_path_fn=lambda db: DB,
                               metrics=["ex", "bleu", "component_f1"], judge_runner=None)
    assert metrics["ex"] == 1.0
    assert metrics["bleu"] > 90
    assert metrics["component_f1"] == 1.0


def test_benchmark_threads_into_ex():
    # gold returns 2 rows; pred collapses to 1. Spider(multiset)=mismatch, BIRD(set)=match.
    from text2sql.types import Example, GenResult
    ex = Example("concert_singer", "q", "SELECT 1 FROM singer")
    results = [GenResult(example=ex, raw_output="", sql="SELECT DISTINCT 1 FROM singer")]
    spider = evaluate_results(results, db_path_fn=lambda db: DB, metrics=["ex"], benchmark="spider")
    bird = evaluate_results(results, db_path_fn=lambda db: DB, metrics=["ex"], benchmark="bird")
    assert spider["ex"] == 0.0
    assert bird["ex"] == 1.0
