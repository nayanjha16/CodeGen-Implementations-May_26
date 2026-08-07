"""
Schema pruning — trims the schema string to only the tables/collections
relevant to the current query, reducing noise and freeing token budget.

Strategy per task:
  sql2nosql  : parse FROM/JOIN from input SQL → exact match, no ML needed
  text2sql   : cosine similarity (BGE-small) between question embedding and
  text2nosql   pre-encoded table/collection embeddings → top-k + FK expansion

Pre-built index (generated once by scripts/build_retrieval_index.py):
  retrieval_index/schema_spider_embeddings.npy      (~747 tables,  384-dim)
  retrieval_index/schema_spider_metadata.json
  retrieval_index/schema_docspider_embeddings.npy   (~716 collections, 384-dim)
  retrieval_index/schema_docspider_metadata.json
"""

import os
import re
import json
import numpy as np

RETRIEVAL_INDEX_DIR = "retrieval_index"
BGE_MODEL_ID = "BAAI/bge-small-en-v1.5"
_TOP_K_DEFAULT = 3


class SchemaPruner:
    """
    Prunes a pipe-delimited schema string to the tables/collections most
    relevant to a given question or SQL query.

    Call prune_sql2nosql() for SQL-to-NoSQL (deterministic FROM/JOIN parse).
    Call prune_text()      for Text-to-SQL and Text-to-NoSQL (embedding sim).
    """

    def __init__(self, index_dir=RETRIEVAL_INDEX_DIR, fk_neighbors=None):
        """
        fk_neighbors : {db_id: {table_name: [connected_table_names]}}
                       from loader.load_spider_fk_neighbors_map().
                       Only used for Spider text tasks; pass None for DocSpider.
        """
        self._fk_neighbors = fk_neighbors or {}
        self._model = None  # BGE model — loaded lazily on first prune_text() call

        # Per-db lookup built at init:  {db_id: [(name, embedding_vector), ...]}
        self._spider_index    = {}
        self._docspider_index = {}

        self._load_index(index_dir)

    # ------------------------------------------------------------------
    # Index loading
    # ------------------------------------------------------------------

    def _load_index(self, index_dir):
        for dataset, attr in [("spider", "_spider_index"), ("docspider", "_docspider_index")]:
            emb_path  = os.path.join(index_dir, f"schema_{dataset}_embeddings.npy")
            meta_path = os.path.join(index_dir, f"schema_{dataset}_metadata.json")

            if not os.path.exists(emb_path) or not os.path.exists(meta_path):
                raise FileNotFoundError(
                    f"Schema pruning index missing: {emb_path}\n"
                    "Build it with:  python scripts/build_retrieval_index.py --task schema"
                )

            embeddings = np.load(emb_path)  # (N, 384) float32, L2-normalised
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            index = {}
            for i, entry in enumerate(metadata):
                db_id = entry["db_id"]
                name  = entry["name"]
                index.setdefault(db_id, []).append((name, embeddings[i]))
            setattr(self, attr, index)

    def _ensure_model(self):
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed.\n"
                "Run:  pip install sentence-transformers>=2.7.0"
            )
        print(f"[SchemaPruner] Loading {BGE_MODEL_ID}...")
        self._model = SentenceTransformer(BGE_MODEL_ID)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def prune_sql2nosql(self, schema_str: str, sql: str) -> str:
        """
        SQL-to-NoSQL: extract FROM/JOIN table names from the input SQL and
        keep only those collections.  Exact string match — no ML required.
        Falls back to the full schema if nothing matches.
        """
        if not schema_str or not sql:
            return schema_str

        referenced = _extract_sql_tables(sql)
        if not referenced:
            return schema_str

        parts      = _parse_schema(schema_str)
        lower_ref  = {t.lower() for t in referenced}
        kept       = [name for name in parts if name.lower() in lower_ref]

        return _reconstruct(kept, parts) if kept else schema_str

    def prune_text(self, schema_str: str, question: str, db_id: str,
                   dataset: str = "spider", top_k: int = _TOP_K_DEFAULT) -> str:
        """
        Text-to-SQL / Text-to-NoSQL: embed the question, score every
        table/collection for this db_id by cosine similarity, keep top_k,
        then expand with FK-connected neighbors (Spider only).
        Falls back to the full schema if db_id is unknown or nothing scores.

        dataset : "spider" for Text-to-SQL, "docspider" for Text-to-NoSQL
        """
        if not schema_str or not question:
            return schema_str

        index     = self._spider_index if dataset == "spider" else self._docspider_index
        db_tables = index.get(db_id)
        if not db_tables:
            return schema_str

        self._ensure_model()
        q_emb  = self._model.encode(question, normalize_embeddings=True, show_progress_bar=False)
        scores = sorted(
            ((name, float(q_emb @ emb)) for name, emb in db_tables),
            key=lambda x: x[1], reverse=True
        )

        kept = {name for name, _ in scores[:top_k]}

        # Expand with FK-connected neighbors so join paths are never broken
        if dataset == "spider" and db_id in self._fk_neighbors:
            neighbors = self._fk_neighbors[db_id]
            for name in list(kept):
                kept.update(neighbors.get(name, []))

        # Reconstruct in the original schema order
        parts   = _parse_schema(schema_str)
        ordered = [name for name in parts if name in kept]
        return _reconstruct(ordered, parts) if ordered else schema_str


# ------------------------------------------------------------------
# Module-level helpers (stateless)
# ------------------------------------------------------------------

def _extract_sql_tables(sql: str) -> set:
    """Return table names referenced in FROM / JOIN clauses (strips AS aliases)."""
    return set(re.findall(r'\b(?:FROM|JOIN)\s+(\w+)', sql, re.IGNORECASE))


def _parse_schema(schema_str: str) -> dict:
    """
    Parse 'A(c1, c2) | B(c3->T.c4)' into an ordered dict {name: full_part}.
    Preserves the original table order for deterministic reconstruction.
    """
    parts = {}
    for part in schema_str.split(' | '):
        part = part.strip()
        m = re.match(r'^(\w+)\(', part)
        if m:
            parts[m.group(1)] = part
    return parts


def _reconstruct(kept_names: list, parts: dict) -> str:
    """Rebuild the pipe-delimited schema from an ordered list of kept names."""
    return ' | '.join(parts[n] for n in kept_names if n in parts)
