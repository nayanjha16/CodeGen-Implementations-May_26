"""Pre-execute SQL validation — reuse agent guards + src syntax checks."""

from __future__ import annotations

import re

from agent.database._utils import quote_pg_ident
from agent.database.postgres import validate_readonly_sql
from agent.lib.text2sql_hints import question_is_open_listing
from src.text2sql.sql_validator import SQLValidator

_FROM_JOIN_RE = re.compile(
    r"\b(?:FROM|JOIN)\s+(?:ONLY\s+)?((?:\"[^\"]+\"|[a-zA-Z_][\w$]*)(?:\s*\.\s*(?:\"[^\"]+\"|[a-zA-Z_][\w$]*))*)",
    re.IGNORECASE,
)
_IDENTIFIER_TOKEN_RE = re.compile(r'("(?:[^"]|"")*"|\b[a-zA-Z_][\w$]*\b)')
_SCHEMA_ARTIFACT_LITERALS = frozenset(
    {
        "pascalcase",
        "mixed-case",
        "mixedcase",
        "double quotes",
        "doublequotes",
        "postgresql",
        "postgres",
    }
)
_ARTIFACT_WHERE_RE = re.compile(
    r"\s+WHERE\s+.+$",
    re.IGNORECASE | re.DOTALL,
)
_LITERAL_EQ_RE = re.compile(
    r"""=\s*(?:'([^']*)'|"([^"]*)")""",
    re.IGNORECASE,
)


def _normalize_table_ref(raw: str) -> str:
    text = raw.strip().strip('"')
    if "." in text:
        text = text.split(".")[-1]
    return text.strip('"')


def identifiers_from_ddl(ddl: str) -> set[str]:
    """Quoted table/column names from CREATE TABLE DDL."""
    return set(re.findall(r'"([^"]+)"', ddl or ""))


def quote_known_identifiers(sql: str, identifiers: set[str]) -> str:
    """Quote mixed-case PostgreSQL identifiers the model omitted."""
    lookup = {name.lower(): name for name in identifiers if name != name.lower()}
    if not lookup:
        return sql

    def repl(match: re.Match[str]) -> str:
        token = match.group(0)
        if token.startswith('"'):
            return token
        canonical = lookup.get(token.lower())
        if canonical:
            return quote_pg_ident(canonical)
        return token

    return _IDENTIFIER_TOKEN_RE.sub(repl, sql)


def _split_where_suffix(where_clause: str) -> tuple[str, str]:
    for suffix_pattern in (
        r"\s+ORDER\s+BY",
        r"\s+GROUP\s+BY",
        r"\s+LIMIT",
        r"\s+HAVING",
    ):
        suffix = re.search(suffix_pattern, where_clause, re.IGNORECASE)
        if suffix:
            return where_clause[: suffix.start()], where_clause[suffix.start() :]
    return where_clause, ""


def strip_schema_artifact_filters(sql: str) -> str:
    """Remove WHERE clauses that treat schema hint words as data values."""
    match = _ARTIFACT_WHERE_RE.search(sql)
    if not match:
        return sql

    where_clause = match.group(0)
    for literal_match in _LITERAL_EQ_RE.finditer(where_clause):
        literal = (literal_match.group(1) or literal_match.group(2) or "").strip().lower()
        if literal in _SCHEMA_ARTIFACT_LITERALS:
            head = sql[: match.start()].rstrip()
            _, tail = _split_where_suffix(where_clause)
            return f"{head}{tail}".strip()

    return sql


def strip_invented_where_filters(sql: str, question: str) -> str:
    """Drop WHERE filters on open listing questions when literals aren't in the prompt."""
    if not question_is_open_listing(question):
        return sql

    match = _ARTIFACT_WHERE_RE.search(sql)
    if not match or not _LITERAL_EQ_RE.search(match.group(0)):
        return sql

    head = sql[: match.start()].rstrip()
    _, tail = _split_where_suffix(match.group(0))
    return f"{head}{tail}".strip()


def normalize_generated_sql(sql: str, schema_ddl: str, question: str = "") -> str:
    """Fix common CodeGen output for PascalCase Chinook-style schemas."""
    cleaned = strip_schema_artifact_filters(sql)
    if question:
        cleaned = strip_invented_where_filters(cleaned, question)
    return quote_known_identifiers(cleaned, identifiers_from_ddl(schema_ddl))


def referenced_tables(sql: str) -> set[str]:
    tables: set[str] = set()
    for match in _FROM_JOIN_RE.finditer(sql):
        tables.add(_normalize_table_ref(match.group(1)))
    return tables


def validate_sql_for_execution(
    sql: str,
    *,
    allowed_tables: set[str] | None = None,
) -> str | None:
    """Return an error message when SQL must not run; otherwise None."""
    readonly_error = validate_readonly_sql(sql)
    if readonly_error:
        return readonly_error

    validator = SQLValidator()
    syntax = validator.validate_syntax(sql)
    if not syntax["valid"]:
        return syntax.get("error") or "Invalid SQL syntax"

    completeness = validator.validate_completeness(sql)
    if not completeness["complete"]:
        issues = completeness.get("issues") or []
        return "; ".join(str(issue) for issue in issues) or "Incomplete SQL query"

    if allowed_tables is not None:
        allowed = {name.lower() for name in allowed_tables}
        missing = [
            table
            for table in referenced_tables(sql)
            if table.lower() not in allowed
        ]
        if missing:
            return f"Query references unknown tables: {', '.join(sorted(missing))}"

    return None
