"""RAG: retrieve similar solved Rust examples and prepend them to the prompt."""

from __future__ import annotations

from rustgen.config import Config
from rustgen.rag.prompt import build_prompt
from rustgen.rag.retriever import MockRetriever, Retriever, TfidfRetriever

__all__ = ["MockRetriever", "Retriever", "TfidfRetriever", "build_prompt", "get_retriever"]


def get_retriever(config: Config) -> Retriever:
    if config.rag_backend == "mock":
        return MockRetriever()
    if config.rag_backend == "tfidf":
        return TfidfRetriever(config.rag_corpus_path)
    raise ValueError(
        f"Unknown rag_backend: {config.rag_backend!r} (expected 'mock' or 'tfidf')"
    )
