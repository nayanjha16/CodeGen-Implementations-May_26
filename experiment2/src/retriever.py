"""
RAG retriever for few-shot prompt injection at inference time.

text2sql  : hybrid search — Dense (BGE-small) + BM25 via Reciprocal Rank Fusion
text2nosql: hybrid search — Dense (BGE-small) + BM25 via Reciprocal Rank Fusion
sql2nosql : dense-only    — BM25 unreliable on raw SQL (universal keywords dominate)

Index is built once by scripts/build_retrieval_index.py.
Only training data is indexed — test data is never embedded.
"""

import json
import os
import sys
import numpy as np

RETRIEVAL_INDEX_DIR = "retrieval_index"
BGE_MODEL_ID = "BAAI/bge-small-en-v1.5"

# RRF weights: 70% dense, 30% BM25; constant=60 dampens rank-1 vs rank-2 gap
_RRF_DENSE_W = 0.7
_RRF_BM25_W  = 0.3
_RRF_K       = 60


class Retriever:
    """
    Loads the pre-built embedding index for one task and handles retrieval.

    Usage:
        r = Retriever(task="text2sql")
        examples = r.retrieve_text2sql(question, db_id, table_names, k=1)

        r = Retriever(task="text2nosql")
        examples = r.retrieve_text2nosql(question, db_id, collection_names, k=1)

        r = Retriever(task="sql2nosql")
        examples = r.retrieve_sql2nosql(sql, k=1)
    """

    def __init__(self, task: str):
        if task not in ("text2sql", "sql2nosql", "text2nosql"):
            raise ValueError(f"task must be 'text2sql', 'sql2nosql', or 'text2nosql', got '{task}'")
        self.task = task

        # Load embedding model
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            print("sentence-transformers not installed. Run: pip install sentence-transformers>=2.7.0")
            sys.exit(1)

        print(f"[Retriever] Loading {BGE_MODEL_ID}...")
        self._model = SentenceTransformer(BGE_MODEL_ID)

        # Load pre-built index
        emb_path  = os.path.join(RETRIEVAL_INDEX_DIR, f"{task}_embeddings.npy")
        meta_path = os.path.join(RETRIEVAL_INDEX_DIR, f"{task}_metadata.json")

        if not os.path.exists(emb_path) or not os.path.exists(meta_path):
            raise FileNotFoundError(
                f"Retrieval index missing at '{RETRIEVAL_INDEX_DIR}/'.\n"
                "Build it first with:\n"
                f"  python scripts/build_retrieval_index.py --task {task}"
            )

        self._embeddings = np.load(emb_path)  # (N, 384) float32, already L2-normalised
        with open(meta_path, "r", encoding="utf-8") as f:
            self._metadata = json.load(f)

        # Build BM25 corpus for natural language tasks
        if task in ("text2sql", "text2nosql"):
            try:
                from rank_bm25 import BM25Okapi
            except ImportError:
                print("rank-bm25 not installed. Run: pip install rank-bm25>=0.2.2")
                sys.exit(1)
                
            # Safely extract context keys regardless of original column name schemas
            corpus_texts = []
            for m in self._metadata:
                contexts = m.get('table_names', m.get('collection_names', []))
                context_str = ", ".join(contexts) if isinstance(contexts, list) else str(contexts)
                corpus_texts.append(f"{m.get('question', '')} | contexts: {context_str}")
                
            self._bm25 = BM25Okapi([t.lower().split() for t in corpus_texts])

        print(f"[Retriever] {task} index: {len(self._metadata)} training examples loaded")

    def _encode(self, text: str) -> np.ndarray:
        return self._model.encode(text, normalize_embeddings=True, show_progress_bar=False)

    def retrieve_text2sql(
        self,
        question: str,
        db_id: str,
        table_names: list,
        k: int = 1,
    ) -> list:
        """
        Hybrid RRF retrieval (Dense + BM25) for SQL paths.
        """
        query_text = f"{question} | contexts: {', '.join(table_names)}"
        return self._hybrid_rrf_search(query_text, question, db_id, k)

    def retrieve_text2nosql(
        self,
        question: str,
        db_id: str,
        collection_names: list,
        k: int = 1,
    ) -> list:
        """
        Hybrid RRF retrieval (Dense + BM25) for Document NoSQL paths.
        """
        query_text = f"{question} | contexts: {', '.join(collection_names)}"
        return self._hybrid_rrf_search(query_text, question, db_id, k)

    def retrieve_sql2nosql(self, sql: str, k: int = 1) -> list:
        """
        Dense-only retrieval on raw structural SQL text blocks.
        """
        q_emb  = self._encode(sql)
        scores = self._embeddings @ q_emb  # (N,)
        sorted_idx = np.argsort(-scores)

        sql_stripped = sql.strip()
        results = []
        for idx in sorted_idx:
            m = self._metadata[int(idx)]
            # Check against potential query mapping fields safely
            gold_sql = m.get("spider_gold_sql", m.get("query", "")).strip()
            if gold_sql == sql_stripped:
                continue  # skip exact duplicate to maintain inference integrity
            results.append(m)
            if len(results) >= k:
                break

        return results

    def _hybrid_rrf_search(self, query_text: str, question: str, db_id: str, k: int) -> list:
        """Shared core engine routing for reciprocal rank fusion analytics."""
        # Dense ranking paths
        q_emb = self._encode(query_text)
        dense_scores = self._embeddings @ q_emb
        dense_order  = np.argsort(-dense_scores)

        # Tokenized lookup matching
        bm25_scores = np.array(self._bm25.get_scores(query_text.lower().split()))
        bm25_order  = np.argsort(-bm25_scores)

        # Construct inverted indexing arrays
        dense_rank = {int(idx): r for r, idx in enumerate(dense_order)}
        bm25_rank  = {int(idx): r for r, idx in enumerate(bm25_order)}

        # Run Reciprocal Rank Fusion calculations
        n = len(self._metadata)
        rrf = np.array([
            _RRF_DENSE_W / (_RRF_K + dense_rank[i]) +
            _RRF_BM25_W  / (_RRF_K + bm25_rank[i])
            for i in range(n)
        ])
        sorted_idx = np.argsort(-rrf)

        q_lower = question.strip().lower()
        same_db, other_db = [], []

        for idx in sorted_idx:
            m = self._metadata[int(idx)]
            if m.get("question", "").strip().lower() == q_lower:
                continue  # Avoid self-retrieval traps
                
            if m.get("db_id") == db_id:
                same_db.append(m)
            else:
                other_db.append(m)
                
            if len(same_db) >= k and len(other_db) >= k:
                break

        # Maximize context match priority (Same-DB > Cross-DB)
        results = same_db[:k]
        if len(results) < k:
            results += other_db[: k - len(results)]

        return results