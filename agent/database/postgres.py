"""Read-only PostgreSQL access for TEND-loaded schemas."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import psycopg
from psycopg.rows import dict_row

from agent.config.settings import AgentSettings, DatabaseProfileKind, get_settings
from agent.database._utils import quote_pg_ident
from agent.database.profiles import ResolvedDatabaseTarget, resolve_database_target

_FORBIDDEN_SQL = re.compile(
    r"\b("
    r"INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|GRANT|REVOKE|"
    r"COPY|CALL|DO|EXECUTE|MERGE|REPLACE|VACUUM|ANALYZE|COMMENT|"
    r"REINDEX|CLUSTER|LOAD|SECURITY|SET\s+ROLE|RESET\s+ROLE"
    r")\b",
    re.IGNORECASE,
)
_MULTI_STATEMENT = re.compile(r";\s*\S", re.DOTALL)
_STRING_LITERAL_RE = re.compile(r"'([^']*(?:''[^']*)*)'")


def _sql_without_string_literals(sql: str) -> str:
    def _repl(match: re.Match[str]) -> str:
        return "'" + (" " * len(match.group(1))) + "'"

    return _STRING_LITERAL_RE.sub(_repl, sql)


def validate_readonly_sql(sql: str) -> str | None:
    text = (sql or "").strip()
    if not text:
        return "Empty SQL query"
    if _MULTI_STATEMENT.search(text.rstrip(";")):
        return "Multiple SQL statements are not allowed"
    guard_text = _sql_without_string_literals(text)
    if _FORBIDDEN_SQL.search(guard_text):
        return "Only read-only SELECT queries are allowed"
    if not re.match(r"^\s*(WITH\b|SELECT\b)", text, re.IGNORECASE):
        return "Only SELECT queries are allowed"
    return None


@dataclass(frozen=True)
class SqlExecutionResult:
    rows: list[dict[str, Any]]
    row_count: int
    truncated: bool = False
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class ColumnInfo:
    name: str
    data_type: str
    is_nullable: bool


@dataclass
class ForeignKeyInfo:
    table: str
    column: str
    foreign_table: str
    foreign_column: str


@dataclass
class TableSchema:
    name: str
    columns: list[ColumnInfo] = field(default_factory=list)


@dataclass
class SchemaSnapshot:
    db_id: str
    dataset: str
    schema_name: str
    tables: list[TableSchema]
    foreign_keys: list[ForeignKeyInfo]

    def to_ddl(self) -> str:
        """Minimal CREATE TABLE DDL for CodeGen API prompts."""
        lines: list[str] = []
        if any(any(ch.isupper() for ch in table.name) for table in self.tables):
            lines.append(
                "-- Use exact quoted table/column names as shown (mixed-case names require double quotes)."
            )
        for table in self.tables:
            col_defs = ", ".join(
                f"{quote_pg_ident(col.name)} {col.data_type.upper()}"
                for col in table.columns
            )
            lines.append(
                f"CREATE TABLE {quote_pg_ident(table.name)} ({col_defs});"
            )
        for fk in self.foreign_keys:
            lines.append(
                f"ALTER TABLE {quote_pg_ident(fk.table)} ADD FOREIGN KEY "
                f"({quote_pg_ident(fk.column)}) REFERENCES "
                f"{quote_pg_ident(fk.foreign_table)} ({quote_pg_ident(fk.foreign_column)});"
            )
        return "\n".join(lines)


class PostgresExecutor:
    """Execute read-only SQL and introspect schemas on TEND or standalone Postgres."""

    def __init__(self, settings: AgentSettings | None = None) -> None:
        self._settings = settings or get_settings()
        self._connections: dict[str, psycopg.Connection[Any]] = {}

    def close(self) -> None:
        for conn in self._connections.values():
            conn.close()
        self._connections.clear()

    def __enter__(self) -> PostgresExecutor:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _connection_for_catalog(self, catalog: str) -> psycopg.Connection[Any]:
        if catalog not in self._connections:
            self._connections[catalog] = psycopg.connect(
                self._settings.postgres.dsn(catalog),
                autocommit=False,
                connect_timeout=5,
            )
        return self._connections[catalog]

    def _connection(self, dataset: str) -> psycopg.Connection[Any]:
        catalog = self._settings.postgres.catalog_name(dataset)
        return self._connection_for_catalog(catalog)

    def ping(
        self,
        dataset: str | None = None,
        *,
        profile: DatabaseProfileKind | None = None,
    ) -> bool:
        active_profile = profile or self._settings.database_profile
        try:
            if active_profile == "standalone":
                conn = self._connection_for_catalog(self._settings.demo.postgres_database)
            else:
                conn = self._connection(dataset or self._settings.default_dataset)
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            return True
        except Exception:
            return False

    def introspect_schema(
        self,
        db_id: str | None = None,
        dataset: str | None = None,
        *,
        profile: DatabaseProfileKind | None = None,
    ) -> SchemaSnapshot:
        target = resolve_database_target(
            db_id,
            dataset=dataset,
            profile=profile,
            settings=self._settings,
        )
        schema = target.postgres_schema
        conn = self._connection_for_catalog(target.postgres_catalog)

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """,
                (schema,),
            )
            table_names = [str(row[0]) for row in cur.fetchall()]

            tables: list[TableSchema] = []
            for table_name in table_names:
                cur.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                    """,
                    (schema, table_name),
                )
                columns = [
                    ColumnInfo(
                        name=str(row[0]),
                        data_type=str(row[1]),
                        is_nullable=str(row[2]).upper() == "YES",
                    )
                    for row in cur.fetchall()
                ]
                tables.append(TableSchema(name=table_name, columns=columns))

            cur.execute(
                """
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                 AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = %s
                ORDER BY tc.table_name, kcu.column_name
                """,
                (schema,),
            )
            foreign_keys = [
                ForeignKeyInfo(
                    table=str(row[0]),
                    column=str(row[1]),
                    foreign_table=str(row[2]),
                    foreign_column=str(row[3]),
                )
                for row in cur.fetchall()
            ]

        return SchemaSnapshot(
            db_id=target.db_id,
            dataset=target.dataset,
            schema_name=schema,
            tables=tables,
            foreign_keys=foreign_keys,
        )

    def execute(
        self,
        sql: str,
        db_id: str | None = None,
        dataset: str | None = None,
        *,
        profile: DatabaseProfileKind | None = None,
        max_rows: int | None = None,
    ) -> SqlExecutionResult:
        target = resolve_database_target(
            db_id,
            dataset=dataset,
            profile=profile,
            settings=self._settings,
        )
        max_rows = max_rows if max_rows is not None else self._settings.max_result_rows
        validation_error = validate_readonly_sql(sql)
        if validation_error:
            return SqlExecutionResult(rows=[], row_count=0, error=validation_error)

        schema = target.postgres_schema
        conn = self._connection_for_catalog(target.postgres_catalog)
        timeout_ms = self._settings.query_timeout_ms
        query = sql.strip().rstrip(";")

        try:
            with conn.transaction():
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute("SET TRANSACTION READ ONLY")
                    cur.execute(f"SET LOCAL search_path TO {quote_pg_ident(schema)}")
                    cur.execute(f"SET LOCAL statement_timeout = '{timeout_ms}ms'")
                    cur.execute(query)
                    if cur.description is None:
                        return SqlExecutionResult(rows=[], row_count=0)
                    rows = [dict(row) for row in cur.fetchall()]
        except Exception as exc:  # noqa: BLE001
            return SqlExecutionResult(rows=[], row_count=0, error=str(exc))

        truncated = len(rows) > max_rows
        if truncated:
            rows = rows[:max_rows]
        return SqlExecutionResult(
            rows=rows,
            row_count=len(rows),
            truncated=truncated,
        )
