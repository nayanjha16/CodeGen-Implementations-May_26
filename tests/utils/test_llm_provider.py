"""Tests for LLM provider configuration."""

from __future__ import annotations

import pytest

from src.utils.config import (
    get_hf_judge_model,
    get_judge_model,
    get_llm_provider,
    get_ollama_judge_model,
)


@pytest.mark.parametrize(
    ("env_value", "expected"),
    [
        (None, "ollama"),
        ("ollama", "ollama"),
        ("huggingface", "huggingface"),
        ("HuggingFace", "huggingface"),
    ],
)
def test_get_llm_provider(monkeypatch, env_value, expected):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    if env_value is not None:
        monkeypatch.setenv("LLM_PROVIDER", env_value)
    assert get_llm_provider({}) == expected


def test_get_llm_provider_invalid(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    with pytest.raises(ValueError, match="Invalid LLM_PROVIDER"):
        get_llm_provider({})


def test_get_judge_model_uses_provider_specific_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_JUDGE_MODEL", "qwen3:8b")
    monkeypatch.setenv("HF_JUDGE_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
    assert get_judge_model({}) == "qwen3:8b"

    monkeypatch.setenv("LLM_PROVIDER", "huggingface")
    assert get_judge_model({}) == "Qwen/Qwen2.5-0.5B-Instruct"


def test_ollama_judge_model_requires_env(monkeypatch):
    monkeypatch.delenv("OLLAMA_JUDGE_MODEL", raising=False)
    monkeypatch.setattr("src.utils.config._load_env", lambda: None)
    with pytest.raises(ValueError, match="OLLAMA_JUDGE_MODEL is not set"):
        get_ollama_judge_model({})


def test_hf_judge_model_requires_env(monkeypatch):
    monkeypatch.delenv("HF_JUDGE_MODEL", raising=False)
    monkeypatch.setattr("src.utils.config._load_env", lambda: None)
    with pytest.raises(ValueError, match="HF_JUDGE_MODEL is not set"):
        get_hf_judge_model({})
