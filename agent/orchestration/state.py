"""Shared agent run state and result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypedDict

from agent.orchestrator.intent_detector import AgentIntent


@dataclass
class RunContext:
    user_message: str
    db_id: str | None = None
    dataset: str | None = None
    intent: AgentIntent = "text2sql"
    schema_ddl: str = ""
    nosql_schema: str = ""
    allowed_tables: set[str] = field(default_factory=set)
    sql: str = ""
    mongo_query: str = ""
    documentation: str = ""
    explanation: str = ""
    rows: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    validation_message: str | None = None


@dataclass(frozen=True)
class AgentResult:
    answer: str
    intent: AgentIntent
    sql: str = ""
    mongo_query: str = ""
    documentation: str = ""
    rows: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "intent": self.intent,
            "sql": self.sql,
            "mongo_query": self.mongo_query,
            "documentation": self.documentation,
            "rows": self.rows,
            "error": self.error,
        }


class AgentState(TypedDict, total=False):
    user_message: str
    explicit_intent: str | None
    db_id: str | None
    dataset: str | None
    intent: str
    answer: str
    sql: str
    mongo_query: str
    documentation: str
    rows: list[dict[str, Any]]
    error: str | None
