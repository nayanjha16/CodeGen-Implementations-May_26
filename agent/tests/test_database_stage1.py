"""Stage 1 unit tests — no live Docker required."""

from __future__ import annotations

import pytest

from agent.database.mongo_shell import ShellParseError, parse_shell_query
from agent.database.postgres import validate_readonly_sql


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT 1",
        "WITH cte AS (SELECT 1) SELECT * FROM cte",
        "select name from singer where age > 10",
    ],
)
def test_validate_readonly_sql_accepts_select(sql: str) -> None:
    assert validate_readonly_sql(sql) is None


@pytest.mark.parametrize(
    "sql,expected",
    [
        ("", "Empty SQL query"),
        ("DELETE FROM singer", "Only read-only SELECT queries are allowed"),
        ("SELECT 1; SELECT 2", "Multiple SQL statements are not allowed"),
        ("INSERT INTO singer VALUES (1)", "Only read-only SELECT queries are allowed"),
    ],
)
def test_validate_readonly_sql_rejects_unsafe(sql: str, expected: str) -> None:
    assert validate_readonly_sql(sql) == expected


def test_parse_mongo_find() -> None:
    parsed = parse_shell_query('db.singer.find({"age": {"$gt": 10}})')
    assert parsed.collection == "singer"
    assert parsed.method == "find"
    assert parsed.args[0] == {"age": {"$gt": 10}}


def test_parse_mongo_aggregate() -> None:
    parsed = parse_shell_query("db.singer.aggregate([{'$match': {'age': 1}}])")
    assert parsed.method == "aggregate"
    assert isinstance(parsed.args[0], list)


def test_parse_mongo_invalid() -> None:
    with pytest.raises(ShellParseError):
        parse_shell_query("not a mongo query")
