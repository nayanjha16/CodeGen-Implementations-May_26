"""Tests for intent classification (rules path; embeddings optional)."""

from __future__ import annotations

import pytest

from codegen_api import CLARIFY_INTENT
from codegen_api.classifier import IntentClassifier


@pytest.fixture
def rules_only() -> IntentClassifier:
    return IntentClassifier(
        confidence_threshold=0.45,
        prefer_rules=True,
        use_embeddings=False,
    )


@pytest.mark.parametrize(
    ("text", "intent"),
    [
        ("Write a SQL query to find all customers", "text2sql"),
        ("generate a sql query for top orders", "text2sql"),
        ("Convert this SQL query to NoSQL / MongoDB", "sql2nosql"),
        ("rewrite the sql as a mongo aggregation", "sql2nosql"),
        ("generate nosql query for the following sql", "sql2nosql"),
        ("Generate a MongoDB query for this SQL:\nSELECT * FROM t", "sql2nosql"),
        ("Generate documentation for this MongoDB query", "nosql2doc"),
        ("please document this collection pipeline", "nosql2doc"),
        ("Task: text2sql\n\nSchema:\nT(a)\n\nQuestion:\nQ\n\nSQL:", "text2sql"),
        ("Task: sql2nosql\n\nConvert the SQL query...", "sql2nosql"),
        ("Task: nosql2doc", "nosql2doc"),
    ],
)
def test_rule_classification(
    rules_only: IntentClassifier, text: str, intent: str
) -> None:
    result = rules_only.classify(text)
    assert result.intent == intent
    assert result.method in {"rules", "task_tag"}
    assert result.confidence >= 0.9


def test_empty_prompt_clarifies(rules_only: IntentClassifier) -> None:
    result = rules_only.classify("   ")
    assert result.intent == CLARIFY_INTENT


def test_unknown_without_embeddings_clarifies(rules_only: IntentClassifier) -> None:
    result = rules_only.classify("hello there how are you")
    assert result.intent == CLARIFY_INTENT


def test_format_prompt_prefix() -> None:
    from codegen_api.prompt import format_generation_prompt

    out = format_generation_prompt("text2sql", "Schema:\nT(a)\n\nQuestion:\nQ\n\nSQL:")
    assert out.startswith("Task: text2sql\n\n")
    assert "Schema:" in out
