"""
============================================================
RepoCoder Studio
prediction_inspector.py  —  v2.4
============================================================

Notebook-friendly prediction inspection tables.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


class PredictionInspector:
    _CELL_MAX = 220

    def _trunc(self, text: str, max_chars: int = _CELL_MAX) -> str:
        if not text:
            return ""
        text = str(text).replace("\n", " ↵ ")
        return text[:max_chars] + "..." if len(text) > max_chars else text

    def build_inspection_table(self, prediction_logs: List[Dict[str, Any]], max_per_task: int = 3) -> pd.DataFrame:
        rows: List[Dict[str, Any]] = []
        by_task: Dict[str, List[Dict[str, Any]]] = {}
        for log in prediction_logs:
            by_task.setdefault(log.get("task_id", "unknown"), []).append(log)
        for task_id, logs in sorted(by_task.items()):
            for log in logs[:max_per_task]:
                rows.append({
                    "task_id": task_id,
                    "model_type": log.get("model_type"),
                    "source_modality": log.get("source_modality"),
                    "target_modality": log.get("target_modality"),
                    "input": self._trunc(log.get("input_text", "")),
                    "reference": self._trunc(log.get("reference", "")),
                    "prediction": self._trunc(log.get("scored_prediction", log.get("raw_prediction", ""))),
                    "primary_success": log.get("primary_success"),
                    "codebleu": log.get("codebleu"),
                    "official_codebleu_used": log.get("official_codebleu_used"),
                    "csr_score": log.get("csr_score", log.get("csr_similarity")),
                    "rouge_l": log.get("rouge_l"),
                    "sacrebleu": log.get("sacrebleu"),
                    "failure_category": log.get("failure_category"),
                })
        return pd.DataFrame(rows)

    def print_inspection(self, prediction_logs: List[Dict[str, Any]], max_per_task: int = 2, model_type: str = "") -> None:
        df = self.build_inspection_table(prediction_logs, max_per_task=max_per_task)
        if df.empty:
            print("No predictions to inspect.")
            return
        label = f" [{model_type.upper()}]" if model_type else ""
        print(f"\n{'='*70}\n  PREDICTION INSPECTION{label}\n{'='*70}")
        for _, r in df.iterrows():
            print(f"\n[Task: {r['task_id']} | {r['source_modality']} -> {r['target_modality']}]")
            print(f"  INPUT     : {r['input']}")
            print(f"  REFERENCE : {r['reference']}")
            print(f"  PREDICTION: {r['prediction']}")
            metrics = []
            for col in ["primary_success", "codebleu", "csr_score", "rouge_l", "sacrebleu", "failure_category"]:
                val = r.get(col)
                if pd.notna(val):
                    metrics.append(f"{col}={val:.4f}" if isinstance(val, float) else f"{col}={val}")
            if metrics:
                print("  METRICS   : " + " | ".join(metrics))
        print(f"\n{'='*70}\n")

    def aggregate_metrics(self, metric_rows: List[Dict[str, Any]]) -> pd.DataFrame:
        df = pd.DataFrame(metric_rows)
        if df.empty:
            return pd.DataFrame()
        summaries: List[Dict[str, Any]] = []
        metric_cols = [
            "primary_success", "python_parse_success", "java_compile_success",
            "official_codebleu", "codebleu", "codebleu_lite", "csr_score", "csr_similarity",
            "sacrebleu", "rouge_l", "semantic_similarity", "prediction_empty",
        ]
        for task_id, group in df.groupby("task_id"):
            row: Dict[str, Any] = {
                "task_id": task_id,
                "model_type": group["model_type"].iloc[0] if "model_type" in group else "",
                "source_modality": group["source_modality"].iloc[0],
                "target_modality": group["target_modality"].iloc[0],
                "num_examples": len(group),
            }
            for col in metric_cols:
                if col in group.columns:
                    row[col] = pd.to_numeric(group[col], errors="coerce").mean()
            summaries.append(row)
        return pd.DataFrame(summaries).sort_values("task_id").reset_index(drop=True)
