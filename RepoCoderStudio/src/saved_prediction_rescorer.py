"""CPU-only rescoring of already-generated evaluation predictions.

This module exists so an interrupted Colab session does not force another
expensive generation run.  It reads the immutable raw completions saved by
``Evaluator``, applies the current shared extraction contract, recomputes the
metrics, and writes new ``*_rescored_*`` artifacts.  Original evaluation
files are never overwritten.

This is rescoring, not answer repair: no token or algorithm is invented.
Only response headers/fences, exact repeated NL clauses, incomplete Python
tails, and content after a complete Java compilation unit may be excluded.
The raw completion remains beside the scored completion in every output row.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import pandas as pd

from src.config import CONFIG, AppConfig
from src.failure_analyzer import FailureAnalyzer
from src.metric_engine import MetricEngine
from src.prediction_inspector import PredictionInspector


_RETRIEVAL_FIELDS = (
    "rag_used",
    "retrieval_decision",
    "retrieval_top_score",
    "retrieval_score_margin",
    "retrieval_candidate_count",
    "retrieval_context_chars",
    "retrieval_context_sha256",
    "retrieval_sources",
    "retrieval_top_k",
)


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"Saved prediction log not found: {path}")
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    if not rows:
        raise ValueError(f"Saved prediction log is empty: {path}")
    return rows


def _write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _primary_metric(row: Dict[str, Any]) -> float | None:
    task_id = row.get("task_id")
    if task_id in {"T1", "T2", "T3", "T4"}:
        value = row.get("primary_success")
    else:
        value = row.get("rouge_l")
    if value is None:
        return None
    return float(value)


def _headline(summary: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for record in summary.to_dict(orient="records"):
        task_id = str(record.get("task_id", ""))
        metric = "primary_success" if task_id in {"T1", "T2", "T3", "T4"} else "rouge_l"
        rows.append(
            {
                "task_id": task_id,
                "model_type": record.get("model_type"),
                "examples": int(record.get("num_examples", 0)),
                "primary_metric": metric,
                "score": record.get(metric),
                "codebleu": record.get("codebleu"),
                "semantic_similarity": record.get("semantic_similarity"),
            }
        )
    return pd.DataFrame(rows)


class SavedPredictionRescorer:
    """Rescore immutable raw logs without loading a language model."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.root = Path(config.storage.drive_project_root)
        self.evaluation_dir = self.root / config.storage.evaluation_dir
        self.metric_engine = MetricEngine(config)
        self.failure_analyzer = FailureAnalyzer()
        self.inspector = PredictionInspector()

    def rescore_one(
        self,
        model_type: str,
        *,
        source_tag: str = "",
        output_tag: str = "rescored",
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], pd.DataFrame]:
        source_suffix = f"_{source_tag}" if source_tag else ""
        output_suffix = f"_{output_tag}" if output_tag else "_rescored"
        source = self.evaluation_dir / f"{model_type}{source_suffix}_prediction_logs.jsonl"
        saved_logs = _read_jsonl(source)

        prediction_logs: List[Dict[str, Any]] = []
        metric_rows: List[Dict[str, Any]] = []
        for index, saved in enumerate(saved_logs, start=1):
            required = ("task_id", "corpus_id", "source_modality", "target_modality", "output_text")
            missing = [key for key in required if key not in saved]
            if missing:
                raise ValueError(f"Row {index} in {source} is missing: {missing}")
            raw = saved.get("raw_prediction", "")
            metrics = self.metric_engine.evaluate_prediction(saved, raw)
            metadata = {
                key: saved.get(key)
                for key in _RETRIEVAL_FIELDS
                if key in saved
            }
            metric = {**metrics, "model_type": model_type, **metadata}
            log = {
                **saved,
                **metric,
                "reference": saved.get("reference", saved["output_text"]),
                "raw_prediction": raw,
                "scored_prediction": metrics.get("scored_prediction", raw),
                "rescored_from": source.name,
                "rescore_contract": "shared_conservative_extraction_v1",
            }
            metric_rows.append(metric)
            prediction_logs.append(log)

        analyzed = self.failure_analyzer.analyze(metric_rows)
        for index, category in enumerate(analyzed.get("failure_category", [])):
            metric_rows[index]["failure_category"] = category
            prediction_logs[index]["failure_category"] = category

        summary = self.inspector.aggregate_metrics(metric_rows)
        stem = f"{model_type}{output_suffix}"
        _write_jsonl(self.evaluation_dir / f"{stem}_prediction_logs.jsonl", prediction_logs)
        _write_jsonl(self.evaluation_dir / f"{stem}_metric_rows.jsonl", metric_rows)
        summary.to_csv(self.evaluation_dir / f"{stem}_summary.csv", index=False)
        self.failure_analyzer.summary(metric_rows).to_csv(
            self.evaluation_dir / f"{stem}_failure_summary.csv", index=False
        )
        return prediction_logs, metric_rows, summary

    def rescore_baseline_and_finetuned(self) -> Dict[str, Any]:
        """Rescore both arms and write a mentor-readable paired headline."""

        baseline_logs, baseline_metrics, baseline_summary = self.rescore_one("baseline")
        finetuned_logs, finetuned_metrics, finetuned_summary = self.rescore_one("finetuned")

        base = _headline(baseline_summary).rename(columns={"score": "baseline"})
        fine = _headline(finetuned_summary).rename(columns={"score": "finetuned"})
        keep = ["task_id", "finetuned", "codebleu", "semantic_similarity"]
        comparison = base.merge(
            fine[keep],
            on="task_id",
            how="inner",
            suffixes=("_baseline", "_finetuned"),
        )
        comparison["delta"] = comparison["finetuned"] - comparison["baseline"]
        comparison.to_csv(
            self.evaluation_dir / "baseline_vs_finetuned_rescored_comparison.csv",
            index=False,
        )

        return {
            "baseline_prediction_logs": baseline_logs,
            "baseline_metric_rows": baseline_metrics,
            "baseline_summary": baseline_summary,
            "finetuned_prediction_logs": finetuned_logs,
            "finetuned_metric_rows": finetuned_metrics,
            "finetuned_summary": finetuned_summary,
            "comparison": comparison,
        }

