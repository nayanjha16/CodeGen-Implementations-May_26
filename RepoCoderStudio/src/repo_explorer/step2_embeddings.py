"""
============================================================
RepoCoder Studio — Stage 4
step2_embeddings.py
============================================================

Code embedding generation via sentence-transformers, with a
deterministic mock-embedding fallback for offline/restricted-network
environments.

NOTE: Reconstructed from the Stage 4 documentation — see step1_ast_parser.py
for the reconstruction disclaimer, which applies to this whole package.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from src.logger import LOG
from src.security import redact_secrets

_E5_PREFIX_MODELS = ("e5-", "intfloat/e5")


class CodeEmbedder:
    """Wraps a sentence-transformer model with a deterministic fallback."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", batch_size: int = 32):
        self.model_name = model_name
        self.batch_size = batch_size
        self.dimension = 384
        self._model = None
        self._mock = False
        self._load()

    def _load(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
            self.dimension = self._model.get_sentence_embedding_dimension()
        except Exception as exc:  # pragma: no cover - depends on network access
            LOG.warning(
                f"Could not load embedding model '{self.model_name}' ({exc}); "
                "falling back to deterministic mock embeddings."
            )
            self._model = None
            self._mock = True

    def _uses_e5_prefix(self) -> bool:
        return any(tag in self.model_name.lower() for tag in _E5_PREFIX_MODELS)

    def _mock_vector(self, text: str) -> np.ndarray:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(digest[:8], "big", signed=False) % (2**32)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self.dimension).astype(np.float32)
        return vec

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vectors / norms

    def encode(self, texts: List[str], is_query: bool = False) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dimension), dtype=np.float32)

        prefixed = texts
        if self._uses_e5_prefix():
            prefix = "query: " if is_query else "passage: "
            prefixed = [prefix + t for t in texts]

        if self._mock or self._model is None:
            vectors = np.stack([self._mock_vector(t) for t in prefixed])
        else:
            vectors = self._model.encode(
                prefixed,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
            ).astype(np.float32)

        return self._normalize(vectors)

    def encode_query(self, query: str) -> np.ndarray:
        return self.encode([query], is_query=True)[0]

    @property
    def is_mock(self) -> bool:
        return self._mock


class EmbeddingBuilder:
    """Builds and persists function/class/module embeddings."""

    def __init__(self, indexer, embedder: CodeEmbedder, output_dir: str):
        self.indexer = indexer
        self.embedder = embedder
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _build_one(self, components: List[Any], kind: str) -> Dict[str, Any]:
        texts = [redact_secrets(c.embedding_text()) for c in components]
        vectors = self.embedder.encode(texts, is_query=False)

        np.save(self.output_dir / f"{kind}_embeddings.npy", vectors)

        metadata = {
            str(i): {
                "name": getattr(c, "name", getattr(c, "module_name", "?")),
                "file_path": c.file_path,
                **({"start_line": c.start_line} if hasattr(c, "start_line") else {}),
                "docstring": redact_secrets(getattr(c, "docstring", "")),
                "source": redact_secrets(getattr(c, "source", "")),
            }
            for i, c in enumerate(components)
        }
        (self.output_dir / f"{kind}_metadata.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )
        return {"count": len(components), "shape": list(vectors.shape)}

    def build_all(self) -> Dict[str, Any]:
        functions = self.indexer.all_functions()
        classes = self.indexer.all_classes()
        modules = self.indexer.modules

        summary = {
            "functions": self._build_one(functions, "function"),
            "classes": self._build_one(classes, "class"),
            "modules": self._build_one(modules, "module"),
            "mock_embeddings": self.embedder.is_mock,
        }
        return summary
