"""Shared database helpers (TEND-compatible naming)."""

from __future__ import annotations

import re


def sanitize_pg_schema_name(db_id: str) -> str:
    name = db_id.strip().lower()
    name = re.sub(r"[^a-z0-9_]", "_", name)
    if not name:
        raise ValueError(f"Invalid db_id for schema name: {db_id!r}")
    if name[0].isdigit():
        name = f"db_{name}"
    return name


def mongo_database_name(dataset: str, db_id: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", db_id)
    return f"{dataset}_{safe}"


def mongo_collection_name(table_name: str) -> str:
    return table_name.lower()


def quote_pg_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'
