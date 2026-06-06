"""SQL execution against benchmark databases."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


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
    def _normalize_rows(rows: list[dict]) -> list[tuple]:
        """Normalize rows for comparison (order-independent)."""
        normalized = []
        for row in rows:
            normalized.append(tuple(sorted(row.items())))
        return sorted(normalized)
