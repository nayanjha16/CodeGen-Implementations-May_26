from __future__ import annotations

import sqlite3
import sys
import types
from pathlib import Path

import pytest

from codegen_rag.evaluation.metrics import (
    compute_bertscore,
    compute_codebleu,
    exact_match,
    execution_accuracy,
    sample_for_manual_inspection,
)


def test_exact_match_all_correct():
    preds = ["a", "b", "c"]
    refs = ["a", "b", "c"]
    assert exact_match(preds, refs) == 1.0


def test_exact_match_partial():
    preds = ["a", "x", "c"]
    refs = ["a", "b", "c"]
    assert exact_match(preds, refs) == pytest.approx(2 / 3)


def test_exact_match_empty_predictions():
    assert exact_match([], []) == 0.0


def test_exact_match_ignores_surrounding_whitespace():
    assert exact_match([" a \n"], ["a"]) == 1.0


def test_sample_for_manual_inspection_caps_at_n():
    records = [{"i": i} for i in range(5)]
    sample = sample_for_manual_inspection(records, n=20)
    assert len(sample) == 5


def test_sample_for_manual_inspection_deterministic():
    records = [{"i": i} for i in range(100)]
    a = sample_for_manual_inspection(records, n=20, seed=42)
    b = sample_for_manual_inspection(records, n=20, seed=42)
    assert a == b


@pytest.fixture
def sample_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "test.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    conn.executemany("INSERT INTO users VALUES (?, ?)", [(1, "alice"), (2, "bob")])
    conn.commit()
    conn.close()
    return db_path


def test_execution_accuracy_matching_queries(sample_db: Path):
    result = execution_accuracy(
        predicted_sql=["SELECT * FROM users ORDER BY id"],
        gold_sql=["SELECT * FROM users ORDER BY id"],
        db_paths=[sample_db],
    )
    assert result["execution_accuracy"] == 1.0
    assert result["correct"] == 1


def test_execution_accuracy_order_insensitive(sample_db: Path):
    result = execution_accuracy(
        predicted_sql=["SELECT * FROM users ORDER BY name DESC"],
        gold_sql=["SELECT * FROM users ORDER BY id ASC"],
        db_paths=[sample_db],
    )
    assert result["execution_accuracy"] == 1.0


def test_execution_accuracy_invalid_sql_counts_as_error(sample_db: Path):
    result = execution_accuracy(
        predicted_sql=["SELECT * FROM nonexistent_table"],
        gold_sql=["SELECT * FROM users"],
        db_paths=[sample_db],
    )
    assert result["execution_accuracy"] == 0.0
    assert len(result["errors"]) == 1


def test_compute_codebleu_uses_real_ast_match_when_tree_sitter_python_installed():
    """Regression test for the `tree-sitter-python` dependency: with it
    installed (and matched to the pinned `tree-sitter`/`codebleu` versions),
    CodeBLEU must compute real syntax/dataflow match for Python instead of
    silently falling back to sacrebleu. Skips (rather than failing) in
    environments where the grammar package genuinely isn't installed, since
    the fallback itself is intentional/graceful there."""
    pytest.importorskip("tree_sitter_python")

    result = compute_codebleu(
        predictions=["def subtract(x, y):\n    result = x - y\n    return result"],
        references=["def add(a, b):\n    return a + b"],
        language="python",
    )

    assert "fallback" not in result
    assert "syntax_match" in result
    assert "dataflow_match" in result
    assert 0.0 <= result["codebleu"] <= 1.0


def test_compute_codebleu_identical_code_scores_perfectly():
    pytest.importorskip("tree_sitter_python")

    code = "def add(a, b):\n    return a + b"
    result = compute_codebleu(predictions=[code], references=[code], language="python")
    assert result["codebleu"] == pytest.approx(1.0)


def test_compute_bertscore_empty_predictions_short_circuits():
    assert compute_bertscore([], []) == {"precision": 0.0, "recall": 0.0, "f1": 0.0}


def test_compute_bertscore_falls_back_when_bert_score_package_broken(monkeypatch):
    """Regression test: bert-score is effectively unmaintained and its
    internals can raise AttributeError against newer transformers releases
    (e.g. "RobertaTokenizer has no attribute
    'build_inputs_with_special_tokens'"). This must degrade gracefully --
    like compute_codebleu's tree-sitter fallback -- instead of crashing the
    whole evaluation run."""

    fake_bert_score = types.ModuleType("bert_score")

    def _broken_score(*args, **kwargs):
        raise AttributeError("RobertaTokenizer has no attribute 'build_inputs_with_special_tokens'")

    fake_bert_score.score = _broken_score
    monkeypatch.setitem(sys.modules, "bert_score", fake_bert_score)

    result = compute_bertscore(["some code"], ["some reference"])

    assert result["fallback"] is True
    assert result["precision"] is None
    assert result["recall"] is None
    assert result["f1"] is None
