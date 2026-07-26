"""Tool 1 — schema extraction for CodeGen prompts."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

from agent.config.settings import AgentSettings, get_settings
from agent.database.mongodb import MongoExecutor
from agent.database.postgres import PostgresExecutor, SchemaSnapshot, TableSchema
from src.utils.schema_conversion import derive_mongo_schema_json


def _tokenize(text: str) -> set[str]:
    tokens = {
        token.lower()
        for token in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text)
        if len(token) >= 2
    }
    return tokens - _STOPWORDS


_STOPWORDS = frozenset(
    {
        "how",
        "many",
        "much",
        "what",
        "which",
        "who",
        "when",
        "where",
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "by",
        "with",
        "from",
        "and",
        "or",
        "not",
        "all",
        "any",
        "each",
        "every",
        "show",
        "list",
        "get",
        "database",
        "table",
        "query",
        "sql",
        "top",
        "bottom",
        "first",
        "last",
        "do",
        "we",
        "have",
        "there",
        "this",
        "that",
        "these",
        "those",
        "be",
        "been",
        "being",
    }
)


def _name_matches(token: str, name: str) -> bool:
    token_l = token.lower()
    name_l = name.lower()
    if token_l == name_l:
        return True
    if token_l.rstrip("s") == name_l.rstrip("s"):
        return True
    if len(token_l) >= 4 and (token_l in name_l or name_l in token_l):
        return True
    return False


def _score_table(question_tokens: set[str], table: TableSchema) -> int:
    score = 0
    for token in question_tokens:
        if _name_matches(token, table.name):
            score += 2
        for column in table.columns:
            if _name_matches(token, column.name):
                score += 1
    return score


_JOIN_HINTS = frozenset(
    {
        "by",
        "per",
        "each",
        "with",
        "join",
        "between",
        "total",
        "totals",
        "sum",
        "average",
        "avg",
        "group",
    }
)


def _join_hints_in_question(question: str) -> set[str]:
    """Join-signal words kept out of `_tokenize` stopword filtering."""
    words = {
        word.lower()
        for word in re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", question)
        if len(word) >= 2
    }
    return words & _JOIN_HINTS


def _expand_foreign_keys(
    snapshot: SchemaSnapshot,
    selected: set[str],
    question_tokens: set[str],
    *,
    join_hints: set[str] | None = None,
) -> set[str]:
    """Pull in FK neighbors when a single table was scored but joins are likely."""
    if len(selected) > 1:
        return selected

    hints = (question_tokens & _JOIN_HINTS) | (join_hints or set())
    if not hints:
        return selected

    expanded = set(selected)
    for fk in snapshot.foreign_keys:
        if fk.table in selected or fk.foreign_table in selected:
            neighbor = fk.foreign_table if fk.table in selected else fk.table
            if any(_name_matches(token, neighbor) for token in question_tokens):
                expanded.add(fk.table)
                expanded.add(fk.foreign_table)
    return expanded


def select_relevant_tables(snapshot: SchemaSnapshot, question: str) -> set[str]:
    tokens = _tokenize(question)
    join_hints = _join_hints_in_question(question)
    if not tokens:
        return {table.name for table in snapshot.tables}

    scored = [(table.name, _score_table(tokens, table)) for table in snapshot.tables]
    if not any(score > 0 for _, score in scored):
        return {table.name for table in snapshot.tables}

    max_score = max(score for _, score in scored)
    if max_score >= 4:
        threshold = max(2, max_score - 2)
    else:
        threshold = max_score
    selected = {name for name, score in scored if score >= threshold and score > 0}
    if not selected:
        selected = {name for name, score in scored if score > 0}
    return _expand_foreign_keys(snapshot, selected, tokens, join_hints=join_hints)


def _filter_snapshot(snapshot: SchemaSnapshot, table_names: set[str]) -> SchemaSnapshot:
    tables = [table for table in snapshot.tables if table.name in table_names]
    foreign_keys = [
        fk
        for fk in snapshot.foreign_keys
        if fk.table in table_names and fk.foreign_table in table_names
    ]
    return SchemaSnapshot(
        db_id=snapshot.db_id,
        dataset=snapshot.dataset,
        schema_name=snapshot.schema_name,
        tables=tables,
        foreign_keys=foreign_keys,
    )


@dataclass(frozen=True)
class SchemaExtractionResult:
    tables: list[str]
    columns: list[dict[str, str]]
    relationships: list[dict[str, str]]
    schema_ddl: str
    nosql_schema: str
    db_id: str
    mongo_collections: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SchemaTool:
    """Return relevant schema slices for a natural-language question."""

    def __init__(
        self,
        settings: AgentSettings | None = None,
        postgres: PostgresExecutor | None = None,
        mongo: MongoExecutor | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._postgres = postgres or PostgresExecutor(self._settings)
        self._mongo = mongo or MongoExecutor(self._settings)
        self._owns_postgres = postgres is None
        self._owns_mongo = mongo is None

    def close(self) -> None:
        if self._owns_postgres:
            self._postgres.close()
        if self._owns_mongo:
            self._mongo.close()

    def __enter__(self) -> SchemaTool:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def extract(
        self,
        question: str,
        *,
        db_id: str | None = None,
        dataset: str | None = None,
    ) -> SchemaExtractionResult:
        snapshot = self._postgres.introspect_schema(db_id=db_id, dataset=dataset)
        selected = select_relevant_tables(snapshot, question)
        filtered = _filter_snapshot(snapshot, selected)
        mongo_collections = self._mongo.list_collections(db_id=db_id, dataset=dataset)
        relevant_collections = sorted(
            name for name in mongo_collections if name.lower() in {t.lower() for t in selected}
        ) or sorted(mongo_collections)

        columns = [
            {
                "table": table.name,
                "column": column.name,
                "type": column.data_type,
            }
            for table in filtered.tables
            for column in table.columns
        ]
        relationships = [
            {
                "from_table": fk.table,
                "from_column": fk.column,
                "to_table": fk.foreign_table,
                "to_column": fk.foreign_column,
            }
            for fk in filtered.foreign_keys
        ]
        schema_ddl = filtered.to_ddl()
        return SchemaExtractionResult(
            tables=[table.name for table in filtered.tables],
            columns=columns,
            relationships=relationships,
            schema_ddl=schema_ddl,
            nosql_schema=derive_mongo_schema_json(schema_ddl),
            db_id=filtered.db_id,
            mongo_collections=relevant_collections,
        )


def extract_schema(
    question: str,
    *,
    db_id: str | None = None,
    dataset: str | None = None,
    settings: AgentSettings | None = None,
) -> dict[str, Any]:
    """Functional entry point for MCP / LangGraph."""
    with SchemaTool(settings=settings) as tool:
        return tool.extract(question, db_id=db_id, dataset=dataset).to_dict()
