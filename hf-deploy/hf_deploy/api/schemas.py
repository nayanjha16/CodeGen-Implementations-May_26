"""OpenAI-compatible request/response models."""

from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

_USER_QUERY_RE = re.compile(
    r"<user_query>\s*(.*?)\s*</user_query>",
    re.IGNORECASE | re.DOTALL,
)


def normalize_message_content(content: Any) -> str:
    """Accept OpenAI string or multimodal content-part lists (Cursor sends lists)."""
    if content is None:
        return ""
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        chunks: list[str] = []
        for part in content:
            if isinstance(part, str):
                chunks.append(part)
            elif isinstance(part, dict):
                if part.get("type") == "text" and isinstance(part.get("text"), str):
                    chunks.append(part["text"])
                elif isinstance(part.get("text"), str):
                    chunks.append(part["text"])
            else:
                text_attr = getattr(part, "text", None)
                if isinstance(text_attr, str):
                    chunks.append(text_attr)
        text = "\n".join(chunk for chunk in chunks if chunk)
    else:
        text = str(content)

    match = _USER_QUERY_RE.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str

    @field_validator("content", mode="before")
    @classmethod
    def _coerce_content(cls, value: Any) -> str:
        return normalize_message_content(value)


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
