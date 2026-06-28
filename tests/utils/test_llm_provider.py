"""Tests for LLM provider configuration."""

from __future__ import annotations

import pytest

from src.utils.config import (
    DEFAULT_HF_CODEGEN_MODEL,
    DEFAULT_HF_JUDGE_MODEL,
    get_hf_codegen_model,
    get_hf_judge_model,
    get_judge_model,
    get_llm_codegen_model,
    get_llm_provider,
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
    monkeypatch.setenv("OLLAMA_JUDGE_MODEL", "qwen3:4b")
    monkeypatch.setenv("HF_JUDGE_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")
    assert get_judge_model({}) == "qwen3:4b"

    monkeypatch.setenv("LLM_PROVIDER", "huggingface")
    assert get_judge_model({}) == "Qwen/Qwen2.5-0.5B-Instruct"


def test_get_llm_codegen_model_uses_provider_specific_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_CODEGEN_MODEL", "qwen2.5-coder:3b")
    monkeypatch.setenv("HF_CODEGEN_MODEL", "Qwen/Qwen2.5-Coder-0.5B-Instruct")
    assert get_llm_codegen_model({}) == "qwen2.5-coder:3b"

    monkeypatch.setenv("LLM_PROVIDER", "huggingface")
    assert get_llm_codegen_model({}) == "Qwen/Qwen2.5-Coder-0.5B-Instruct"


def test_hf_model_defaults(monkeypatch):
    monkeypatch.delenv("HF_JUDGE_MODEL", raising=False)
    monkeypatch.delenv("HF_CODEGEN_MODEL", raising=False)
    assert get_hf_judge_model({}) == DEFAULT_HF_JUDGE_MODEL
    assert get_hf_codegen_model({}) == DEFAULT_HF_CODEGEN_MODEL
