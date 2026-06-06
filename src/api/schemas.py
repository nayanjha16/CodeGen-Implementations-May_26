"""Pydantic schemas for API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class GenerateSQLRequest(BaseModel):
    question: str = Field(..., description="Natural language question")
    schema: str = Field(..., description="Database schema")
    decoding_strategy: str = Field("greedy", description="greedy or beam")


class GenerateSQLResponse(BaseModel):
    sql: str
    raw_output: str
    prompt: str


class TranslateNoSQLRequest(BaseModel):
    sql: str = Field(..., description="SQL query to translate")


class TranslateNoSQLResponse(BaseModel):
    mongodb_query: str
    collection: str | None = None
    warnings: list[str] = []
    success: bool


class ExecuteQueryRequest(BaseModel):
    sql: str = Field(..., description="SQL query to execute")
    db_path: str = Field(..., description="Path to SQLite database")


class ExecuteQueryResponse(BaseModel):
    success: bool
    rows: list[dict[str, Any]]
    row_count: int
    error: str | None = None


class EvaluateRequest(BaseModel):
    predictions: list[str]
    references: list[str]
    db_paths: list[str | None] | None = None


class EvaluateResponse(BaseModel):
    metrics: dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    version: str
