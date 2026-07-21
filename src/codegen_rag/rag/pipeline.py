"""End-to-end RAG pipeline: embed -> retrieve (dense / AST / hybrid) -> pack
context -> augment prompt -> generate.

Decoupled from any specific model via two injected callables (``embed_fn`` and
``generate_fn``) so the exact same pipeline object can drive "fine-tuned model
inside RAG", "LLM + RAG", or a unit test with fakes — matching the four-tier
comparison the proposal requires (small LM, LLM no-RAG, LLM+RAG, fine-tuned+RAG).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

from codegen_rag.rag.ast_retrieval import ASTRetrievalIndex
from codegen_rag.rag.context_packing import build_augmented_prompt, dynamic_top_k, pack_context
from codegen_rag.rag.faiss_index import CodeSearchIndex
from codegen_rag.rag.hybrid_retrieval import HybridRetriever
from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)

RetrievalStrategy = Literal["dense", "ast", "hybrid"]


@dataclass
class RAGResult:
    query: str
    retrieved_chunks: list[dict[str, Any]]
    augmented_prompt: str
    generation: str
    strategy: str
    top_k: int


class RAGPipeline:
    def __init__(
        self,
        dense_index: CodeSearchIndex | None = None,
        ast_index: ASTRetrievalIndex | None = None,
        embed_fn: Callable[[str], Any] | None = None,
        strategy: RetrievalStrategy = "hybrid",
        top_k: int = 5,
        max_context_chars: int = 2000,
        use_dynamic_top_k: bool = False,
        dynamic_top_k_kwargs: dict[str, Any] | None = None,
    ):
        if strategy in ("dense", "hybrid") and (dense_index is None or embed_fn is None):
            raise ValueError(f"strategy='{strategy}' requires both dense_index and embed_fn")
        if strategy in ("ast", "hybrid") and ast_index is None:
            raise ValueError(f"strategy='{strategy}' requires ast_index")

        self.dense_index = dense_index
        self.ast_index = ast_index
        self.embed_fn = embed_fn
        self.strategy = strategy
        self.top_k = top_k
        self.max_context_chars = max_context_chars
        self.use_dynamic_top_k = use_dynamic_top_k
        self.dynamic_top_k_kwargs = dynamic_top_k_kwargs or {}

        self._hybrid = (
            HybridRetriever(dense_index, ast_index) if strategy == "hybrid" and dense_index and ast_index else None
        )

    def retrieve(self, query: str) -> list[dict[str, Any]]:
        search_top_k = self.top_k * 2 if self.use_dynamic_top_k else self.top_k

        if self.strategy == "dense":
            query_embedding = self.embed_fn(query)
            results = self.dense_index.search(query_embedding, top_k=search_top_k)
        elif self.strategy == "ast":
            results = self.ast_index.search(query, top_k=search_top_k)
        else:  # hybrid
            query_embedding = self.embed_fn(query)
            results = self._hybrid.search(query, query_embedding, top_k=search_top_k)

        if self.use_dynamic_top_k:
            score_key = "fusion_score" if self.strategy == "hybrid" else "score"
            results = dynamic_top_k(results, score_key=score_key, max_k=self.top_k, **self.dynamic_top_k_kwargs)

        return results

    def build_prompt(self, query: str, task_instruction: str = "") -> tuple[str, list[dict[str, Any]]]:
        retrieved = self.retrieve(query)
        context = pack_context(retrieved, max_chars=self.max_context_chars)
        prompt = build_augmented_prompt(query, context, task_instruction)
        return prompt, retrieved

    def generate(
        self,
        query: str,
        generate_fn: Callable[[str], str],
        task_instruction: str = "",
    ) -> RAGResult:
        """Run retrieval + generation end to end. ``generate_fn`` is any
        callable ``str -> str`` — e.g. ``lambda p: llm_client.generate(p).text``
        or ``lambda p: codegen_model.generate(p)[0]`` — so this pipeline works
        identically for the LLM+RAG tier and the fine-tuned-model+RAG tier.
        """
        prompt, retrieved = self.build_prompt(query, task_instruction)
        completion = generate_fn(prompt)
        return RAGResult(
            query=query,
            retrieved_chunks=retrieved,
            augmented_prompt=prompt,
            generation=completion,
            strategy=self.strategy,
            top_k=self.top_k,
        )
