"""
============================================================
RepoCoder Studio
evaluator.py  —  v2.4
============================================================

Evaluation orchestrator with per-task reporting.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pandas as pd

from src.config import CONFIG, AppConfig
from src.storage import ProjectStorageManager
from src.generation_engine import GenerationEngine
from src.metric_engine import MetricEngine
from src.prediction_inspector import PredictionInspector
from src.failure_analyzer import FailureAnalyzer
from src.comparison_engine import ComparisonEngine
from src.logger import LOG, SectionPrinter, SummaryPrinter


class EvaluationEngine:
    """Runs baseline/fine-tuned evaluation and comparison."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.storage = ProjectStorageManager(config)
        self.gen_engine = GenerationEngine(config)
        self.metric_engine = MetricEngine(config)
        self.inspector = PredictionInspector()
        self.failure_analyzer = FailureAnalyzer()
        self.comparison_engine = ComparisonEngine()

    def load_model(self, model_type: str):
        return self.gen_engine.load_model(model_type)

    def _select_examples(self, rows: List[Dict[str, Any]], max_examples_per_task: int) -> List[Dict[str, Any]]:
        by_task: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            by_task.setdefault(row["task_id"], []).append(row)
        selected: List[Dict[str, Any]] = []
        for task_id in sorted(by_task):
            selected.extend(by_task[task_id][:max_examples_per_task])
        return selected

    def evaluate(
        self,
        test_dataset,
        model_type: str,
        max_examples_per_task: int = 5,
        print_inspection: bool = True,
        print_failures: bool = True,
    ) -> Tuple[List[Dict], List[Dict], pd.DataFrame]:
        assert model_type in {"baseline", "finetuned"}
        SectionPrinter.header(f"{model_type.upper()} Evaluation  [v2.4]")
        model, tokenizer = self.gen_engine.load_model(model_type)
        selected = self._select_examples(list(test_dataset), max_examples_per_task)

        prediction_logs: List[Dict[str, Any]] = []
        metric_rows: List[Dict[str, Any]] = []

        for idx, row in enumerate(selected):
            LOG.info(f"[{model_type}] {idx + 1}/{len(selected)} | {row['task_id']}")
            raw = self.gen_engine.generate(
                model=model,
                tokenizer=tokenizer,
                instruction=row["instruction"],
                input_text=row["input_text"],
                task_id=row.get("task_id", ""),
            )
            metrics = self.metric_engine.evaluate_prediction(row, raw)
            metric = {**metrics, "model_type": model_type}
            log = {
                **row,
                **metric,
                "model_type": model_type,
                "raw_prediction": raw,
                "scored_prediction": metrics.get("scored_prediction", raw),
                "reference": row["output_text"],
            }
            metric_rows.append(metric)
            prediction_logs.append(log)

        failure_df = self.failure_analyzer.analyze(metric_rows)
        if not failure_df.empty:
            # Copy failure category back to logs/metrics for inspection and persistence.
            for i, cat in enumerate(failure_df["failure_category"].tolist()):
                metric_rows[i]["failure_category"] = cat
                prediction_logs[i]["failure_category"] = cat

        pred_path = f"{self.config.storage.evaluation_dir}/{model_type}_prediction_logs.jsonl"
        metric_path = f"{self.config.storage.evaluation_dir}/{model_type}_metric_rows.jsonl"
        self.storage.save_jsonl(prediction_logs, pred_path)
        self.storage.save_jsonl(metric_rows, metric_path)

        summary_df = self.inspector.aggregate_metrics(metric_rows)
        summary_path = self.config.storage.project_root() / self.config.storage.evaluation_dir / f"{model_type}_summary.csv"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_df.to_csv(summary_path, index=False)

        if print_inspection:
            self.inspector.print_inspection(prediction_logs, max_per_task=2, model_type=model_type)
        if print_failures:
            self.failure_analyzer.print_failure_report(metric_rows, model_type=model_type)

        SummaryPrinter.print_summary(
            f"{model_type.upper()} Evaluation Summary  [v2.4]",
            {
                "Evaluated Examples": len(selected),
                "Prediction Logs": pred_path,
                "Metric Rows": metric_path,
                "Summary CSV": str(summary_path),
            },
        )
        return prediction_logs, metric_rows, summary_df

    def compare(self, baseline_summary: pd.DataFrame, finetuned_summary: pd.DataFrame) -> pd.DataFrame:
        comparison = self.comparison_engine.print_comparison(baseline_summary, finetuned_summary)
        comparison_path = self.config.storage.project_root() / self.config.storage.evaluation_dir / "baseline_vs_finetuned_comparison.csv"
        comparison_path.parent.mkdir(parents=True, exist_ok=True)
        comparison.to_csv(comparison_path, index=False)
        return comparison
