from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from codegen_rag.sql.schema import introspect_sqlite_schema
from codegen_rag.sql.schema_injection import build_schema_prompt, build_sql_prompt
from codegen_rag.sql.spider_birdbench import (
    attach_schemas,
    find_db_path,
    normalize_bird_row,
    normalize_spider_row,
)
from codegen_rag.sql.sql_generation_task import SQLGenerationTask


@pytest.fixture
def concert_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "concert_singer.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE singer (Singer_ID INTEGER PRIMARY KEY, Name TEXT, Country TEXT, Age INTEGER)")
    conn.execute("CREATE TABLE concert (concert_ID INTEGER PRIMARY KEY, concert_Name TEXT, Year INTEGER)")
    conn.executemany(
        "INSERT INTO singer VALUES (?, ?, ?, ?)",
        [(1, "Joe Sharp", "Netherlands", 52), (2, "Timbaland", "United States", 32)],
    )
    conn.commit()
    conn.close()
    return db_path


def test_introspect_sqlite_schema_finds_tables_and_columns(concert_db: Path):
    schema = introspect_sqlite_schema(concert_db, db_id="concert_singer")
    assert schema.table_names() == ["singer", "concert"]
    singer_table = schema.tables[0]
    assert [c.name for c in singer_table.columns] == ["Singer_ID", "Name", "Country", "Age"]
    assert singer_table.columns[0].is_primary_key is True


def test_introspect_sqlite_schema_captures_sample_rows(concert_db: Path):
    schema = introspect_sqlite_schema(concert_db, db_id="concert_singer", sample_rows_per_table=2)
    singer_table = next(t for t in schema.tables if t.name == "singer")
    assert len(singer_table.sample_rows) == 2
    assert singer_table.sample_rows[0][1] == "Joe Sharp"


def test_build_schema_prompt_includes_table_and_columns(concert_db: Path):
    schema = introspect_sqlite_schema(concert_db, db_id="concert_singer")
    prompt = build_schema_prompt(schema)
    assert "# Database: concert_singer" in prompt
    assert "singer(Singer_ID, Name, Country, Age)" in prompt
    assert "sample row:" in prompt


def test_build_schema_prompt_can_omit_samples(concert_db: Path):
    schema = introspect_sqlite_schema(concert_db, db_id="concert_singer")
    prompt = build_schema_prompt(schema, include_sample_values=False)
    assert "sample row" not in prompt


def test_build_sql_prompt_includes_question_and_few_shot(concert_db: Path):
    schema = introspect_sqlite_schema(concert_db, db_id="concert_singer")
    prompt = build_sql_prompt(
        "How many singers are there?",
        schema,
        few_shot_examples=[("How many concerts?", "SELECT COUNT(*) FROM concert;")],
    )
    assert "How many singers are there?" in prompt
    assert "SELECT COUNT(*) FROM concert;" in prompt
    assert prompt.strip().endswith("# SQL:")


def test_normalize_spider_row_maps_query_field():
    row = {"question": "How many singers?", "query": "SELECT COUNT(*) FROM singer", "db_id": "concert_singer"}
    normalized = normalize_spider_row(row)
    assert normalized["gold_sql"] == "SELECT COUNT(*) FROM singer"
    assert normalized["source"] == "spider"


def test_normalize_bird_row_maps_SQL_field():
    row = {"question": "Q", "SQL": "SELECT 1", "db_id": "d1", "evidence": "some evidence"}
    normalized = normalize_bird_row(row)
    assert normalized["gold_sql"] == "SELECT 1"
    assert normalized["evidence"] == "some evidence"


def test_find_db_path_locates_nested_layout(tmp_path: Path):
    nested = tmp_path / "concert_singer"
    nested.mkdir()
    db_file = nested / "concert_singer.sqlite"
    db_file.write_bytes(b"")
    found = find_db_path(tmp_path, "concert_singer")
    assert found == db_file


def test_find_db_path_returns_none_when_missing(tmp_path: Path):
    assert find_db_path(tmp_path, "nonexistent") is None


def test_attach_schemas_skips_missing_db_with_warning(tmp_path: Path, concert_db: Path):
    databases_root = concert_db.parent
    records = [
        {"question": "Q1", "gold_sql": "SELECT 1", "db_id": "concert_singer", "source": "spider"},
        {"question": "Q2", "gold_sql": "SELECT 1", "db_id": "missing_db", "source": "spider"},
    ]
    enriched = attach_schemas(records, databases_root)
    assert len(enriched) == 1
    assert enriched[0]["schema"].db_id == "concert_singer"


def test_sql_generation_task_prompt_and_postprocess(fake_model, concert_db: Path):
    schema = introspect_sqlite_schema(concert_db, db_id="concert_singer")
    task = SQLGenerationTask(fake_model)
    record = {"question": "How many singers are there?", "schema": schema}
    prompt = task.build_prompt(record)
    assert "How many singers are there?" in prompt


def test_sql_generation_task_postprocess_strips_markdown_fence():
    task = SQLGenerationTask(model=None)
    raw = "```sql\nSELECT COUNT(*) FROM singer\n```"
    assert task.postprocess(raw) == "SELECT COUNT(*) FROM singer;"


def test_sql_generation_task_postprocess_keeps_first_statement_only():
    task = SQLGenerationTask(model=None)
    raw = "SELECT COUNT(*) FROM singer; SELECT * FROM concert;"
    assert task.postprocess(raw) == "SELECT COUNT(*) FROM singer;"


def test_sql_generation_task_postprocess_stops_at_commentary():
    task = SQLGenerationTask(model=None)
    raw = "SELECT COUNT(*) FROM singer\n\n# This query counts all singers."
    assert task.postprocess(raw) == "SELECT COUNT(*) FROM singer;"
