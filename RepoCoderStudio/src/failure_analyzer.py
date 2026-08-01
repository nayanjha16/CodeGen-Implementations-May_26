"""
============================================================
RepoCoder Studio
failure_analyzer.py  —  v2.4
============================================================

Failure categorization for per-task evaluation.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


def _categorize(row: Dict[str, Any]) -> str:
    if row.get("prediction_empty"):
        return "empty_generation"
    raw = (row.get("raw_prediction") or "")
    if "### Instruction" in raw or "### Task Contract" in raw:
        return "prompt_echo"
    target = row.get("target_modality")
    if target == "Python":
        if row.get("python_parse_success") in (False, 0, "False", "false"):
            return "python_syntax_error"
        if float(row.get("codebleu", 0.0) or 0.0) < 0.10:
            return "low_similarity"
        return "ok"
    if target == "Java":
        if row.get("java_compile_success") in (False, 0, "False", "false"):
            return "java_compile_error"
        if float(row.get("codebleu", 0.0) or 0.0) < 0.10:
            return "low_similarity"
        return "ok"
    if target == "Natural Language":
        if float(row.get("rouge_l", 0.0) or 0.0) < 0.05 and float(row.get("sacrebleu", 0.0) or 0.0) < 1.0:
            return "nl_low_overlap"
        return "ok"
    return "unknown"


class FailureAnalyzer:
    """Annotates metric rows with failure categories."""

    def analyze(self, metric_rows: List[Dict[str, Any]]) -> pd.DataFrame:
        return pd.DataFrame([{**row, "failure_category": _categorize(row)} for row in metric_rows])

    def summary(self, metric_rows: List[Dict[str, Any]]) -> pd.DataFrame:
        df = self.analyze(metric_rows)
        if df.empty:
            return pd.DataFrame()
        return df.groupby(["task_id", "failure_category"]).size().unstack(fill_value=0).reset_index()

    def print_failure_report(self, metric_rows: List[Dict[str, Any]], model_type: str = "") -> None:
        df = self.analyze(metric_rows)
        if df.empty:
            print("No metric rows to analyze.")
            return
        label = f" [{model_type.upper()}]" if model_type else ""
        print(f"\n{'='*70}\n  FAILURE ANALYSIS{label}\n{'='*70}")
        total = len(df)
        print(f"\nOverall ({total} predictions):")
        for cat, count in df["failure_category"].value_counts().items():
            print(f"  {cat:<24}: {count:4d} ({100*count/total:.1f}%)")
        print("\nPer task:")
        for task_id, group in df.groupby("task_id"):
            cats = group["failure_category"].value_counts().to_dict()
            print(f"  {task_id}: " + "  ".join(f"{k}={v}" for k, v in cats.items()))
        print(f"\n{'='*70}\n")
