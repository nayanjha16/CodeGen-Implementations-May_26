"""Execution harness for MongoDB MQL — the correctness signal for the NoSQL tasks.

Gold MQL is MongoDB *shell* syntax (``db.coll.find(...).sort(...)``), so we
execute it with ``mongosh`` and compare result sets, rather than translating it
into pymongo (a parser project whose bugs would corrupt the signal — SPEC §4).

Result-equality semantics match DocSpider's own scorer
(``docspider/pipelines/bp_step3_compare_results.py``): each row is reduced to the
SET of its values (field names + intra-row duplicates ignored), ``_id`` dropped,
row counts must match. Order-sensitivity is corrected relative to their scorer —
see ``implies_order`` and SPEC §4.3.

Safety: a normal local connection, no guard. A garbled query errors → treated as
an empty result (the desired "wrong" signal). A per-query timeout protects
pipeline liveness, not data (SPEC §4.4).
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass

from . import config

log = logging.getLogger(__name__)

MONGOSH = "mongosh"
_OK = "__OK__"
_ERR = "__ERR__"

# JS wrapper: the query is injected directly as code (mongosh's fluent cursor
# API — .sort()/.limit() — and async rewriting only apply to real code, not to
# eval'd strings). Passed as the --eval argument (subprocess argv, so no shell
# escaping and quotes in the query are safe). A runtime error is caught and
# printed as an __ERR__ line; a *syntax* error breaks the script's parse (no
# marker printed) and is handled by the no-marker fallback -> ok=False, which is
# the correct outcome for a broken query anyway. Cursor/array/scalar are
# normalized to an array; marker + EJSON printed on one line.
_WRAPPER = """
try {{
  const __r = ( {query} );
  let __out;
  if (__r && typeof __r.toArray === 'function') {{ __out = __r.toArray(); }}
  else if (Array.isArray(__r)) {{ __out = __r; }}
  else {{ __out = [__r]; }}
  print("{ok}" + EJSON.stringify(__out));
}} catch (e) {{
  print("{err}" + (e && e.message ? e.message : String(e)));
}}
"""


@dataclass
class ExecResult:
    ok: bool
    rows: list | None  # list of documents/scalars on success; None on failure
    error: str | None = None


# --- EJSON normalization ---------------------------------------------------
def _normalize(value):
    """Recursively convert EJSON wrappers to plain Python and drop ``_id``."""
    if isinstance(value, dict):
        # EJSON extended-type wrappers (single $-prefixed key).
        if len(value) == 1:
            (k, v), = value.items()
            if k in ("$numberInt", "$numberLong"):
                return int(v)
            if k in ("$numberDouble", "$numberDecimal"):
                try:
                    return float(v)
                except (TypeError, ValueError):
                    return str(v)
            if k == "$oid":
                return str(v)
            if k == "$date":
                return str(v)
            if k.startswith("$"):
                return _normalize(v)
        return {k: _normalize(v) for k, v in value.items() if k != "_id"}
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    return value


def _hashable(v):
    """Make a value hashable for set membership; stringify containers."""
    if isinstance(v, (list, dict)):
        return json.dumps(v, sort_keys=True, default=str)
    return v


def _row_value_set(row) -> frozenset:
    """Reduce one result row to the set of its values (DocSpider semantics)."""
    if isinstance(row, dict):
        vals = [v for k, v in row.items() if k != "_id"]
    else:
        vals = [row]
    return frozenset(_hashable(_normalize(v)) for v in vals)


# --- Execution -------------------------------------------------------------
def run_mql(db_id: str, mql: str, timeout_s: float | None = None) -> ExecResult:
    """Execute one MQL string against Mongo database ``db_id`` via mongosh."""
    if timeout_s is None:
        timeout_s = config.CONFIG.mongo.eval_timeout_s
    if not mql or not mql.strip():
        return ExecResult(ok=False, rows=None, error="empty query")

    script = _WRAPPER.format(query=mql.strip(), ok=_OK, err=_ERR)
    # Connect via the configured host/port (localhost by default → identical to
    # the old ``mongosh <db_id>`` on the Mac). A full connection string lets a
    # deployment target a separate Mongo service without changing query semantics.
    target = f"{config.CONFIG.mongo.uri}/{db_id}"
    try:
        proc = subprocess.run(
            [MONGOSH, target, "--quiet", "--eval", script],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return ExecResult(ok=False, rows=None, error="timeout")
    except FileNotFoundError:
        raise RuntimeError("mongosh not found on PATH")

    # Scan lines for the marker; take the payload on that single line only
    # (avoids "extra data" from any trailing shell output).
    ok_payload = None
    err_payload = None
    for line in (proc.stdout or "").splitlines():
        if _OK in line:
            ok_payload = line[line.index(_OK) + len(_OK):].strip()
        elif _ERR in line:
            err_payload = line[line.index(_ERR) + len(_ERR):].strip()

    if ok_payload is not None:
        try:
            parsed = json.loads(ok_payload)
        except json.JSONDecodeError as e:
            return ExecResult(ok=False, rows=None, error=f"parse: {e}")
        rows = parsed if isinstance(parsed, list) else [parsed]
        return ExecResult(ok=True, rows=rows, error=None)
    if err_payload is not None:
        return ExecResult(ok=False, rows=None, error=err_payload)
    return ExecResult(ok=False, rows=None, error=(proc.stderr or "no output").strip()[:200])


# --- Comparison ------------------------------------------------------------
def implies_order(gold_sql: str | None = None, gold_mql: str | None = None) -> bool:
    """Whether row order matters. Corrected vs DocSpider's scorer (SPEC §4.3):
    derive from the gold SQL's ORDER BY or the gold MQL's .sort(), not from the
    string 'order by' in the MQL (which is never present)."""
    if gold_sql and "order by" in gold_sql.lower():
        return True
    if gold_mql and ".sort(" in gold_mql.lower():
        return True
    return False


def results_equal(gold: ExecResult, pred: ExecResult, order_sensitive: bool) -> bool:
    """Compare two execution results by DocSpider's value-set-per-row semantics.
    A failed result is treated as an empty result set."""
    gold_rows = gold.rows if gold.ok and gold.rows is not None else []
    pred_rows = pred.rows if pred.ok and pred.rows is not None else []

    gvs = [_row_value_set(r) for r in gold_rows]
    pvs = [_row_value_set(r) for r in pred_rows]

    if len(gvs) != len(pvs):
        return False
    if not gvs:  # both empty
        return True

    if order_sensitive:
        return all(g == p for g, p in zip(gvs, pvs))
    # order-insensitive: every expected row-set must appear among achieved
    # (mirrors their non-removing search; row counts already equal).
    for g in gvs:
        if not any(g == p for p in pvs):
            return False
    return True


def is_correct(db_id: str, gold_mql: str, pred_mql: str, order_sensitive: bool) -> bool:
    """Execute gold and predicted MQL, return whether result sets match.

    Note: runs the gold query each call. Callers mining many predictions for one
    gold should cache the gold ExecResult and use ``results_equal`` directly.
    """
    gold = run_mql(db_id, gold_mql)
    pred = run_mql(db_id, pred_mql)
    return results_equal(gold, pred, order_sensitive)
