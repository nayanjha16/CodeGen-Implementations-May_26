"""Tests for adapter registry."""

from tool.desktop.registry import build_adapters


def test_build_adapters_includes_text2sql_and_stub():
    adapters = build_adapters()
    assert "Text-to-SQL" in adapters
    assert "SQL-to-NoSQL" in adapters
    assert adapters["Text-to-SQL"].name == "Text-to-SQL"
