"""Request/response models for the agent web API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

IntentChoice = Literal[
    "auto",
    "text2sql",
    "sql2nosql",
    "nosql2doc",
    "explain_sql",
    "validate_sql",
]


class QueryRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    intent: IntentChoice = "auto"
    sql: str | None = Field(default=None, max_length=8000)
    db_id: str | None = Field(default=None, max_length=64)
    dataset: str | None = Field(default=None, max_length=64)


class QueryResponse(BaseModel):
    answer: str
    intent: str
    sql: str = ""
    mongo_query: str = ""
    documentation: str = ""
    rows: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None


class ExampleItem(BaseModel):
    id: str
    label: str
    message: str
    intent: IntentChoice = "auto"
    sql: str | None = None


class HealthResponse(BaseModel):
    status: str
    database_profile: str
    demo_db_id: str
    codegen_api_url: str
    orchestrator_model: str
