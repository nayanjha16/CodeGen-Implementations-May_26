"""Factory helpers for selecting Ollama or Hugging Face LLM backends."""

from __future__ import annotations

from typing import Protocol

from src.llm.huggingface_client import HuggingFaceClient
from src.llm.ollama_client import OllamaClient
from src.utils.config import get_judge_model, get_llm_provider


class ChatClient(Protocol):
    def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        *,
        format_json: bool = False,
        think: bool | None = None,
    ) -> str: ...


def create_chat_client(config: dict | None = None) -> ChatClient:
    """Return a chat client for the configured ``LLM_PROVIDER``."""
    provider = get_llm_provider(config)
    if provider == "huggingface":
        return HuggingFaceClient()
    return OllamaClient()


def create_judge(config: dict | None = None):
    """Return a semantic judge wired to the active LLM provider."""
    from src.evaluation.ollama_judge import OllamaJudge

    return OllamaJudge(model_name=get_judge_model(config), config=config)
