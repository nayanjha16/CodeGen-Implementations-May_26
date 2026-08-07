"""
Extract Pass 1 inference failures for all three task types.
Compares predicted output against gold and writes failure records that
generate_teacher_data.py will use for teacher annotation.

Usage:
    python extract_failures.py \\
        --text2sql_pred  outputs/codegen/pass1/text2sql/predictions.json \\
        --sql2nosql_pred outputs/codegen/pass1/sql2nosql/predictions.json \\
        --text2nosql_pred outputs/codegen/pass1/text2nosql/predictions.json
"""

import argparse
import json
import os
import re

from src.config import DATA
from src.logger import pipeline_logger


# ---------------------------------------------------------------------------
# Normalization helpers — lightweight comparison, not Spider eval-level exact
# ---------------------------------------------------------------------------

def _norm_sql(sql: str) -> str:
    """Lowercase, collapse whitespace, strip trailing semicolons."""
    return re.sub(r"\s+", " ", sql.lower().strip().rstrip(";").strip())


def _norm_mql(mql: str) -> str:
    """Collapse whitespace only — MQL is case-sensitive."""
    return re.sub(r"\s+", " ", mql.strip())


def _load_preds(path: str) -> list:
    if not path or not os.path.exists(path):
        pipeline_logger.warning("extract_failures", "predictions_file_missing", stats={"path": path})
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(records: list, out_path: str, label: str):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    pipeline_logger.info("extract_failures", f"{label}_saved", stats={
        "path": out_path, "count": len(records)
    })
    print(f"[extract_failures] {label}: {len(records)} failures → {out_path}")


# ---------------------------------------------------------------------------
# Per-task extractors
# ---------------------------------------------------------------------------

def extract_text2sql(pred_path: str, out_path: str) -> int:
    preds = _load_preds(pred_path)
    failures = []
    for item in preds:
        gold      = _norm_sql(item.get("gold_sql", ""))
        predicted = _norm_sql(item.get("predicted_sql", ""))
        if not gold or not predicted:
            continue
        if gold != predicted:
            failures.append({
                "db_id":        item["db_id"],
                "question":     item.get("question", ""),
                "query":        item.get("gold_sql", ""),   # gold SQL — used as target in Pass 2
                "broken_draft": item.get("predicted_sql", ""),
            })

    pipeline_logger.info("extract_failures", "text2sql_extraction_done", stats={
        "total_predictions": len(preds),
        "failures": len(failures),
        "failure_pct": round(len(failures) / len(preds) * 100, 1) if preds else 0
    })
    _save(failures, out_path, "text2sql_failures")
    return len(failures)


def extract_docspider(pred_path: str, out_path: str, task_label: str) -> int:
    preds = _load_preds(pred_path)
    failures = []
    for item in preds:
        gold      = _norm_mql(item.get("gold_mql", ""))
        predicted = _norm_mql(item.get("predicted_mql", ""))
        if not gold or not predicted:
            continue
        if gold != predicted:
            failures.append({
                "db_id":         item["db_id"],
                "question":      item.get("question", ""),
                "query":         item.get("gold_mql", ""),      # gold MQL
                "spider_gold_sql": item.get("gold_sql", ""),    # gold SQL (for sql2nosql context)
                "broken_draft":  item.get("predicted_mql", ""),
            })

    pipeline_logger.info("extract_failures", f"{task_label}_extraction_done", stats={
        "total_predictions": len(preds),
        "failures": len(failures),
        "failure_pct": round(len(failures) / len(preds) * 100, 1) if preds else 0
    })
    _save(failures, out_path, f"{task_label}_failures")
    return len(failures)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Extract Pass 1 inference failures for teacher annotation")
    parser.add_argument("--text2sql_pred",   default=None, help="Path to text2sql predictions.json")
    parser.add_argument("--sql2nosql_pred",  default=None, help="Path to sql2nosql predictions.json")
    parser.add_argument("--text2nosql_pred", default=None, help="Path to text2nosql predictions.json")
    args = parser.parse_args()

    pipeline_logger.info("extract_failures", "start")

    total = 0
    total += extract_text2sql(
        pred_path=args.text2sql_pred,
        out_path=DATA["spider_failures"]
    )
    total += extract_docspider(
        pred_path=args.sql2nosql_pred,
        out_path=DATA["docspider_sql2nosql_failures"],
        task_label="sql2nosql"
    )
    total += extract_docspider(
        pred_path=args.text2nosql_pred,
        out_path=DATA["docspider_text2nosql_failures"],
        task_label="text2nosql"
    )

    pipeline_logger.info("extract_failures", "complete", stats={"total_failures": total})
    print(f"\n[extract_failures] Done. Total failures across all tasks: {total}")


if __name__ == "__main__":
    main()
