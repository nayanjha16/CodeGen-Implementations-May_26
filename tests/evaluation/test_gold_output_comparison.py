"""Tests for gold output comparison helpers."""

from __future__ import annotations

import json

import pytest

from src.evaluation.gold_output_comparison import (
    build_mongo_vs_gold_diff_summary,
    build_sql_vs_sql_diff_summary,
    _parse_gold_mongo_output,
    _parse_gold_sql_output,
)


def test_build_sql_vs_sql_diff_summary_uses_predicted_reference_labels():
    summary = build_sql_vs_sql_diff_summary([], [1])
    assert summary == "row count mismatch: predicted=0 reference=1"


def test_build_mongo_vs_gold_diff_summary_uses_gold_label():
    summary = build_mongo_vs_gold_diff_summary([1], [2], gold_label="gold_nosql")
    assert summary == "first mismatch at row 0: predicted=1 gold_nosql=2"


def test_parse_gold_sql_output_rejects_error_payload():
    _, error = _parse_gold_sql_output(json.dumps({"error": "syntax error"}))
    assert error == "gold sql_output error: syntax error"


def test_parse_gold_mongo_output_accepts_scalar_value():
    pytest.importorskip("psycopg")
    try:
        result, error = _parse_gold_mongo_output(json.dumps({"value": 6}))
    except ImportError:
        pytest.skip("TEND database modules unavailable")
    assert error is None
    assert result is not None
    assert result.scalar == 6


def test_parse_gold_mongo_output_accepts_row_array():
    pytest.importorskip("psycopg")
    try:
        payload = json.dumps([{"_id": None, "count": 6}])
        result, error = _parse_gold_mongo_output(payload)
    except ImportError:
        pytest.skip("TEND database modules unavailable")
    assert error is None
    assert result is not None
    assert result.rows == [{"_id": None, "count": 6}]
