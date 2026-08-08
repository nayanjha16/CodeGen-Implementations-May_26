"""Execution-based failure mining (plan §8, SPEC §10 step 11).

Reads the Pass-1 **train-split** predictions written by
``run_multi_task_inference.py --split train`` and keeps only the ones the model
got **wrong by execution** — never by string match (plan §2 change #2 /
SPEC-REVIEW #6). Each kept row's ``broken_draft`` is the actual Pass-1 prediction,
execution-confirmed to disagree with gold; these are the raw material the teacher
explains (step 12).

Correctness is decided by the same harnesses used everywhere: ``sql_exec`` (SQL)
and ``mongo_exec`` (MQL, order derived from the gold SQL). Because mining runs on
the train split against a train-built retrieval index, this stage is exactly where
the retriever's self-exclusion-by-uid must hold (SPEC-REVIEW #5) — otherwise a
query would have copied its own gold and never surfaced here.

Run:  python extract_failures.py [--task T] [--limit N] [--sanity]
"""

from __future__ import annotations

import argparse
import json
import logging

from src import config, mongo_exec, sql_exec
from src.logger import setup_logging

log = logging.getLogger(__name__)


def _predictions_path(task: str):
    return config.OUTPUTS_DIR / "codegen" / "pass1_train" / task / "predictions.json"


def _failures_path(task: str):
    return config.FAILURES_DIR / f"{task}_failures.json"


def _correct_path(task: str):
    return config.FAILURES_DIR / f"{task}_correct.json"


def _is_correct(rec: dict) -> bool:
    """Execution correctness for one mining record (SQL via sqlite, NoSQL via mongosh)."""
    task, db_id, gold, pred = rec["task"], rec["db_id"], rec["gold"], rec["prediction"]
    if task == "text2sql":
        return sql_exec.is_correct(db_id, gold, pred)
    order_sensitive = mongo_exec.implies_order(gold_sql=rec.get("aux_sql"), gold_mql=gold)
    return mongo_exec.is_correct(db_id, gold, pred, order_sensitive)


def mine_task(task: str, limit: int | None = None) -> dict:
    path = _predictions_path(task)
    if not path.exists():
        raise FileNotFoundError(f"no train predictions for {task!r}: {path} "
                                f"(run run_multi_task_inference.py --split train first)")
    records = json.loads(path.read_text(encoding="utf-8"))
    if limit is not None:
        records = records[:limit]

    failures = []
    correct = []  # correct drafts — the "keep" pool for Stage-B (fixes over-correction, run #1 finding)
    for rec in records:
        if _is_correct(rec):
            if (rec.get("draft") or "").strip():
                correct.append({
                    "db_id": rec["db_id"], "task": task,
                    "question": rec.get("question"), "source_sql": rec.get("source_sql"),
                    "aux_sql": rec.get("aux_sql"), "gold": rec["gold"], "draft": rec["draft"],
                })
            continue
        failures.append({
            "db_id": rec["db_id"],
            "task": task,
            "question": rec.get("question"),
            "source_sql": rec.get("source_sql"),
            "aux_sql": rec.get("aux_sql"),
            "gold": rec["gold"],
            "broken_draft": rec["prediction"],  # execution-confirmed wrong
        })

    config.ensure_dirs()
    out = _failures_path(task)
    out.write_text(json.dumps(failures, indent=1), encoding="utf-8")
    _correct_path(task).write_text(json.dumps(correct, indent=1), encoding="utf-8")
    n = len(records)
    summary = {
        "task": task, "predictions": n, "failures": len(failures), "correct": len(correct),
        "fail_rate": round(len(failures) / max(n, 1), 4), "path": str(out),
    }
    log.info("mined %s", summary)
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Execution-based failure mining.")
    ap.add_argument("--task", choices=config.TASKS, help="mine one task (default: all present)")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sanity", action="store_true")
    args = ap.parse_args()

    setup_logging("extract_failures")
    limit = 6 if args.sanity and args.limit is None else args.limit
    tasks = [args.task] if args.task else list(config.TASKS)

    summaries = []
    for task in tasks:
        if not _predictions_path(task).exists():
            log.warning("skipping %s: no train predictions on disk", task)
            continue
        summaries.append(mine_task(task, limit=limit))
    total = sum(s["failures"] for s in summaries)
    print(f"failures mined: {total} across {len(summaries)} task(s): "
          + ", ".join(f"{s['task']}={s['failures']}/{s['predictions']}" for s in summaries))


if __name__ == "__main__":
    main()
