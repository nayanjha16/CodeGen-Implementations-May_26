import math
import sqlite3
import time
from collections import Counter
from pathlib import Path

def _run(sql: str, db_path: Path, timeout: float = 5.0):
    con = sqlite3.connect(db_path, timeout=timeout)
    try:
        con.execute("PRAGMA busy_timeout = 5000")
        return con.execute(sql).fetchall()
    finally:
        con.close()

def _comparable(rows, benchmark: str):
    """Dataset-aware result representation for equality.

    spider -> multiset (Counter): order-insensitive, duplicate-preserving.
    bird   -> set: order-insensitive, duplicate-insensitive (BIRD official).
    """
    tuples = list(map(tuple, rows))
    if benchmark == "spider":
        return Counter(tuples)
    if benchmark == "bird":
        return set(tuples)
    raise ValueError(f"unknown benchmark: {benchmark!r} (expected 'spider' or 'bird')")

def ex_match(pred_sql: str, gold_sql: str, db_path: Path, benchmark: str = "spider") -> bool:
    """Execution Accuracy: do predicted and gold queries return matching results?"""
    try:
        pred = _run(pred_sql, db_path)
        gold = _run(gold_sql, db_path)
    except sqlite3.Error:
        return False
    return _comparable(pred, benchmark) == _comparable(gold, benchmark)

def ts_match(pred_sql: str, gold_sql: str, db_paths: list[Path], benchmark: str = "spider") -> bool:
    """Test-Suite Accuracy: EX must hold across every provided DB instance."""
    return all(ex_match(pred_sql, gold_sql, p, benchmark) for p in db_paths)

def ves_score(pred_sql: str, gold_sql: str, db_path: Path, runs: int = 3, benchmark: str = "spider") -> float:
    """Valid Efficiency Score: 0 if incorrect, else sqrt(gold_time / pred_time)."""
    if not ex_match(pred_sql, gold_sql, db_path, benchmark):
        return 0.0
    def timed(sql):
        best = float("inf")
        for _ in range(runs):
            t0 = time.perf_counter()
            _run(sql, db_path)
            best = min(best, time.perf_counter() - t0)
        return max(best, 1e-6)
    ratio = timed(gold_sql) / timed(pred_sql)
    return float(math.sqrt(ratio))
