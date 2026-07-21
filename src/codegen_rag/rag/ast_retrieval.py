"""AST-based retrieval: index code by its abstract-syntax-tree node-type
sequence rather than (or in addition to) dense embeddings, per the proposal's
"AST-based retrieval will also be compared: code parsed into AST node type
sequences and indexed separately."

Python code is parsed with the standard-library ``ast`` module. Other
languages fall back to a lightweight structural tokenizer (keyword and
punctuation shape) so retrieval degrades gracefully rather than requiring a
tree-sitter grammar for every language up front.
"""

from __future__ import annotations

import ast as python_ast
import re
from collections import Counter
from typing import Any

from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)

_STRUCTURAL_TOKEN_RE = re.compile(
    r"\b(if|else|elif|for|while|return|def|fn|function|class|struct|impl|"
    r"try|catch|except|match|switch|case|break|continue|let|var|const)\b"
    r"|[{}()\[\];,]"
)


def extract_ast_node_sequence(code: str, language: str = "python") -> list[str]:
    """Return a sequence of structural node-type labels for ``code``.

    For Python this is the exact AST node class names (e.g. ``FunctionDef``,
    ``For``, ``BinOp``); for other languages it's a coarser but still
    order-preserving sequence of control-flow keywords and brace/paren shape.
    """
    if language.lower() == "python":
        try:
            tree = python_ast.parse(code)
        except SyntaxError:
            logger.debug("AST parse failed for python snippet; falling back to structural tokenizer")
            return _structural_fallback_sequence(code)
        return [type(node).__name__ for node in python_ast.walk(tree)]
    return _structural_fallback_sequence(code)


def _structural_fallback_sequence(code: str) -> list[str]:
    return _STRUCTURAL_TOKEN_RE.findall(code)


def ast_similarity(seq_a: list[str], seq_b: list[str]) -> float:
    """Jaccard similarity over node-type multisets — order-insensitive and
    O(n) per comparison, which matters when scoring against a large corpus."""
    if not seq_a and not seq_b:
        return 1.0
    if not seq_a or not seq_b:
        return 0.0
    counter_a, counter_b = Counter(seq_a), Counter(seq_b)
    intersection = sum((counter_a & counter_b).values())
    union = sum((counter_a | counter_b).values())
    return intersection / union if union else 0.0


class ASTRetrievalIndex:
    """In-memory AST-similarity index. Linear-scan (O(n) per query) — fine for
    the corpus sizes this project targets (thousands, not millions, of chunks);
    swap for an LSH/min-hash index if the corpus grows past that.
    """

    def __init__(self, language: str = "python"):
        self.language = language
        self.entries: list[tuple[list[str], dict[str, Any]]] = []

    def build(self, codes: list[str], metadata: list[dict[str, Any]]) -> None:
        if len(codes) != len(metadata):
            raise ValueError("codes and metadata must have the same length")
        self.entries = [
            (extract_ast_node_sequence(code, self.language), meta)
            for code, meta in zip(codes, metadata, strict=True)
        ]
        for idx, (_, meta) in enumerate(self.entries):
            meta.setdefault("chunk_id", idx)
        logger.info("Built AST retrieval index over %d entries", len(self.entries))

    def search(self, query_code: str, top_k: int = 5) -> list[dict[str, Any]]:
        query_seq = extract_ast_node_sequence(query_code, self.language)
        scored = [
            (ast_similarity(query_seq, seq), meta) for seq, meta in self.entries
        ]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [{"score": score, **meta} for score, meta in scored[:top_k]]

    def __len__(self) -> int:
        return len(self.entries)
