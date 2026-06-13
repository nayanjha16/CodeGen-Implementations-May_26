"""Create sample SQLite database for testing."""

import sqlite3
from pathlib import Path


def create_sample_db(db_path: str | Path = "data/sample/students.db") -> Path:
    """Create a sample students database."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS students")
    cursor.execute("DROP TABLE IF EXISTS courses")
    cursor.execute("DROP TABLE IF EXISTS enrollments")

    cursor.execute(
        "CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"
    )
    cursor.execute(
        "CREATE TABLE courses (id INTEGER PRIMARY KEY, name TEXT, credits INTEGER)"
    )
    cursor.execute(
        "CREATE TABLE enrollments (student_id INTEGER, course_id INTEGER)"
    )

    students = [
        (1, "Alice", 22),
        (2, "Bob", 19),
        (3, "Charlie", 25),
        (4, "Diana", 21),
    ]
    courses = [
        (1, "Database Systems", 4),
        (2, "Machine Learning", 3),
        (3, "NLP", 3),
    ]
    enrollments = [(1, 1), (1, 2), (2, 1), (3, 3), (4, 2)]

    cursor.executemany("INSERT INTO students VALUES (?, ?, ?)", students)
    cursor.executemany("INSERT INTO courses VALUES (?, ?, ?)", courses)
    cursor.executemany("INSERT INTO enrollments VALUES (?, ?)", enrollments)

    conn.commit()
    conn.close()
    return db_path


if __name__ == "__main__":
    path = create_sample_db()
    print(f"Sample database created at: {path}")
