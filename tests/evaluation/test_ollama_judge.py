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


def test_documentation_judge_prefers_predicted_documentation(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "huggingface")
    monkeypatch.setenv("HF_JUDGE_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")

    mock_client = MagicMock()
    mock_client.chat.return_value = (
        '{"correctness": 8, "completeness": 8, "clarity": 8, "relevance": 8, '
        '"judge_score": 8.0, "reason": "good"}'
    )

    judge = OllamaJudge(client=mock_client)
    result = judge.evaluate_documentation_sample(
        mongodb_query="db.singer.countDocuments({})",
        raw_output="* MongoDB Query:\ndb.singer.countDocuments({})",
        predicted_documentation="Counts all singer records in the database.",
        reference_documentation="The query counts all singer records.",
    )

    assert result["judge_score"] == 8.0
    messages = mock_client.chat.call_args.args[1]
    prompt = messages[0]["content"]
    assert "Counts all singer records in the database." in prompt
    assert "* MongoDB Query:" not in prompt


def test_documentation_judge_evaluates_template_echo_output(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "huggingface")
    monkeypatch.setenv("HF_JUDGE_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")

    mock_client = MagicMock()
    mock_client.chat.return_value = (
        '{"correctness": 0, "completeness": 0, "clarity": 0, "relevance": 0, '
        '"judge_score": 0.0, "reason": "template echo"}'
    )

    judge = OllamaJudge(client=mock_client)
    result = judge.evaluate_documentation_sample(
        mongodb_query="db.stadium.find({}, {\"_id\":0,\"name\":1})",
        raw_output="* MongoDB documentation\n* MongoDB query",
        predicted_documentation="* MongoDB documentation * MongoDB query",
        reference_documentation="Returns stadium names.",
    )

    assert result["judge_score"] == 0.0
    mock_client.chat.assert_called_once()
