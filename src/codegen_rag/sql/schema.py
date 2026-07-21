"""SQLite schema introspection — the foundation of "schema injection"
(table names, column names, and sample values prepended to the prompt, per
the proposal's Task 2 methodology).
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ColumnInfo:
    name: str
    dtype: str
    is_primary_key: bool = False


@dataclass
class TableInfo:
    name: str
    columns: list[ColumnInfo] = field(default_factory=list)
    sample_rows: list[tuple] = field(default_factory=list)


@dataclass
class DatabaseSchema:
    db_id: str
    db_path: Path
    tables: list[TableInfo] = field(default_factory=list)

    def table_names(self) -> list[str]:
        return [t.name for t in self.tables]


def introspect_sqlite_schema(
    db_path: Path,
    db_id: str | None = None,
    sample_rows_per_table: int = 3,
) -> DatabaseSchema:
    """Read a SQLite file's schema (tables, columns, types) plus a handful of
    sample rows per table, used to build the schema-injection prompt prefix.
    """
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        table_names = [row[0] for row in cursor.fetchall()]

        tables: list[TableInfo] = []
        for table_name in table_names:
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = [
                ColumnInfo(name=row[1], dtype=row[2] or "TEXT", is_primary_key=bool(row[5]))
                for row in cursor.fetchall()
            ]

            sample_rows: list[tuple] = []
            if sample_rows_per_table > 0:
                try:
                    cursor.execute(f'SELECT * FROM "{table_name}" LIMIT ?', (sample_rows_per_table,))
                    sample_rows = cursor.fetchall()
                except sqlite3.Error:
                    sample_rows = []

            tables.append(TableInfo(name=table_name, columns=columns, sample_rows=sample_rows))

        return DatabaseSchema(db_id=db_id or db_path.stem, db_path=db_path, tables=tables)
    finally:
        conn.close()
