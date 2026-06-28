"""Tests for provider-aware semantic judge wiring."""

from __future__ import annotations

from unittest.mock import MagicMock

from src.evaluation.ollama_judge import OllamaJudge


def test_judge_uses_injected_client(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "huggingface")
    monkeypatch.setenv("HF_JUDGE_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")

    mock_client = MagicMock()
    mock_client.chat.return_value = '{"sql_correct": true, "reason": "match"}'

    judge = OllamaJudge(client=mock_client)
    result = judge.evaluate_text2sql_sample(
        predicted_sql="SELECT id FROM users WHERE active = 1",
        ground_truth_sql="SELECT name FROM users WHERE active = 1",
    )

    assert result["sql_correct"] is True
    mock_client.chat.assert_called_once()
    call_kwargs = mock_client.chat.call_args.kwargs
    assert call_kwargs["format_json"] is True
    assert call_kwargs["think"] is False
