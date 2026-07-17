"""Unit tests for SQL extractor."""

from tool.core.sql_extractor import extract_sql


def test_extract_from_code_fence():
    raw = "Here is the query:\n```sql\nSELECT id FROM orders\n```"
    assert extract_sql(raw) == "SELECT id FROM orders"


def test_extract_inline_select():
    raw = "SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id"
    assert "SELECT" in extract_sql(raw)
    assert "orders" in extract_sql(raw)


def test_extract_empty():
    assert extract_sql("No SQL here, just text.") == ""
