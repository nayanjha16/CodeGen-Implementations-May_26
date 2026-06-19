"""Convert loader schema text into SQL DDL and MongoDB schema JSON."""

from __future__ import annotations

import json
import re
from typing import Any

_SQL_TYPE_MAP = {
    "text": "TEXT",
    "number": "REAL",
    "integer": "INTEGER",
    "time": "TIME",
    "date": "TEXT",
    "boolean": "BOOLEAN",
    "bool": "BOOLEAN",
    "real": "REAL",
    "others": "TEXT",
}

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


def _sql_type(token: str) -> str:
    return _SQL_TYPE_MAP.get(token.lower(), "TEXT")


def _mongo_type(sql_type: str) -> str:
    token = sql_type.strip().upper().split("(")[0]
    return _MONGO_TYPE_MAP.get(token, "string")


def _ddl_from_table_lines(schema: str) -> str:
    """Convert ``Table name(col type, ...)`` lines into SQL DDL."""
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
                sql_col_type = _sql_type(col_type)
            else:
                name, sql_col_type = col, "TEXT"
            col_defs.append(f"    {name} {sql_col_type}")
        statements.append(f"CREATE TABLE {table_name} (\n" + ",\n".join(col_defs) + "\n);")
    return "\n\n".join(statements)


def _ddl_from_loader_schema(schema: str) -> str:
    """Convert loader schema text into SQL DDL."""
    if not schema.strip():
        return ""
    if re.search(r"CREATE\s+TABLE\b", schema, re.IGNORECASE):
        return schema.strip()
    return _ddl_from_table_lines(schema)


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
            col_line = re.sub(
                r"\bPRIMARY\s+KEY\b", "", col_line, flags=re.IGNORECASE
            ).strip()
            parts = col_line.split()
            if len(parts) < 2:
                continue
            col_name = " ".join(parts[:-1])
            sql_type = parts[-1]
            columns.append((col_name, _mongo_type(sql_type), is_pk))
        tables[table_name] = columns
    return tables


def derive_mongo_schema(sql_schema: str) -> dict[str, Any]:
    """Derive a MongoDB collection schema from loader or DDL SQL schema text."""
    if not sql_schema.strip():
        return {}

    ddl = _ddl_from_loader_schema(sql_schema)
    if not ddl.strip():
        return {}

    tables = _parse_create_tables(ddl)
    mongo_schema: dict[str, Any] = {}
    for table_name, columns in tables.items():
        fields: dict[str, str] = {"_id": "ObjectId"}
        for col_name, mongo_type, is_pk in columns:
            if is_pk and col_name.lower() in {"id", f"{table_name}_id"}:
                continue
            fields[col_name] = mongo_type
        mongo_schema[table_name] = fields
    return mongo_schema


def derive_mongo_schema_json(sql_schema: str, *, compact: bool = False) -> str:
    """Return MongoDB schema as JSON for prompts and exports."""
    mongo_schema = derive_mongo_schema(sql_schema)
    if not mongo_schema:
        return "{}"
    if compact:
        return json.dumps(mongo_schema, sort_keys=True)
    return json.dumps(mongo_schema, indent=2, sort_keys=True)
