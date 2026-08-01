"""Stage 4 — repository understanding (AST indexing, embeddings, FAISS
search, dependency graphs) exposed through RepositoryExplorer.

See step1_ast_parser.py for a note on how these modules were assembled.
"""

from .step5_repository_explorer import RepositoryExplorer

__all__ = ["RepositoryExplorer"]
