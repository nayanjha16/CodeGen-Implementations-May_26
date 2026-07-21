"""Builds the dense (FAISS) and AST retrieval indexes over a code corpus.

This is the "index some programs of the same language and use it for RAG"
step from the proposal (Task 3.2), producing the "FAISS vector index with
2000+ code samples" deliverable artifact.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import numpy as np

from codegen_rag.rag.ast_retrieval import ASTRetrievalIndex
from codegen_rag.rag.faiss_index import CodeSearchIndex
from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


def build_indexes_from_corpus(
    corpus: list[dict[str, Any]],
    embed_fn: Callable[[list[str]], np.ndarray],
    embedding_dim: int,
    language: str = "python",
    code_key: str = "code",
    batch_size: int = 32,
    use_ivf: bool = True,
) -> tuple[CodeSearchIndex, ASTRetrievalIndex]:
    """Embed every corpus entry in batches, then build both indexes over the
    same ordered corpus (so `chunk_id` aligns between them for hybrid fusion).
    """
    codes = [entry[code_key] for entry in corpus]
    metadata = [{**entry, "chunk_id": i} for i, entry in enumerate(corpus)]

    embeddings = np.zeros((len(codes), embedding_dim), dtype="float32")
    for start in range(0, len(codes), batch_size):
        batch = codes[start : start + batch_size]
        batch_embeddings = embed_fn(batch)
        embeddings[start : start + len(batch)] = np.asarray(batch_embeddings)
        if (start // batch_size) % 10 == 0:
            logger.info("Embedded %d/%d corpus entries", start + len(batch), len(codes))

    dense_index = CodeSearchIndex(dim=embedding_dim, use_ivf=use_ivf)
    dense_index.build(embeddings, metadata)

    ast_index = ASTRetrievalIndex(language=language)
    ast_index.build(codes, [dict(m) for m in metadata])

    logger.info("Built dense (%d vectors) and AST (%d entries) indexes", len(dense_index), len(ast_index))
    return dense_index, ast_index


def save_indexes(dense_index: CodeSearchIndex, ast_index: ASTRetrievalIndex, root: Path) -> None:
    import pickle

    root.mkdir(parents=True, exist_ok=True)
    dense_index.save(root / "dense")
    with open(root / "ast_index.pkl", "wb") as fh:
        pickle.dump(ast_index, fh)
    logger.info("Saved RAG indexes to %s", root)


def load_indexes(root: Path) -> tuple[CodeSearchIndex, ASTRetrievalIndex]:
    import pickle

    dense_index = CodeSearchIndex.load(root / "dense")
    with open(root / "ast_index.pkl", "rb") as fh:
        ast_index = pickle.load(fh)
    return dense_index, ast_index
