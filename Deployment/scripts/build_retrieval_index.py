"""Build the per-task RAG retrieval index from the TRAIN split only (plan §7).

For each task we embed the retrieval key (the NL question, or the source SQL for
sql2nosql) with ``BAAI/bge-small-en-v1.5`` and persist ``<task>_embeddings.npy``
+ ``<task>_metadata.json`` under ``retrieval_index/``.

**Train-only:** the index is built from the train *partition* (after the
valid carve), never dev — retrieving a dev example as a reference would leak
(plan §7). Self-exclusion at query time (``retriever.py``) then prevents an
example retrieving its own twin during train-split failure mining.

Run:  python scripts/build_retrieval_index.py [--limit N] [--sanity] [--task T]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import config, loader, splits  # noqa: E402
from src.logger import setup_logging  # noqa: E402
from src.prompt_builder import input_value  # noqa: E402
from src.retriever import embed_texts  # noqa: E402

log = logging.getLogger(__name__)


def build_task_index(task: str, limit: int | None = None) -> int:
    """Build and persist the index for one task; returns the number of rows."""
    all_train = loader.load_task(task, "train")
    # Carve valid so the index is the train partition only (persisted split).
    name = "spider" if task == "text2sql" else task
    train, _valid = splits.carve_valid(all_train, name)
    if limit is not None:
        train = train[:limit]

    texts = [input_value(e) for e in train]
    meta = [
        {"uid": e.uid, "db_id": e.db_id, "input_text": input_value(e), "gold": e.gold}
        for e in train
    ]
    log.info("%s: embedding %d train examples", task, len(texts))
    emb = embed_texts(texts) if texts else np.zeros((0, 384), dtype=np.float32)

    config.ensure_dirs()
    np.save(config.RETRIEVAL_INDEX_DIR / f"{task}_embeddings.npy", emb)
    (config.RETRIEVAL_INDEX_DIR / f"{task}_metadata.json").write_text(
        json.dumps(meta), encoding="utf-8"
    )
    log.info("%s: wrote index (%d rows, dim=%d)", task, emb.shape[0], emb.shape[1] if emb.ndim == 2 else 0)
    return emb.shape[0]


def main() -> None:
    ap = argparse.ArgumentParser(description="Build RAG retrieval indexes (train only).")
    ap.add_argument("--task", choices=config.TASKS, help="build only this task")
    ap.add_argument("--limit", type=int, default=None, help="cap examples per task")
    ap.add_argument("--sanity", action="store_true", help="tiny build (limit=32)")
    args = ap.parse_args()

    setup_logging("build_retrieval_index")
    limit = 32 if args.sanity else args.limit
    tasks = [args.task] if args.task else list(config.TASKS)

    total = 0
    for task in tasks:
        total += build_task_index(task, limit=limit)
    log.info("done: %d total rows across %d task(s)", total, len(tasks))
    print(f"built retrieval index: {total} rows across {len(tasks)} task(s)")


if __name__ == "__main__":
    main()
