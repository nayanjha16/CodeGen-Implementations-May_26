"""Tests for evaluation CSV export."""

import csv

from src.evaluation.export import save_evaluation_details_csv


class TestEvaluationExport:
    def test_save_evaluation_details_csv(self, tmp_path):
        predictions = [
            {
                "question": "List students",
                "schema": "Table students(id, name)",
                "db_id": "students",
                "prompt": "Generate SQL for: List students",
                "raw_output": "SELECT * FROM students",
                "sql": "SELECT * FROM students",
                "ground_truth": "SELECT name FROM students",
            }
        ]

        csv_path = save_evaluation_details_csv(tmp_path / "details.csv", predictions)
        assert csv_path.exists()

        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert len(rows) == 1
        assert rows[0]["question"] == "List students"
        assert rows[0]["prompt"] == "Generate SQL for: List students"
        assert rows[0]["raw_output"] == "SELECT * FROM students"
        assert rows[0]["predicted_sql"] == "SELECT * FROM students"
        assert rows[0]["ground_truth"] == "SELECT name FROM students"
        assert rows[0]["exact_match"] == "False"
