"""Interactive conversational query engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.sql2nosql.translator import SQLToNoSQLTranslator
from src.text2sql.sql_executor import SQLExecutor
from src.text2sql.sql_generator import SQLGenerator
from src.text2sql.sql_validator import SQLValidator


class QueryEngine:
    """
    End-to-end interactive query pipeline:
    NL Question -> SQL -> Validation -> Execution -> Explanation
    """

    def __init__(
        self,
        sql_generator: SQLGenerator | None = None,
        sql_validator: SQLValidator | None = None,
        sql_executor: SQLExecutor | None = None,
        nosql_translator: SQLToNoSQLTranslator | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.config = config or {}
        self.sql_generator = sql_generator or SQLGenerator(config=self.config)
        self.sql_validator = sql_validator or SQLValidator()
        self.sql_executor = sql_executor or SQLExecutor()
        self.nosql_translator = nosql_translator or SQLToNoSQLTranslator()

    def process(
        self,
        question: str,
        schema: str,
        db_path: str | Path | None = None,
    ) -> dict[str, Any]:
        """Run full interactive query pipeline."""
        # Step 1: Generate SQL
        gen_result = self.sql_generator.generate(question, schema)
        sql = gen_result["sql"]

        # Step 2: Validate SQL
        validation = self.sql_validator.validate(sql, str(db_path) if db_path else None)

        # Step 3: Execute SQL
        execution = {"success": False, "rows": [], "error": "No database provided"}
        if db_path and validation["valid"]:
            execution = self.sql_executor.execute(sql, db_path)

        # Step 4: Translate to NoSQL
        nosql = self.nosql_translator.translate(sql)

        # Step 5: Human-readable explanation
        explanation = self._explain(question, sql, execution, validation)

        return {
            "question": question,
            "schema": schema,
            "sql": sql,
            "raw_model_output": gen_result["raw_output"],
            "validation": validation,
            "execution": execution,
            "nosql": nosql,
            "explanation": explanation,
        }

    def _explain(
        self,
        question: str,
        sql: str,
        execution: dict[str, Any],
        validation: dict[str, Any],
    ) -> str:
        """Generate human-readable explanation of results."""
        parts = [f'For the question "{question}", the system generated:']
        parts.append(f"  SQL: {sql}")

        if validation["valid"]:
            parts.append("  Validation: SQL syntax is valid.")
        else:
            parts.append(f"  Validation: Failed - {validation.get('syntax_error', 'unknown error')}")

        if execution["success"]:
            parts.append(f"  Execution: Success - returned {execution['row_count']} row(s).")
            if execution["rows"][:3]:
                parts.append(f"  Sample results: {execution['rows'][:3]}")
        elif execution.get("error"):
            parts.append(f"  Execution: Failed - {execution['error']}")

        return "\n".join(parts)
