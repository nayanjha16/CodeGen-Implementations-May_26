"""Tests for LLM backend factory and Hugging Face chat client."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.llm.factory import create_chat_client, create_judge
from src.llm.huggingface_client import HuggingFaceClient
from src.llm.ollama_client import OllamaClient


def test_create_chat_client_defaults_to_ollama(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    client = create_chat_client({})
    assert isinstance(client, OllamaClient)


def test_create_chat_client_uses_huggingface(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "huggingface")
    client = create_chat_client({})
    assert isinstance(client, HuggingFaceClient)


def test_create_judge_uses_provider_model(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "huggingface")
    monkeypatch.setenv("HF_JUDGE_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")

    mock_client = MagicMock()
    with patch("src.evaluation.ollama_judge.create_chat_client", return_value=mock_client):
        judge = create_judge({})

    assert judge.model_name == "Qwen/Qwen2.5-0.5B-Instruct"
    assert judge.provider == "huggingface"
    assert judge._client is mock_client


def test_huggingface_client_adds_json_instruction():
    messages = [{"role": "user", "content": "Compare these queries."}]
    prepared = HuggingFaceClient._prepare_messages(messages, format_json=True)
    assert "valid JSON only" in prepared[-1]["content"]


def test_huggingface_client_chat_uses_chat_template():
    client = HuggingFaceClient(device="cpu")

    tokenizer = MagicMock()
    tokenizer.chat_template = "<chat>"
    tokenizer.pad_token_id = 0
    tokenizer.eos_token_id = 0
    tokenizer.apply_chat_template.return_value = "prompt"

    input_ids = MagicMock()
    input_ids.shape = (1, 3)
    inputs = MagicMock()
    inputs.__getitem__.return_value = input_ids
    inputs.to.return_value = inputs
    tokenizer.return_value = inputs
    tokenizer.decode.return_value = '{"sql_correct": true, "reason": "ok"}'

    output_ids = MagicMock()
    output_ids.__getitem__.return_value = MagicMock()
    model = MagicMock()
    model.generate.return_value = output_ids

    client._models["demo-model"] = (tokenizer, model)

    response = client.chat(
        "demo-model",
        [{"role": "user", "content": "Judge this."}],
        format_json=True,
    )

    assert response == '{"sql_correct": true, "reason": "ok"}'
    tokenizer.apply_chat_template.assert_called_once()
    model.generate.assert_called_once()
