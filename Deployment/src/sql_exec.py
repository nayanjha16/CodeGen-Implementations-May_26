"""Execution harness for Spider SQL — the correctness signal for text2sql.

The mirror of ``mongo_exec`` for the relational side: execute gold and predicted
SQL against the Spider SQLite database for a ``db_id`` and compare result sets.
It reuses the **same value-set-per-row semantics** (SPEC §4.3) so SQL and NoSQL
correctness are scored consistently — each row reduced to the set of its values,
row counts must match first, order-insensitive unless the gold query has
``ORDER BY``.

Why a fresh SQLite scorer instead of Spider's ``evaluation.py``: the build-fresh
constraint forbids copying that code, and it carries the known ``process_sql.py``
path problem (STATUS gotchas). Executing against SQLite directly measures the
execution accuracy plan §12 itself calls "the more honest number", with no
subprocess/path fragility. A per-query timeout (via ``connection.interrupt``)
protects pipeline liveness, matching the mongo harness.
"""

from __future__ import annotations

import logging
import sqlite3
import threading
from dataclasses import dataclass

from . import config
from .mongo_exec import _hashable, _normalize  # shared scalar normalization

log = logging.getLogger(__name__)


@dataclass
class ExecResult:
    ok: bool
    rows: list | None  # list of row-tuples on success; None on failure
    error: str | None = None


def _db_path(db_id: str):
    return config.SPIDER_DB_DIR / db_id / f"{db_id}.sqlite"


def run_sql(db_id: str, sql: str, timeout_s: float | None = None) -> ExecResult:
    """Execute one SQL string against the Spider SQLite DB for ``db_id``."""
    if timeout_s is None:
        timeout_s = config.CONFIG.mongo.eval_timeout_s  # reuse the liveness timeout knob
    if not sql or not sql.strip():
        return ExecResult(ok=False, rows=None, error="empty query")

    path = _db_path(db_id)
    if not path.exists():
        return ExecResult(ok=False, rows=None, error=f"no sqlite db for {db_id}")

    con = sqlite3.connect(str(path))
    con.text_factory = lambda b: b.decode("utf-8", "replace")
    timer = threading.Timer(timeout_s, con.interrupt)
    try:
        timer.start()
        cur = con.execute(sql)
        rows = cur.fetchall()
        return ExecResult(ok=True, rows=[list(r) for r in rows], error=None)
    except sqlite3.OperationalError as e:
        msg = "timeout" if "interrupted" in str(e).lower() else str(e)
        return ExecResult(ok=False, rows=None, error=msg[:200])
    except sqlite3.Error as e:
        return ExecResult(ok=False, rows=None, error=str(e)[:200])
    finally:
        timer.cancel()
        con.close()


def _row_value_set(row) -> frozenset:
    """Reduce one SQL row to the set of its values (value-set-per-row, SPEC §4.3)."""
    vals = row if isinstance(row, (list, tuple)) else [row]
    return frozenset(_hashable(_normalize(v)) for v in vals)


def implies_order(gold_sql: str) -> bool:
    """Row order matters iff the gold SQL has an ORDER BY (SPEC §4.3)."""
    return bool(gold_sql) and "order by" in gold_sql.lower()


def results_equal(gold: ExecResult, pred: ExecResult, order_sensitive: bool) -> bool:
    """Compare two SQL results by value-set-per-row; failure ⇒ empty result."""
    gold_rows = gold.rows if gold.ok and gold.rows is not None else []
    pred_rows = pred.rows if pred.ok and pred.rows is not None else []

    gvs = [_row_value_set(r) for r in gold_rows]
    pvs = [_row_value_set(r) for r in pred_rows]

    if len(gvs) != len(pvs):
        return False
    if not gvs:
        return True
    if order_sensitive:
        return all(g == p for g, p in zip(gvs, pvs))
    for g in gvs:
        if not any(g == p for p in pvs):
            return False
    return True


def is_correct(db_id: str, gold_sql: str, pred_sql: str) -> bool:
    """Execute gold and predicted SQL, compare result sets (order from gold)."""
    gold = run_sql(db_id, gold_sql)
    pred = run_sql(db_id, pred_sql)
    return results_equal(gold, pred, implies_order(gold_sql))
