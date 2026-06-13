"""Tests for text-to-SQL module."""

import pytest

from src.text2sql.prompt_builder import PromptBuilder
from src.text2sql.sql_executor import SQLExecutor
from src.text2sql.sql_generator import SQLGenerator
from src.text2sql.sql_validator import SQLValidator


class TestPromptBuilder:
    def test_build_prompt(self):
        builder = PromptBuilder()
        prompt = builder.build(
            "Show all students",
            "Table students(id, name, age)",
        )
        assert "Schema:" in prompt
        assert "Show all students" in prompt
        assert "Generate SQL query" in prompt

    def test_build_batch(self, sample_examples):
        builder = PromptBuilder()
        prompts = builder.build_batch(sample_examples)
        assert len(prompts) == 2

    def test_custom_template(self):
        builder = PromptBuilder(template="Q: {question}\nS: {schema}")
        assert builder.get_template_name() == "custom"
        assert "Q:" in builder.build("test", "schema")


class TestSQLGenerator:
    def test_generate_with_mock(self, mock_model):
        generator = SQLGenerator(model=mock_model)
        result = generator.generate(
            "Show all students older than 20",
            "Table students(id, name, age)",
        )
        assert "sql" in result
        assert "SELECT" in result["sql"].upper()

    def test_extract_sql_from_codeblock(self, mock_model):
        mock_model.generate = lambda prompt, **kw: "```sql\nSELECT * FROM t\n```"
        generator = SQLGenerator(model=mock_model)
        result = generator.generate("q", "schema")
        assert result["sql"] == "SELECT * FROM t"

    def test_generate_batch(self, mock_model, sample_examples):
        generator = SQLGenerator(model=mock_model)
        results = generator.generate_batch(sample_examples)
        assert len(results) == 2
        assert all("sql" in r for r in results)


class TestSQLValidator:
    def test_valid_sql(self):
        validator = SQLValidator()
        result = validator.validate_syntax("SELECT name FROM students WHERE age > 20")
        assert result["valid"] is True

    def test_invalid_sql(self):
        validator = SQLValidator()
        result = validator.validate_syntax("")
        assert result["valid"] is False

    def test_completeness(self):
        validator = SQLValidator()
        result = validator.validate_completeness("SELECT name FROM students")
        assert result["complete"] is True

    def test_incomplete_select(self):
        validator = SQLValidator()
        result = validator.validate_completeness("SELECT name")
        assert result["complete"] is False

    def test_validate_with_sqlite(self, sample_db):
        validator = SQLValidator()
        result = validator.validate(
            "SELECT name FROM students WHERE age > 20",
            str(sample_db),
        )
        assert result["valid"] is True


class TestSQLExecutor:
    def test_execute_success(self, sample_db):
        executor = SQLExecutor()
        result = executor.execute(
            "SELECT name FROM students WHERE age > 20",
            sample_db,
        )
        assert result["success"] is True
        assert result["row_count"] == 1
        assert result["rows"][0]["name"] == "Alice"

    def test_execute_failure(self, sample_db):
        executor = SQLExecutor()
        result = executor.execute("SELECT bad_column FROM students", sample_db)
        assert result["success"] is False

    def test_compare_results(self, sample_db):
        executor = SQLExecutor()
        result = executor.compare_results(
            "SELECT name FROM students WHERE age > 20",
            "SELECT name FROM students WHERE age > 20",
            sample_db,
        )
        assert result["execution_match"] is True

    def test_missing_database(self):
        executor = SQLExecutor()
        result = executor.execute("SELECT 1", "/nonexistent/db.sqlite")
        assert result["success"] is False
