"""SQL execution against benchmark databases."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


from src.utils.schema_conversion import derive_mongo_schema_json


def build_text2sql_prompt(
    question: str,
    schema: str,
    *,
    config: dict[str, Any] | None = None,
    model_name: str | None = None,
) -> str:
    """Build a SQL-only text-to-SQL prompt (same format as text2sql_details.csv)."""
    from src.text2sql.prompt_builder import PromptBuilder
    from src.utils.config import get_model_name, load_config

    cfg = config or load_config()
    name = model_name or get_model_name(cfg)
    return PromptBuilder.for_model(name, cfg).build(question, schema)


def build_nosql_prompt(
    sql_query: str,
    schema: str,
    *,
    config: dict[str, Any] | None = None,
    model_name: str | None = None,
    nosql_schema: str | None = None,
) -> str:
    """Build a SQL-to-MongoDB conversion prompt."""
    from src.sql2nosql.prompt_builder import NoSQLPromptBuilder
    from src.utils.config import get_model_name, load_config

    cfg = config or load_config()
    name = model_name or get_model_name(cfg)
    return NoSQLPromptBuilder.for_model(name, cfg).build(
        sql_query,
        schema,
        nosql_schema=nosql_schema,
    )


def derive_nosql_schema(schema: str, *, compact: bool = False) -> str:
    """Derive MongoDB schema JSON from SQL schema text."""
    return derive_mongo_schema_json(schema, compact=compact)


def build_documentation_prompt(
    mongodb_query: str,
    schema: str = "",
    *,
    config: dict[str, Any] | None = None,
    model_name: str | None = None,
    nosql_schema: str | None = None,
    question: str = "",
) -> str:
    """Build a MongoDB query documentation prompt."""
    from src.documentation.prompt_builder import DocumentationPromptBuilder
    from src.utils.config import get_model_name, load_config

    cfg = config or load_config()
    name = model_name or get_model_name(cfg)
    return DocumentationPromptBuilder.for_model(name, cfg).build(
        mongodb_query,
        schema,
        nosql_schema=nosql_schema,
        question=question,
    )


class SQLExecutor:
    """Execute SQL queries and compare results for evaluation."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else None

    def execute(
        self,
        sql: str,
        db_path: str | Path | None = None,
        params: tuple | None = None,
    ) -> dict[str, Any]:
        """Execute SQL and return results."""
        path = Path(db_path) if db_path else self.db_path
        if path is None or not path.exists():
            return {
                "success": False,
                "error": f"Database not found: {path}",
                "rows": [],
                "row_count": 0,
            }

        try:
            conn = sqlite3.connect(str(path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            rows = cursor.fetchall()
            result_rows = [dict(row) for row in rows]
            conn.close()
            return {
                "success": True,
                "error": None,
                "rows": result_rows,
                "row_count": len(result_rows),
            }
        except sqlite3.Error as e:
            return {
                "success": False,
                "error": str(e),
                "rows": [],
                "row_count": 0,
            }

    def compare_results(
        self,
        predicted_sql: str,
        ground_truth_sql: str,
        db_path: str | Path,
    ) -> dict[str, Any]:
        """Compare execution results of predicted vs ground truth SQL."""
        pred_result = self.execute(predicted_sql, db_path)
        gt_result = self.execute(ground_truth_sql, db_path)

        if not pred_result["success"]:
            return {
                "execution_match": False,
                "predicted_success": False,
                "ground_truth_success": gt_result["success"],
                "predicted_error": pred_result["error"],
                "ground_truth_error": gt_result.get("error"),
            }

        if not gt_result["success"]:
            return {
                "execution_match": False,
                "predicted_success": True,
                "ground_truth_success": False,
                "predicted_error": None,
                "ground_truth_error": gt_result["error"],
            }

        pred_rows = self._normalize_rows(pred_result["rows"])
        gt_rows = self._normalize_rows(gt_result["rows"])

        return {
            "execution_match": pred_rows == gt_rows,
            "predicted_success": True,
            "ground_truth_success": True,
            "predicted_row_count": len(pred_rows),
            "ground_truth_row_count": len(gt_rows),
            "predicted_error": None,
            "ground_truth_error": None,
        }

    @staticmethod
    def _normalize_value(value: Any) -> str:
        """Canonical string for order-independent result comparison."""
        if value is None:
            return "__NULL__"
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    @staticmethod
    def _normalize_rows(rows: list[dict]) -> list[tuple]:
        """Normalize rows for comparison (order-independent)."""
        normalized = []
        for row in rows:
            items = tuple(
                (key, SQLExecutor._normalize_value(val))
                for key, val in sorted(row.items(), key=lambda item: item[0])
            )
            normalized.append(items)
        return sorted(normalized)
