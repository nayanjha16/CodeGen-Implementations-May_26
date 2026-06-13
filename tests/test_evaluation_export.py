"""Tests for evaluation CSV export."""

import csv

from src.evaluation.export import save_sql2nosql_details_csv, save_text2sql_details_csv


class TestEvaluationExport:
    def test_save_text2sql_details_csv(self, tmp_path):
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

        csv_path = save_text2sql_details_csv(tmp_path / "text2sql_details.csv", predictions)
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
        assert "predicted_mongodb_query" not in rows[0]

    def test_save_sql2nosql_details_csv(self, tmp_path):
        predictions = [
            {
                "question": "List students",
                "db_id": "students",
                "sql": "SELECT * FROM students",
                "reference_sql": "SELECT name FROM students",
                "predicted_sql_valid": True,
                "reference_sql_valid": True,
                "predicted_mongodb_query": "db.students.find({})",
                "reference_mongodb_query": "db.students.find({}, { name: 1 })",
                "reference_translation_success": True,
                "mongodb_warnings": "",
                "mongodb_success": True,
                "collection": "students",
                "filter": {},
                "projection": {},
                "reference_collection": "students",
                "reference_filter": {},
                "reference_projection": {"name": 1},
            }
        ]

        csv_path = save_sql2nosql_details_csv(tmp_path / "sql2nosql_details.csv", predictions)
        assert csv_path.exists()

        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert rows[0]["reference_sql"] == "SELECT name FROM students"
        assert rows[0]["predicted_mongodb_query"] == "db.students.find({})"
        assert rows[0]["reference_mongodb_query"] == "db.students.find({}, { name: 1 })"
        assert rows[0]["exact_match"] == "False"
        assert rows[0]["syntax_valid"] == "True"
        assert rows[0]["structural_match"] == "False"
        assert float(rows[0]["token_f1"]) > 0

    def test_save_sql2nosql_skips_failed_translation(self, tmp_path):
        predictions = [
            {
                "question": "Bad output",
                "db_id": "students",
                "sql": "not valid sql",
                "reference_sql": "SELECT * FROM students",
                "predicted_sql_valid": False,
                "reference_sql_valid": True,
                "predicted_mongodb_query": "",
                "reference_mongodb_query": "db.students.find({})",
                "reference_translation_success": True,
                "mongodb_warnings": "Input is not a valid SELECT query with FROM clause",
                "mongodb_success": False,
            }
        ]

        csv_path = save_sql2nosql_details_csv(tmp_path / "sql2nosql_details.csv", predictions)
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        assert rows[0]["exact_match"] == ""
        assert rows[0]["syntax_valid"] == ""
        assert rows[0]["mongodb_success"] == "False"
