"""Pydantic request/response schemas for the FastAPI backend."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    base_model: str
    active_checkpoints: dict[str, str | None] = Field(
        default_factory=dict,
        description=(
            "Per-language fine-tuned checkpoint currently served (e.g. "
            "{'rust': '.../checkpoints/rust_full'}), or null if that "
            "language has no trained checkpoint yet and falls back to the "
            "base model."
        ),
    )


class GenerateRequest(BaseModel):
    problem_description: str = Field(..., min_length=1, description="Natural-language problem statement")
    language: str = Field("python", description="Target programming language: python | java | cpp | rust")


class GenerateResponse(BaseModel):
    code: str
    language: str


class DocumentRequest(BaseModel):
    code: str = Field(..., min_length=1, description="Source code to document")
    language: str = "python"


class DocumentResponse(BaseModel):
    docstring: str


class TranslateRequest(BaseModel):
    source_code: str = Field(..., min_length=1, description="Source code to translate")
    source_language: str = Field("python", description="Language the source code is written in")
    target_language: str = Field("java", description="Language to translate the code into")


class TranslateResponse(BaseModel):
    translated_code: str
    source_language: str
    target_language: str


class SQLRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Natural-language question")
    db_id: str = Field(..., description="Database identifier (must exist in the configured databases dir)")


class SQLResponse(BaseModel):
    sql: str
    db_id: str


class RAGRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Query or problem description to retrieve context for")
    task: str = Field("program_synthesis", description="Downstream task: program_synthesis | documentation_generation")
    top_k: int = Field(5, ge=1, le=20)
    strategy: str = Field("hybrid", description="dense | ast | hybrid")
    use_llm: bool = Field(False, description="If true, generate with the upper-bound LLM instead of the small LM")


class RAGResponse(BaseModel):
    generation: str
    retrieved_count: int
    strategy: str
    top_k: int
    used_llm: bool


class ErrorResponse(BaseModel):
    detail: str
