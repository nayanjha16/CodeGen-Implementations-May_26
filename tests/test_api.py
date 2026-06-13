"""Tests for FastAPI endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestAPI:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    @patch("src.api.main.get_sql_generator")
    def test_generate_sql(self, mock_get_gen, client):
        mock_gen = mock_get_gen.return_value
        mock_gen.generate.return_value = {
            "sql": "SELECT * FROM students",
            "raw_output": "SELECT * FROM students",
            "prompt": "test prompt",
        }
        response = client.post(
            "/generate-sql",
            json={
                "question": "Show all students",
                "schema": "Table students(id, name)",
            },
        )
        assert response.status_code == 200
        assert "sql" in response.json()

    def test_translate_nosql(self, client):
        response = client.post(
            "/translate-nosql",
            json={"sql": "SELECT name FROM users WHERE age > 20"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "mongodb_query" in data

    def test_execute_query(self, client, sample_db):
        response = client.post(
            "/execute-query",
            json={
                "sql": "SELECT name FROM students WHERE age > 20",
                "db_path": str(sample_db),
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["row_count"] == 1

    def test_evaluate(self, client):
        response = client.post(
            "/evaluate",
            json={
                "predictions": ["SELECT name FROM students WHERE age > 20"],
                "references": ["SELECT name FROM students WHERE age > 20"],
            },
        )
        assert response.status_code == 200
        metrics = response.json()["metrics"]
        assert "exact_match" in metrics
        assert "bleu" in metrics

    def test_evaluate_mismatched_lengths(self, client):
        response = client.post(
            "/evaluate",
            json={
                "predictions": ["SELECT 1"],
                "references": ["SELECT 1", "SELECT 2"],
            },
        )
        assert response.status_code == 400

    @patch("src.api.main.QueryEngine")
    def test_interactive_query(self, mock_engine_cls, client):
        mock_engine_cls.return_value.process.return_value = {
            "sql": "SELECT * FROM students",
            "explanation": "test",
        }
        response = client.post(
            "/interactive-query",
            params={
                "question": "Show students",
                "schema": "Table students(id, name)",
            },
        )
        assert response.status_code == 200
