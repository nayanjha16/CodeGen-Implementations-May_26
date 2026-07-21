"""Upper-bound LLM client (Claude Sonnet 4, with automatic fallback).

Used by the LLM-comparison tier (Objective 3 / Task 3) and the RAG pipeline's
generation step (Checkpoint 3). Kept separate from ``codegen_wrapper.py``
because it talks to a hosted API rather than a locally loaded checkpoint.
"""

from __future__ import annotations

from dataclasses import dataclass

from codegen_rag.config import get_secret
from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


class LLMUnavailableError(RuntimeError):
    """Raised when no configured upper-bound LLM could be reached."""


def _requires_max_completion_tokens(model: str) -> bool:
    """True for OpenAI model families that require `max_completion_tokens`
    instead of the classic Chat Completions `max_tokens` param (gpt-5 and the
    o-series reasoning models)."""
    newer_prefixes = ("gpt-5", "o1", "o3", "o4")
    return model.startswith(newer_prefixes)


@dataclass
class LLMResponse:
    text: str
    model_used: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class UpperBoundLLMClient:
    """Calls Claude Sonnet 4 first; falls back through ``fallback_order`` on error.

    This mirrors the proposal's requirement: "Use Claude Sonnet 4 as the large
    LLM comparison model. If unavailable, automatically substitute GPT-5 or
    another state-of-the-art coding LLM."
    """

    def __init__(
        self,
        primary: str = "claude-sonnet-4-20250514",
        fallback_order: list[str] | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.2,
    ):
        self.primary = primary
        self.fallback_order = fallback_order or ["gpt-5", "gpt-4o", "claude-3-5-sonnet-20241022"]
        self.max_tokens = max_tokens
        self.temperature = temperature

    def _call_anthropic(self, model: str, system: str, prompt: str) -> LLMResponse:
        import anthropic

        api_key = get_secret("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMUnavailableError("ANTHROPIC_API_KEY not set")
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in message.content if hasattr(block, "text"))
        return LLMResponse(
            text=text,
            model_used=model,
            prompt_tokens=message.usage.input_tokens,
            completion_tokens=message.usage.output_tokens,
        )

    def _call_openai(self, model: str, system: str, prompt: str) -> LLMResponse:
        import openai

        api_key = get_secret("OPENAI_API_KEY")
        if not api_key:
            raise LLMUnavailableError("OPENAI_API_KEY not set")
        client = openai.OpenAI(api_key=api_key)

        # Newer OpenAI model families (gpt-5, the o-series reasoning models)
        # reject the classic Chat Completions `max_tokens` param outright --
        # "Unsupported parameter: 'max_tokens' is not supported with this
        # model. Use 'max_completion_tokens' instead" -- while older families
        # (gpt-4o, gpt-4, gpt-3.5) still expect `max_tokens` and don't accept
        # `max_completion_tokens`. The fallback list mixes both generations,
        # so pick the right kwarg name per model instead of hardcoding one.
        token_kwarg = {
            ("max_completion_tokens" if _requires_max_completion_tokens(model) else "max_tokens"): self.max_tokens
        }

        completion = client.chat.completions.create(
            model=model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            **token_kwarg,
        )
        choice = completion.choices[0].message.content or ""
        usage = completion.usage
        return LLMResponse(
            text=choice,
            model_used=model,
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
        )

    def generate(
        self,
        prompt: str,
        system: str = "You are an expert software engineer.",
    ) -> LLMResponse:
        """Try the primary model, then walk the fallback chain on any failure."""
        candidates = [self.primary, *self.fallback_order]
        last_error: Exception | None = None

        for model in candidates:
            try:
                if model.startswith("claude"):
                    return self._call_anthropic(model, system, prompt)
                return self._call_openai(model, system, prompt)
            except Exception as exc:  # noqa: BLE001 - deliberately broad, we fall back
                logger.warning("Upper-bound LLM call failed for model=%s: %s", model, exc)
                last_error = exc
                continue

        raise LLMUnavailableError(
            f"All upper-bound LLM candidates failed. Tried: {candidates}. Last error: {last_error}"
        )
