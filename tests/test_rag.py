import json

import pytest

from rustgen.config import Config
from rustgen.rag import get_retriever
from rustgen.rag.prompt import build_prompt
from rustgen.rag.retriever import MockRetriever
from rustgen.translator.base import TranslationTask


def test_mock_retriever_returns_k_snippets():
    retriever = MockRetriever()
    for k in (1, 3, 5):
        examples = retriever.retrieve("sum a list of numbers", k)
        assert len(examples) == k
        assert all("fn " in example for example in examples)


def test_get_retriever_default_is_mock():
    assert isinstance(get_retriever(Config()), MockRetriever)


def test_tfidf_retriever_ranks_by_similarity(tmp_path):
    pytest.importorskip("sklearn")
    from rustgen.rag.retriever import TfidfRetriever

    docs = [
        "fn add(a: i64, b: i64) -> i64 { a + b }",
        "fn reverse_string(s: &str) -> String { s.chars().rev().collect() }",
        "fn is_prime(n: u64) -> bool { n > 1 && (2..=n / 2).all(|d| n % d != 0) }",
    ]
    corpus = tmp_path / "corpus.jsonl"
    corpus.write_text("\n".join(json.dumps({"content": doc}) for doc in docs))

    retriever = TfidfRetriever(str(corpus))
    results = retriever.retrieve("add two numbers", 2)
    assert len(results) == 2
    assert results[0] == docs[0]


def test_build_prompt_assembles_all_sections():
    task = TranslationTask(
        description="Add two integers.",
        python_code="def add(a, b):\n    return a + b",
        signature="fn add(a: i64, b: i64) -> i64",
    )
    prompt = build_prompt(task, ["fn one() -> i64 { 1 }"])

    assert prompt.startswith("// Example:")
    assert "fn one() -> i64 { 1 }" in prompt
    assert "/// Add two integers." in prompt
    assert "// Python reference:" in prompt
    assert "// def add(a, b):" in prompt
    assert prompt.rstrip().endswith("fn add(a: i64, b: i64) -> i64")
    assert prompt.index("// Example:") < prompt.index("/// Add two integers.")


def test_build_prompt_without_examples_or_extras():
    prompt = build_prompt(TranslationTask(description="Reverse a string."), [])
    assert prompt == "/// Reverse a string."
