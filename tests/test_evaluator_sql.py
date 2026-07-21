from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

from codegen_rag.evaluation.evaluator import Evaluator
from codegen_rag.sql.schema import introspect_sqlite_schema
from codegen_rag.sql.sql_generation_task import SQLGenerationTask


class FakeSQLModel:
    """Always returns a correct COUNT(*) query, to exercise the full path."""

    def generate(self, prompt: str, gen_config=None) -> list[str]:  # noqa: ANN001
        return ["SELECT COUNT(*) FROM singer;"]


@pytest.fixture
def concert_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "concert_singer.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE singer (Singer_ID INTEGER PRIMARY KEY, Name TEXT)")
    conn.executemany("INSERT INTO singer VALUES (?, ?)", [(1, "Joe"), (2, "Amy")])
    conn.commit()
    conn.close()
    return db_path


def test_evaluate_sql_task_computes_execution_accuracy(tmp_path: Path, concert_db: Path):
    schema = introspect_sqlite_schema(concert_db, db_id="concert_singer")
    record = {
        "question": "How many singers are there?",
        "schema": schema,
        "gold_sql": "SELECT COUNT(*) FROM singer;",
        "db_path": concert_db,
    }

    task = SQLGenerationTask(FakeSQLModel())
    evaluator = Evaluator(tmp_path / "results")
    summary = evaluator.evaluate_sql_task(task, [record], model_tier="small_lm_baseline", dataset_name="spider")

    assert summary["metrics"]["execution_accuracy"]["execution_accuracy"] == 1.0
    assert (tmp_path / "results" / "sql_generation__spider__small_lm_baseline__metrics.json").exists()


def test_evaluate_sql_task_predictions_file_is_json_serializable(tmp_path: Path, concert_db: Path):
    schema = introspect_sqlite_schema(concert_db, db_id="concert_singer")
    record = {
        "question": "Count singers",
        "schema": schema,
        "gold_sql": "SELECT COUNT(*) FROM singer;",
        "db_path": concert_db,
    }
    task = SQLGenerationTask(FakeSQLModel())
    evaluator = Evaluator(tmp_path / "results")
    evaluator.evaluate_sql_task(task, [record], model_tier="small_lm_baseline")

    pred_file = tmp_path / "results" / "sql_generation__spider__small_lm_baseline__predictions.jsonl"
    assert pred_file.exists()
    # schema/db_path (non-serializable objects) must not have been written raw
    content = pred_file.read_text()
    assert "DatabaseSchema" not in content


def test_build_comparison_table_includes_execution_accuracy_column(tmp_path: Path, concert_db: Path):
    schema = introspect_sqlite_schema(concert_db, db_id="concert_singer")
    record = {
        "question": "Count singers",
        "schema": schema,
        "gold_sql": "SELECT COUNT(*) FROM singer;",
        "db_path": concert_db,
    }
    task = SQLGenerationTask(FakeSQLModel())
    evaluator = Evaluator(tmp_path / "results")
    summary = evaluator.evaluate_sql_task(task, [record], model_tier="small_lm_baseline")
    df = evaluator.build_comparison_table([summary])
    assert "execution_accuracy" in df.columns
    assert df.iloc[0]["execution_accuracy"] == 1.0


def test_build_comparison_table_merges_across_separate_calls_instead_of_overwriting(tmp_path: Path):
    """Regression test: each checkpoint notebook is a separate Colab session
    calling build_comparison_table with only its own summaries. A prior bug
    (df.to_csv() with no merge) meant the second checkpoint's call silently
    wiped out the first checkpoint's rows instead of accumulating."""
    evaluator = Evaluator(tmp_path / "results")

    checkpoint1_summary = {
        "task": "documentation_generation",
        "model_tier": "small_lm_baseline",
        "n_examples": 10,
        "metrics": {"exact_match": 0.2},
    }
    evaluator.build_comparison_table([checkpoint1_summary])

    checkpoint2_summary = {
        "task": "sql_generation_spider",
        "model_tier": "small_lm_baseline",
        "n_examples": 15,
        "metrics": {"execution_accuracy": {"execution_accuracy": 0.07}},
    }
    combined = evaluator.build_comparison_table([checkpoint2_summary])

    assert len(combined) == 2
    assert set(combined["task"]) == {"documentation_generation", "sql_generation_spider"}

    saved = pd.read_csv(tmp_path / "results" / "comparison_table.csv")
    assert len(saved) == 2


def test_build_comparison_table_rerun_updates_row_instead_of_duplicating(tmp_path: Path):
    """Re-running the same checkpoint (same task + model_tier) should update
    that row in place, not append a duplicate."""
    evaluator = Evaluator(tmp_path / "results")

    summary_v1 = {
        "task": "program_synthesis",
        "model_tier": "small_lm_baseline",
        "n_examples": 10,
        "metrics": {"exact_match": 0.1},
    }
    evaluator.build_comparison_table([summary_v1])

    summary_v2 = {
        "task": "program_synthesis",
        "model_tier": "small_lm_baseline",
        "n_examples": 10,
        "metrics": {"exact_match": 0.3},
    }
    combined = evaluator.build_comparison_table([summary_v2])

    assert len(combined) == 1
    assert combined.iloc[0]["exact_match"] == 0.3
