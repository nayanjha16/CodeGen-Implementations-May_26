from __future__ import annotations

import pytest

from codegen_rag.models.model_registry import (
    LLMResponse,
    LLMUnavailableError,
    UpperBoundLLMClient,
    _requires_max_completion_tokens,
)


def test_generate_uses_primary_model_when_it_succeeds(monkeypatch):
    client = UpperBoundLLMClient(primary="claude-sonnet-4-20250514", fallback_order=["gpt-5"])
    monkeypatch.setattr(
        client, "_call_anthropic", lambda model, system, prompt: LLMResponse(text="ok", model_used=model)
    )
    response = client.generate("write a function")
    assert response.model_used == "claude-sonnet-4-20250514"
    assert response.text == "ok"


def test_generate_falls_back_to_next_candidate_on_failure(monkeypatch):
    client = UpperBoundLLMClient(primary="claude-sonnet-4-20250514", fallback_order=["gpt-5", "gpt-4o"])

    def failing_anthropic(model, system, prompt):
        raise RuntimeError("primary unavailable")

    def working_openai(model, system, prompt):
        return LLMResponse(text="fallback ok", model_used=model)

    monkeypatch.setattr(client, "_call_anthropic", failing_anthropic)
    monkeypatch.setattr(client, "_call_openai", working_openai)

    response = client.generate("write a function")
    assert response.model_used == "gpt-5"
    assert response.text == "fallback ok"


def test_generate_raises_when_all_candidates_fail(monkeypatch):
    client = UpperBoundLLMClient(primary="claude-sonnet-4-20250514", fallback_order=["gpt-5"])
    monkeypatch.setattr(
        client, "_call_anthropic", lambda *a: (_ for _ in ()).throw(RuntimeError("no key"))
    )
    monkeypatch.setattr(
        client, "_call_openai", lambda *a: (_ for _ in ()).throw(RuntimeError("no key"))
    )
    with pytest.raises(LLMUnavailableError):
        client.generate("write a function")


@pytest.mark.parametrize(
    "model,expected",
    [
        ("gpt-5", True),
        ("gpt-5-mini", True),
        ("o1", True),
        ("o1-preview", True),
        ("o3-mini", True),
        ("o4-mini", True),
        ("gpt-4o", False),
        ("gpt-4", False),
        ("gpt-4o-mini", False),
        ("gpt-3.5-turbo", False),
    ],
)
def test_requires_max_completion_tokens(model, expected):
    assert _requires_max_completion_tokens(model) is expected


def test_call_openai_uses_max_completion_tokens_for_gpt5(monkeypatch):
    """Regression test: gpt-5 rejects `max_tokens` outright ('Unsupported
    parameter: max_tokens ... Use max_completion_tokens instead'). The client
    must send `max_completion_tokens` for gpt-5 and `max_tokens` for gpt-4o."""
    import sys
    import types

    captured_kwargs = {}

    class FakeMessage:
        content = "ok"

    class FakeChoice:
        message = FakeMessage()

    class FakeUsage:
        prompt_tokens = 10
        completion_tokens = 5

    class FakeCompletion:
        choices = [FakeChoice()]
        usage = FakeUsage()

    class FakeChatCompletions:
        @staticmethod
        def create(**kwargs):
            captured_kwargs.update(kwargs)
            return FakeCompletion()

    class FakeChat:
        completions = FakeChatCompletions()

    class FakeOpenAIClient:
        def __init__(self, api_key=None):
            self.chat = FakeChat()

    fake_openai = types.ModuleType("openai")
    fake_openai.OpenAI = FakeOpenAIClient
    monkeypatch.setitem(sys.modules, "openai", fake_openai)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    client = UpperBoundLLMClient(primary="claude-sonnet-4-20250514")
    client._call_openai("gpt-5", "system prompt", "user prompt")
    assert "max_completion_tokens" in captured_kwargs
    assert "max_tokens" not in captured_kwargs

    captured_kwargs.clear()
    client._call_openai("gpt-4o", "system prompt", "user prompt")
    assert "max_tokens" in captured_kwargs
    assert "max_completion_tokens" not in captured_kwargs


def test_generate_tries_candidates_in_declared_order(monkeypatch):
    calls: list[str] = []
    client = UpperBoundLLMClient(primary="claude-sonnet-4-20250514", fallback_order=["gpt-5", "gpt-4o"])

    def record_and_fail_anthropic(model, system, prompt):
        calls.append(model)
        raise RuntimeError("fail")

    def record_and_fail_openai(model, system, prompt):
        calls.append(model)
        raise RuntimeError("fail")

    monkeypatch.setattr(client, "_call_anthropic", record_and_fail_anthropic)
    monkeypatch.setattr(client, "_call_openai", record_and_fail_openai)

    with pytest.raises(LLMUnavailableError):
        client.generate("prompt")

    assert calls == ["claude-sonnet-4-20250514", "gpt-5", "gpt-4o"]
