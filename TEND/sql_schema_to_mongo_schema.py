"""Convert SQL DDL into MongoDB collection schemas."""

from __future__ import annotations

import json
import re
from typing import Any

_MONGO_TYPE_MAP = {
    "INT": "number",
    "INTEGER": "number",
    "REAL": "number",
    "FLOAT": "number",
    "DOUBLE": "number",
    "DECIMAL": "number",
    "NUMERIC": "number",
    "BOOLEAN": "boolean",
    "BOOL": "boolean",
    "TIME": "string",
    "DATE": "string",
    "DATETIME": "string",
    "TIMESTAMP": "string",
    "TEXT": "string",
    "VARCHAR": "string",
    "CHAR": "string",
}


def _mongo_type(sql_type: str) -> str:
    token = sql_type.strip().upper().split("(")[0]
    return _MONGO_TYPE_MAP.get(token, "string")


def _parse_create_tables(sql_schema: str) -> dict[str, list[tuple[str, str, bool]]]:
    tables: dict[str, list[tuple[str, str, bool]]] = {}
    for match in re.finditer(
        r"CREATE\s+TABLE\s+(\w+)\s*\((.*?)\)\s*;",
        sql_schema,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        table_name = match.group(1)
        body = match.group(2)
        columns: list[tuple[str, str, bool]] = []
        for raw_col in body.split(","):
            col_line = raw_col.strip()
            if not col_line:
                continue
            is_pk = bool(re.search(r"\bPRIMARY\s+KEY\b", col_line, re.IGNORECASE))
            col_line = re.sub(r"\bPRIMARY\s+KEY\b", "", col_line, flags=re.IGNORECASE).strip()
            parts = col_line.split()
            if len(parts) < 2:
                continue
            col_name, sql_type = parts[0], parts[1]
            columns.append((col_name, _mongo_type(sql_type), is_pk))
        tables[table_name] = columns
    return tables


def convert_schema(sql_schema: str) -> dict[str, Any]:
    """Convert SQL DDL to MongoDB schema representation."""
    tables = _parse_create_tables(sql_schema)
    mongo_schema: dict[str, Any] = {}

    for table_name, columns in tables.items():
        fields: dict[str, str] = {"_id": "ObjectId"}
        for col_name, mongo_type, is_pk in columns:
            if is_pk and col_name.lower() in {"id", f"{table_name}_id"}:
                continue
            fields[col_name] = mongo_type
        mongo_schema[table_name] = fields

    return mongo_schema


def convert_schema_json(sql_schema: str) -> str:
    """Return MongoDB schema as a compact JSON string."""
    return json.dumps(convert_schema(sql_schema), indent=2, sort_keys=True)
