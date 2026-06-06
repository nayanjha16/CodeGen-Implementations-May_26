"""MLflow experiment tracking for CodeGen evaluation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import mlflow


def _normalize_tracking_uri(tracking_uri: str) -> str:
    """Ensure local paths use file:// scheme for cross-platform MLflow support."""
    if tracking_uri in ("", "mlruns"):
        return "mlruns"
    path = Path(tracking_uri)
    if path.exists() or not tracking_uri.startswith(("http://", "https://", "file://", "sqlite://")):
        return path.as_uri()
    return tracking_uri


class MLflowTracker:
    """Track evaluation runs with MLflow."""

    def __init__(
        self,
        experiment_name: str = "codegen-text2sql",
        tracking_uri: str = "mlruns",
    ):
        mlflow.set_tracking_uri(_normalize_tracking_uri(tracking_uri))
        mlflow.set_experiment(experiment_name)
        self.experiment_name = experiment_name
        self._active_run = None

    def start_run(
        self,
        run_name: str | None = None,
        tags: dict[str, str] | None = None,
    ):
        """Start an MLflow run."""
        self._active_run = mlflow.start_run(run_name=run_name, tags=tags)
        return self._active_run

    def log_params(self, params: dict[str, Any]) -> None:
        """Log run parameters."""
        for key, value in params.items():
            mlflow.log_param(key, value)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        """Log evaluation metrics."""
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                mlflow.log_metric(key, float(value))

    def log_evaluation(
        self,
        model_name: str,
        dataset: str,
        prompt_template: str,
        metrics: dict[str, Any],
        extra_params: dict[str, Any] | None = None,
        run_name: str | None = None,
    ) -> str:
        """Log a complete evaluation run."""
        with self.start_run(run_name=run_name or f"{dataset}-{model_name}"):
            self.log_params(
                {
                    "model_name": model_name,
                    "dataset": dataset,
                    "prompt_template": prompt_template,
                    **(extra_params or {}),
                }
            )
            metric_keys = [
                "bleu",
                "bertscore",
                "codebleu",
                "exact_match",
                "execution_accuracy",
                "rouge_l",
                "syntax_validity",
                "ngram_match",
                "syntax_match",
                "semantic_match",
            ]
            logged = {k: metrics[k] for k in metric_keys if k in metrics}
            self.log_metrics(logged)
            return mlflow.active_run().info.run_id

    def end_run(self) -> None:
        """End active MLflow run."""
        if self._active_run:
            mlflow.end_run()
            self._active_run = None
