"""Shared pytest fixtures."""

import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def sample_db(tmp_path):
    """Create a temporary SQLite database."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE students (id INTEGER, name TEXT, age INTEGER)")
    cursor.execute("CREATE TABLE users (id INTEGER, name TEXT, age INTEGER)")
    cursor.executemany(
        "INSERT INTO students VALUES (?, ?, ?)",
        [(1, "Alice", 22), (2, "Bob", 19), (3, "Charlie", 18)],
    )
    cursor.executemany(
        "INSERT INTO users VALUES (?, ?, ?)",
        [(1, "Alice", 22), (2, "Bob", 19)],
    )
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def mock_model():
    """Mock CodeGen model that returns predictable SQL."""

    class MockModel:
        model_name = "mock/codegen"
        device = "cpu"

        def generate(self, prompt, **kwargs):
            if "older than 20" in prompt.lower() or "age > 20" in prompt.lower():
                return "SELECT name FROM students WHERE age > 20"
            if "all students" in prompt.lower():
                return "SELECT * FROM students"
            return "SELECT * FROM students"

        def load(self):
            pass

    return MockModel()


@pytest.fixture
def sample_examples():
    """Sample standardized dataset examples."""
    return [
        {
            "question": "Show all students older than 20",
            "schema": "Table students(id, name, age)",
            "sql": "SELECT name FROM students WHERE age > 20",
            "db_id": "students",
        },
        {
            "question": "List all students",
            "schema": "Table students(id, name, age)",
            "sql": "SELECT * FROM students",
            "db_id": "students",
        },
    ]
