"""OpenAI-compatible request/response models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "codegen-multi-adapter"
    messages: list[ChatMessage]
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = Field(default=None, description="Maps to max_new_tokens")
    stream: bool = False
    # Optional override when the client already knows the task.
    intent: str | None = None


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str = "stop"


class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class IntentMetadata(BaseModel):
    intent: str
    confidence: float
    method: str
    scores: dict[str, float] = Field(default_factory=dict)
    adapter: str | None = None
    checkpoint_version: str | None = None


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: UsageInfo = Field(default_factory=UsageInfo)
    # Capstone extension: routing metadata (ignored by strict OpenAI clients).
    codegen_routing: IntentMetadata | None = None


class ModelCard(BaseModel):
    id: str
    object: str = "model"
    owned_by: str = "codegen-capstone"


class ModelList(BaseModel):
    object: str = "list"
    data: list[ModelCard]


class HealthResponse(BaseModel):
    status: str
    router: dict[str, Any]
