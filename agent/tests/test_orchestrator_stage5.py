"""Stage 5 unit tests — intent, planner, retry, orchestrator LLM (mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agent.orchestrator import (
    IntentDetector,
    PlanStep,
    RetryState,
    build_plan,
    classify_by_rules,
    should_retry_sql,
)
from agent.orchestrator.intent_detector import extract_sql_from_message


def test_classify_text2sql_question() -> None:
    result = classify_by_rules("How many customers are in the database?")
    assert result is not None
    assert result.intent == "text2sql"


def test_classify_sql2nosql() -> None:
    result = classify_by_rules("Convert this SQL to MongoDB syntax")
    assert result is not None
    assert result.intent == "sql2nosql"


def test_classify_explain_sql_from_select() -> None:
    result = classify_by_rules("Explain this SQL: SELECT * FROM customers")
    assert result is not None
    assert result.intent == "explain_sql"


def test_extract_sql_from_fence() -> None:
    sql = extract_sql_from_message("Please run:\n```sql\nSELECT 1\n```")
    assert sql == "SELECT 1"


def test_build_plan_text2sql_steps() -> None:
    plan = build_plan("text2sql")
    assert plan.steps[0] == PlanStep.EXTRACT_SCHEMA
    assert PlanStep.GENERATE_SQL in plan.steps
    assert PlanStep.EXECUTE_POSTGRES in plan.steps


def test_build_plan_nosql2doc() -> None:
    plan = build_plan("nosql2doc")
    assert plan.steps == (PlanStep.GENERATE_DOCUMENTATION, PlanStep.SUMMARIZE)


def test_retry_state_can_retry_until_max() -> None:
    state = RetryState(max_retries=3)
    state.record_failure(sql="SELECT bad", error="relation missing")
    assert should_retry_sql(state, success=False) is True
    state.record_failure(sql="SELECT bad", error="relation missing")
    state.record_failure(sql="SELECT bad", error="relation missing")
    assert state.exhausted is True
    assert should_retry_sql(state, success=False) is False


def test_intent_detector_explicit_override() -> None:
    llm = MagicMock()
    result = IntentDetector(llm=llm).detect(
        "anything",
        explicit_intent="sql2nosql",
    )
    assert result.intent == "sql2nosql"
    assert result.source == "explicit"
    llm.classify_intent.assert_not_called()


def test_intent_detector_llm_fallback() -> None:
    llm = MagicMock()
    llm.classify_intent.return_value = ("nosql2doc", 0.8)
    result = IntentDetector(llm=llm, use_llm_fallback=True).detect("Tell me about this pipeline")
    assert result.intent == "nosql2doc"
    assert result.source == "llm"


def test_orchestrator_summarize_delegates_to_ollama() -> None:
    from agent.clients.orchestrator_llm import OrchestratorLLM

    mock_client = MagicMock()
    mock_client.chat.return_value = "There are 59 customers."
    llm = OrchestratorLLM(client=mock_client)
    answer = llm.summarize_results(
        question="How many customers?",
        query='SELECT COUNT(*) FROM "Customer"',
        rows=[{"c": 59}],
    )
    assert "59" in answer
    mock_client.chat.assert_called_once()
