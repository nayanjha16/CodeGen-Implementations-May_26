"""Retrievers: given a query, return relevant Rust snippets for the prompt."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path


class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, k: int) -> list[str]:
        """Return up to k Rust code snippets relevant to the query."""


_CANNED_SNIPPETS = [
    "fn factorial(n: u64) -> u64 {\n    (1..=n).product()\n}",
    "fn reverse_string(s: &str) -> String {\n    s.chars().rev().collect()\n}",
    "fn is_prime(n: u64) -> bool {\n    n > 1 && (2..=n / 2).all(|d| n % d != 0)\n}",
    "fn sum_list(values: &[i64]) -> i64 {\n    values.iter().sum()\n}",
    "fn fibonacci(n: u32) -> u64 {\n    match n {\n        0 => 0,\n        1 => 1,\n        _ => fibonacci(n - 1) + fibonacci(n - 2),\n    }\n}",
]


class MockRetriever(Retriever):
    """Canned snippets so the RAG plumbing runs with zero dependencies."""

    def retrieve(self, query: str, k: int) -> list[str]:
        return _CANNED_SNIPPETS[:k]


class TfidfRetriever(Retriever):
    """TF-IDF over a jsonl corpus ({"content": ...} per line), cosine top-k.

    Embeddings can replace this later behind the same ABC.
    """

    def __init__(self, corpus_path: str):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
        except ImportError as exc:
            raise ImportError(
                "TfidfRetriever needs scikit-learn: pip install -e '.[rag]'"
            ) from exc

        path = Path(corpus_path)
        if not path.exists():
            raise FileNotFoundError(
                f"RAG corpus not found at {corpus_path}. Drop a jsonl file with "
                '{"content": "<rust code>"} per line there (produced by the data '
                "notebooks), or use rag_backend='mock'."
            )
        with path.open() as handle:
            self._docs = [json.loads(line)["content"] for line in handle if line.strip()]
        if not self._docs:
            raise ValueError(f"RAG corpus at {corpus_path} is empty")
        self._vectorizer = TfidfVectorizer()
        self._matrix = self._vectorizer.fit_transform(self._docs)

    def retrieve(self, query: str, k: int) -> list[str]:
        from sklearn.metrics.pairwise import cosine_similarity

        scores = cosine_similarity(self._vectorizer.transform([query]), self._matrix)[0]
        top = scores.argsort()[::-1][:k]
        return [self._docs[i] for i in top]
