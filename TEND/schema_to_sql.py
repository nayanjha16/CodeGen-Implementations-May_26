"""Convert Spider/BIRD tables.json entries into SQL DDL."""

from __future__ import annotations

from typing import Any

_SQL_TYPE_MAP = {
    "text": "TEXT",
    "number": "REAL",
    "time": "TIME",
    "boolean": "BOOLEAN",
    "others": "TEXT",
}


def _sql_type(spider_type: str) -> str:
    return _SQL_TYPE_MAP.get(spider_type.lower(), "TEXT")


def generate_sql_schema(db_json: dict[str, Any]) -> str:
    """Generate SQL DDL from a Spider ``tables.json`` database entry."""
    table_names = db_json.get("table_names_original") or db_json.get("table_names", [])
    column_names = db_json.get("column_names_original") or db_json.get("column_names", [])
    column_types = db_json.get("column_types", [])
    primary_keys = set(db_json.get("primary_keys", []))

    columns_by_table: dict[int, list[tuple[str, str, bool]]] = {}
    for col_idx, (table_idx, col_name) in enumerate(column_names):
        if table_idx < 0:
            continue
        spider_type = column_types[col_idx] if col_idx < len(column_types) else "text"
        columns_by_table.setdefault(table_idx, []).append(
            (col_name, _sql_type(spider_type), col_idx in primary_keys)
        )

    statements: list[str] = []
    for table_idx, table_name in enumerate(table_names):
        cols = columns_by_table.get(table_idx, [])
        if not cols:
            continue
        col_defs = []
        for col_name, col_type, is_pk in cols:
            definition = f"    {col_name} {col_type}"
            if is_pk:
                definition += " PRIMARY KEY"
            col_defs.append(definition)
        body = ",\n".join(col_defs)
        statements.append(f"CREATE TABLE {table_name} (\n{body}\n);")

    return "\n\n".join(statements)


def generate_sql_schema_from_spider_schema(schema: str) -> str:
    """Convert SpiderLoader simplified schema text into SQL DDL."""
    statements: list[str] = []
    for line in schema.splitlines():
        line = line.strip()
        if not line.startswith("Table "):
            continue
        table_part, _, cols_part = line.partition("(")
        table_name = table_part.replace("Table ", "", 1).strip()
        cols = [c.strip() for c in cols_part.rstrip(")").split(",") if c.strip()]
        if not cols:
            continue
        col_defs = []
        for col in cols:
            if " " in col:
                name, col_type = col.rsplit(" ", 1)
                sql_type = _sql_type(col_type)
            else:
                name, sql_type = col, "TEXT"
            col_defs.append(f"    {name} {sql_type}")
        statements.append(f"CREATE TABLE {table_name} (\n" + ",\n".join(col_defs) + "\n);")
    return "\n\n".join(statements)
