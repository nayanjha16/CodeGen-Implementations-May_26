"""PostgreSQL schema introspection via SQLAlchemy Inspector."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import inspect
from sqlalchemy.engine import Engine


@dataclass
class TableSchema:
    name: str
    ddl: str
    columns: list[str] = field(default_factory=list)
    foreign_keys: list[dict[str, str]] = field(default_factory=list)

    def embedding_text(self) -> str:
        fk_summary = ", ".join(f"{fk['column']} -> {fk['referred_table']}.{fk['referred_column']}" for fk in self.foreign_keys)
        parts = [self.name, " ".join(self.columns)]
        if fk_summary:
            parts.append(fk_summary)
        parts.append(self.ddl[:500])
        return " | ".join(parts)


def _format_column_type(col: dict[str, Any]) -> str:
    col_type = col.get("type")
    return str(col_type) if col_type is not None else "TEXT"


def _build_ddl(table_name: str, columns: list[dict[str, Any]], pk_cols: list[str], fks: list[dict[str, str]]) -> str:
    col_defs: list[str] = []
    for col in columns:
        name = col["name"]
        ctype = _format_column_type(col)
        nullable = "" if col.get("nullable", True) else " NOT NULL"
        col_defs.append(f"  {name} {ctype}{nullable}")

    if pk_cols:
        col_defs.append(f"  PRIMARY KEY ({', '.join(pk_cols)})")

    for fk in fks:
        col_defs.append(
            f"  FOREIGN KEY ({fk['column']}) REFERENCES {fk['referred_table']}({fk['referred_column']})"
        )

    body = ",\n".join(col_defs)
    return f"CREATE TABLE {table_name} (\n{body}\n);"


def load_all_tables(engine: Engine, schema: str = "public") -> list[TableSchema]:
    """Introspect all tables in the given schema."""
    inspector = inspect(engine)
    table_names = inspector.get_table_names(schema=schema)
    results: list[TableSchema] = []

    for table_name in sorted(table_names):
        columns_raw = inspector.get_columns(table_name, schema=schema)
        pk = inspector.get_pk_constraint(table_name, schema=schema) or {}
        pk_cols = pk.get("constrained_columns") or []

        fks: list[dict[str, str]] = []
        for fk_raw in inspector.get_foreign_keys(table_name, schema=schema):
            referred = fk_raw.get("referred_table", "")
            referred_cols = fk_raw.get("referred_columns") or []
            constrained = fk_raw.get("constrained_columns") or []
            for col, ref_col in zip(constrained, referred_cols):
                fks.append(
                    {
                        "column": col,
                        "referred_table": referred,
                        "referred_column": ref_col,
                    }
                )

        columns = [{"name": c["name"], "type": c.get("type"), "nullable": c.get("nullable", True)} for c in columns_raw]
        ddl = _build_ddl(table_name, columns, pk_cols, fks)
        results.append(
            TableSchema(
                name=table_name,
                ddl=ddl,
                columns=[c["name"] for c in columns],
                foreign_keys=fks,
            )
        )

    return results
