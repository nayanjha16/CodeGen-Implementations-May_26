"""FastAPI backend for CodeGen."""

from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException

from evaluation.metrics import EvaluationMetrics
from src import __version__
from src.api.schemas import (
    EvaluateRequest,
    EvaluateResponse,
    ExecuteQueryRequest,
    ExecuteQueryResponse,
    GenerateSQLRequest,
    GenerateSQLResponse,
    HealthResponse,
    TranslateNoSQLRequest,
    TranslateNoSQLResponse,
)
from src.query_engine.engine import QueryEngine
from src.sql2nosql.translator import SQLToNoSQLTranslator
from src.text2sql.sql_executor import SQLExecutor
from src.text2sql.sql_generator import SQLGenerator
from src.utils.config import load_config

app = FastAPI(
    title="CodeGen API",
    description="Interactive Database Querying Using Small Code Language Models",
    version=__version__,
)


@lru_cache
def get_config():
    return load_config()


@lru_cache
def get_sql_generator():
    return SQLGenerator(config=get_config())


@lru_cache
def get_translator():
    return SQLToNoSQLTranslator()


@lru_cache
def get_executor():
    return SQLExecutor()


@lru_cache
def get_metrics():
    return EvaluationMetrics()


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version=__version__)


@app.post("/generate-sql", response_model=GenerateSQLResponse, tags=["Text-to-SQL"])
def generate_sql(request: GenerateSQLRequest):
    """Generate SQL from natural language question and schema."""
    try:
        result = get_sql_generator().generate(
            request.question,
            request.schema,
            decoding_strategy=request.decoding_strategy,
        )
        return GenerateSQLResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/translate-nosql", response_model=TranslateNoSQLResponse, tags=["SQL-to-NoSQL"])
def translate_nosql(request: TranslateNoSQLRequest):
    """Translate SQL query to MongoDB syntax."""
    try:
        result = get_translator().translate(request.sql)
        return TranslateNoSQLResponse(
            mongodb_query=result.get("mongodb_query", ""),
            collection=result.get("collection"),
            warnings=result.get("warnings", []),
            success=result.get("success", False),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/execute-query", response_model=ExecuteQueryResponse, tags=["Execution"])
def execute_query(request: ExecuteQueryRequest):
    """Execute SQL query against a SQLite database."""
    try:
        result = get_executor().execute(request.sql, request.db_path)
        return ExecuteQueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/evaluate", response_model=EvaluateResponse, tags=["Evaluation"])
def evaluate(request: EvaluateRequest):
    """Evaluate predicted SQL against references."""
    try:
        if len(request.predictions) != len(request.references):
            raise HTTPException(
                status_code=400,
                detail="predictions and references must have same length",
            )
        metrics = get_metrics().evaluate_all(
            request.predictions,
            request.references,
            request.db_paths,
        )
        return EvaluateResponse(metrics=metrics)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/interactive-query", tags=["Interactive"])
def interactive_query(question: str, schema: str, db_path: str | None = None):
    """Full interactive query pipeline."""
    try:
        engine = QueryEngine(config=get_config())
        return engine.process(question, schema, db_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
