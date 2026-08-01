"""
============================================================
RepoCoder Studio
repobench_eval.py — external benchmark: RepoBench-R
============================================================

Adapts RepoBench (Liu et al., ICLR 2024 — https://github.com/Leolty/repobench)
into a Precision/Recall/MRR-style retrieval evaluation using this
project's own CodeEmbedder: a real, externally-authored benchmark for
Stage 4's retrieval quality, answering the gap the project's own
self-audits flagged (Precision/Recall/MRR previously only measured
against a hand-labeled fixture this project wrote itself).

What this is, and isn't
------------------------
RepoBench's own published evaluation scores next-line *completion*
quality (Exact Match / Edit Similarity / CodeBLEU) after retrieval. This
module does NOT reproduce that harness. It uses RepoBench's `context`
(candidate cross-file snippets) + `gold_snippet_index` fields -- a real
open-source repository's actual cross-file dependency, not something
this project invented -- as (query, relevant-snippet) pairs to score
retrieval quality specifically: given the code right before a gap in a
real file, does ranking that row's own candidate snippets by our
embedder's cosine similarity put the snippet actually needed at the
top? This is an honest, scoped adaptation of real external data, not a
claim of running RepoBench's official leaderboard protocol.

Why per-row candidate ranking, not a single shared index
-----------------------------------------------------------
Each RepoBench row ships its own small candidate pool (2-7 snippets)
already narrowed to plausible cross-file dependencies for that specific
gap. Precision@5/Recall@5 (fixed k against a large shared index, as
Stage 4's own repo evaluation uses) doesn't fit a per-row pool that's
sometimes smaller than 5 -- top-1 accuracy, top-3 accuracy, and MRR are
the metrics that make sense against RepoBench's actual task shape, and
are reported here instead, alongside a random-baseline comparison since
candidate pools are small (a completely broken retriever would still
score non-trivially by chance on a 2-candidate row).

Requires the `datasets` library (already a project dependency for
XLCoST/CodeXGLUE loading, see src/dataset_loader.py) and network access
to Hugging Face Hub -- streamed (not fully downloaded) to stay
Colab-friendly; only num_samples rows are ever pulled.

Python and Java
----------------
RepoBench ships matching Python and Java datasets with an identical
schema (verified directly, not assumed from documentation) -- this
project is bilingual throughout (Stage 1-3's XLCoST corpus, Stage 4's
Java indexing via tree-sitter-java), so evaluate_repobench() takes a
`language` argument rather than hardcoding Python only.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from src.config import AppConfig, CONFIG
from src.logger import LOG
from src.storage import ProjectStorageManager
from src.statistical_evaluation import bootstrap_ci

REPOBENCH_DATASETS = {
    "python": "tianyang/repobench_python_v1.1",
    "java": "tianyang/repobench_java_v1.1",
}
REPOBENCH_SPLIT = "cross_file_first"  # the split that specifically requires cross-file retrieval
_QUERY_CHARS = 1000   # tail of cropped_code used as the retrieval query
_SNIPPET_CHARS = 800  # candidate snippet truncation, same order of magnitude as Stage 4's own embedding_text() truncation


def _cosine_rank(query_vec: np.ndarray, candidate_vecs: np.ndarray) -> List[int]:
    """Candidate indices sorted by cosine similarity to query_vec, descending.
    Vectors are assumed already L2-normalized (CodeEmbedder.encode() does this)."""
    scores = candidate_vecs @ query_vec
    return list(np.argsort(-scores))


def evaluate_repobench(
    embedder,
    num_samples: int = 100,
    split: str = REPOBENCH_SPLIT,
    language: str = "python",
    config: AppConfig = CONFIG,
) -> Dict[str, Any]:
    """Runs a retrieval-quality evaluation against a real streamed sample
    of RepoBench (language: "python" or "java"). Returns
    {"status": "skipped", "reason": ...} if the `datasets` library or
    network access isn't available -- this is an optional, best-effort
    external check, not something that should block the rest of Stage
    4/5 from running."""
    if language not in REPOBENCH_DATASETS:
        return {"status": "skipped", "reason": f"unknown language {language!r}, expected one of {list(REPOBENCH_DATASETS)}"}
    dataset_name = REPOBENCH_DATASETS[language]

    try:
        from datasets import load_dataset
    except ImportError as exc:
        LOG.warning(f"RepoBench evaluation skipped: 'datasets' library not installed ({exc})")
        return {"status": "skipped", "reason": "datasets library not installed"}

    LOG.info(f"Streaming up to {num_samples} rows from {dataset_name} ({split}) ...")
    try:
        ds = load_dataset(dataset_name, split=split, streaming=True)
    except Exception as exc:
        LOG.warning(f"RepoBench evaluation skipped: could not load dataset ({exc})")
        return {"status": "skipped", "reason": repr(exc)}

    rows = []
    try:
        for row in ds:
            if len(rows) >= num_samples:
                break
            if len(row.get("context") or []) >= 2:  # need >=2 candidates for ranking to mean anything
                rows.append(row)
    except Exception as exc:
        LOG.warning(f"RepoBench evaluation skipped: error while streaming rows ({exc})")
        return {"status": "skipped", "reason": repr(exc)}

    if not rows:
        return {"status": "skipped", "reason": "no usable rows retrieved"}

    top1_hits = 0
    top3_hits = 0
    reciprocal_ranks: List[float] = []
    top1_values: List[float] = []
    top3_values: List[float] = []
    per_row: List[Dict[str, Any]] = []
    random_top1_expected = 0.0
    candidate_counts: List[int] = []

    for row in rows:
        query_text = row["cropped_code"][-_QUERY_CHARS:]
        candidates = row["context"]
        gold_idx = row["gold_snippet_index"]
        candidate_counts.append(len(candidates))

        query_vec = embedder.encode_query(query_text)
        cand_texts = [c["snippet"][:_SNIPPET_CHARS] for c in candidates]
        cand_vecs = embedder.encode(cand_texts, is_query=False)

        ranking = _cosine_rank(query_vec, cand_vecs)
        rank_of_gold = ranking.index(gold_idx) + 1  # 1-indexed

        if rank_of_gold == 1:
            top1_hits += 1
        if rank_of_gold <= 3:
            top3_hits += 1
        reciprocal_ranks.append(1.0 / rank_of_gold)
        top1_values.append(float(rank_of_gold == 1))
        top3_values.append(float(rank_of_gold <= 3))
        random_top1_expected += 1 / len(candidates)
        per_row.append(
            {
                "rank_of_gold": rank_of_gold,
                "candidate_count": len(candidates),
                "reciprocal_rank": round(1.0 / rank_of_gold, 6),
            }
        )

    n = len(rows)
    metrics: Dict[str, Any] = {
        "status": "ok",
        "language": language,
        "dataset": dataset_name,
        "split": split,
        "rows_evaluated": n,
        "avg_candidates_per_row": round(sum(candidate_counts) / n, 2),
        "top1_accuracy": round(top1_hits / n, 4),
        "top3_accuracy": round(top3_hits / n, 4),
        "mrr": round(sum(reciprocal_ranks) / n, 4),
        "random_baseline_top1_accuracy": round(random_top1_expected / n, 4),
        "mock_embeddings": getattr(embedder, "is_mock", None),
        "confidence_intervals_95": {
            "top1_accuracy": bootstrap_ci(top1_values, seed=config.runtime.random_seed),
            "top3_accuracy": bootstrap_ci(top3_values, seed=config.runtime.random_seed),
            "mrr": bootstrap_ci(reciprocal_ranks, seed=config.runtime.random_seed),
        },
        "evidence_grade": (
            "benchmark_sample" if n >= 100 else "proof_of_concept_sample"
        ),
        "per_row": per_row,
    }

    storage = ProjectStorageManager(config)
    storage.save_json(metrics, storage.repobench_eval_report_path(language=language))
    return metrics
