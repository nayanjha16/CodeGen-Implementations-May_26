"""Tests for interactive query engine."""

from src.query_engine.engine import QueryEngine
from src.text2sql.sql_generator import SQLGenerator


class TestQueryEngine:
    def test_full_pipeline_without_db(self, mock_model):
        engine = QueryEngine(sql_generator=SQLGenerator(model=mock_model))
        result = engine.process(
            "Show all students older than 20",
            "Table students(id, name, age)",
        )
        assert "sql" in result
        assert "validation" in result
        assert "nosql" in result
        assert "explanation" in result
        assert "SELECT" in result["sql"].upper()

    def test_full_pipeline_with_db(self, mock_model, sample_db):
        engine = QueryEngine(sql_generator=SQLGenerator(model=mock_model))
        result = engine.process(
            "Show all students older than 20",
            "Table students(id, name, age)",
            sample_db,
        )
        assert result["execution"]["success"] is True
        assert result["execution"]["row_count"] >= 1
