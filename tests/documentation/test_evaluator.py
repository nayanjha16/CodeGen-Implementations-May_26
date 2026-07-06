"""Tests for documentation evaluation metrics."""

from __future__ import annotations

from src.documentation.evaluator import DocumentationEvaluator


def test_documentation_exact_match_normalizes_whitespace_and_case():
    evaluator = DocumentationEvaluator()
    predicted = "The query counts all singer records."
    reference = "  the query   counts all singer records.  "
    assert evaluator.exact_match(predicted, reference) is True


def test_documentation_exact_match_batch():
    evaluator = DocumentationEvaluator()
    score = evaluator.exact_match_batch(
        ["Count all singers.", "Different text."],
        ["count all singers.", "Reference text."],
    )
    assert score == 0.5


def test_evaluate_all_includes_exact_match(monkeypatch):
    monkeypatch.setattr(
        "src.documentation.evaluator.embedding_similarity_batch",
        lambda predictions, references, model_name=None: 0.75,
    )
    evaluator = DocumentationEvaluator()
    result = evaluator.evaluate_all(
        ["Count all singers.", "Different text."],
        ["count all singers.", "Reference text."],
    )
    assert result["exact_match"] == 0.5
    assert result["embedding_similarity"] == 0.75
