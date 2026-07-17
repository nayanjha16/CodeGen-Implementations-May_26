"""Unit tests for SafetyValidator."""

from tool.core.safety_validator import SafetyValidator


def test_allows_select():
    v = SafetyValidator().validate("SELECT id, name FROM customers WHERE active = true")
    assert v["passed"] is True


def test_allows_with_cte():
    v = SafetyValidator().validate("WITH cte AS (SELECT 1 AS n) SELECT n FROM cte")
    assert v["passed"] is True


def test_blocks_delete():
    v = SafetyValidator().validate("DELETE FROM customers")
    assert v["passed"] is False
    assert "DELETE" in v.get("reason", "")


def test_blocks_multi_statement():
    v = SafetyValidator().validate("SELECT 1; SELECT 2")
    assert v["passed"] is False


def test_blocks_empty():
    v = SafetyValidator().validate("")
    assert v["passed"] is False
