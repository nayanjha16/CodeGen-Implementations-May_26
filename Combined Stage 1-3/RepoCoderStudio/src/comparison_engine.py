"""
============================================================
RepoCoder Studio
comparison_engine.py  —  v2.4
============================================================

Per-task baseline vs fine-tuned comparison.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import pandas as pd


_TASK_PRIMARY = {
    "T1": "python_parse_success",
    "T2": "java_compile_success",
    "T3": "java_compile_success",
    "T4": "python_parse_success",
    "T5": "rouge_l",
    "T6": "rouge_l",
}


class ComparisonEngine:
    """Builds per-task comparison tables and compact overview."""

    def compare(self, baseline_summary: pd.DataFrame, finetuned_summary: pd.DataFrame) -> pd.DataFrame:
        if baseline_summary is None or finetuned_summary is None or baseline_summary.empty or finetuned_summary.empty:
            return pd.DataFrame()
        base = baseline_summary.copy().add_prefix("baseline_")
        ft = finetuned_summary.copy().add_prefix("finetuned_")
        merged = base.merge(ft, left_on="baseline_task_id", right_on="finetuned_task_id", how="outer")
        merged["task_id"] = merged["baseline_task_id"].fillna(merged["finetuned_task_id"])
        for col in set(c.replace("baseline_", "") for c in base.columns) & set(c.replace("finetuned_", "") for c in ft.columns):
            if col in {"task_id", "model_type", "source_modality", "target_modality"}:
                continue
            bcol, fcol = f"baseline_{col}", f"finetuned_{col}"
            if bcol in merged and fcol in merged:
                merged[f"delta_{col}"] = pd.to_numeric(merged[fcol], errors="coerce") - pd.to_numeric(merged[bcol], errors="coerce")
        return merged.sort_values("task_id").reset_index(drop=True)

    def per_task_tables(self, comparison_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        tables: Dict[str, pd.DataFrame] = {}
        if comparison_df is None or comparison_df.empty:
            return tables
        for _, row in comparison_df.iterrows():
            task_id = row.get("task_id")
            metrics: List[Dict[str, object]] = []
            for col in comparison_df.columns:
                if not col.startswith("baseline_"):
                    continue
                metric = col.replace("baseline_", "")
                if metric in {"task_id", "model_type", "source_modality", "target_modality"}:
                    continue
                fcol, dcol = f"finetuned_{metric}", f"delta_{metric}"
                if fcol in comparison_df.columns:
                    metrics.append({
                        "metric": metric,
                        "baseline": row.get(col),
                        "fine_tuned": row.get(fcol),
                        "delta": row.get(dcol),
                        "primary": metric == _TASK_PRIMARY.get(task_id),
                    })
            tables[task_id] = pd.DataFrame(metrics)
        return tables

    def overview(self, comparison_df: pd.DataFrame) -> pd.DataFrame:
        rows: List[Dict[str, object]] = []
        if comparison_df is None or comparison_df.empty:
            return pd.DataFrame()
        for _, row in comparison_df.iterrows():
            task_id = row.get("task_id")
            metric = _TASK_PRIMARY.get(task_id)
            rows.append({
                "task_id": task_id,
                "primary_metric": metric,
                "baseline": row.get(f"baseline_{metric}"),
                "fine_tuned": row.get(f"finetuned_{metric}"),
                "delta": row.get(f"delta_{metric}"),
            })
        return pd.DataFrame(rows)

    def print_comparison(self, baseline_summary: pd.DataFrame, finetuned_summary: pd.DataFrame) -> pd.DataFrame:
        comparison = self.compare(baseline_summary, finetuned_summary)
        if comparison.empty:
            print("No comparison available.")
            return comparison
        print("\n" + "=" * 70)
        print("PER-TASK BASELINE VS FINE-TUNED COMPARISON")
        print("=" * 70)
        print("\nOverview:")
        print(self.overview(comparison).to_string(index=False))
        print("\nPer-task tables:")
        for task_id, table in self.per_task_tables(comparison).items():
            print(f"\n{task_id}")
            print(table.to_string(index=False))
        print("=" * 70 + "\n")
        return comparison
