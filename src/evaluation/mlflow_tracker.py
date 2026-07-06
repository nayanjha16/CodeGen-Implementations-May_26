"""MLflow experiment tracking for CodeGen evaluation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import mlflow


def default_tracking_uri(project_root: Path | None = None) -> str:
    """Return SQLite tracking URI (compatible with MLflow 3.x)."""
    root = project_root or Path(__file__).resolve().parents[2]
    db_path = (root / "mlflow.db").resolve().as_posix()
    return f"sqlite:///{db_path}"


def _sqlite_uri_for_path(path: Path) -> str:
    """Map a local path to a SQLite MLflow backend URI."""
    if path.suffix == ".db":
        db_path = path.resolve()
    elif path.is_dir() or path.suffix == "":
        db_path = (path / "mlflow.db").resolve()
    else:
        db_path = path.with_suffix(".db").resolve()
    return f"sqlite:///{db_path.as_posix()}"


def _normalize_tracking_uri(tracking_uri: str) -> str:
    """Normalize tracking URI for cross-platform MLflow 3.x support."""
    if tracking_uri in ("", "mlruns", "mlflow.db"):
        return default_tracking_uri()
    if tracking_uri.startswith("sqlite://"):
        return tracking_uri
    if tracking_uri.startswith(("http://", "https://")):
        return tracking_uri

    local_path = tracking_uri.removeprefix("file://")
    return _sqlite_uri_for_path(Path(local_path))


class MLflowTracker:
    """Track evaluation runs with MLflow."""

    def __init__(
        self,
        experiment_name: str = "codegen-text2sql",
        tracking_uri: str | None = None,
    ):
        uri = _normalize_tracking_uri(tracking_uri or default_tracking_uri())
        mlflow.set_tracking_uri(uri)
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
        nosql_metrics: dict[str, Any] | None = None,
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
                "execution_accuracy",
                "exact_match",
                "structural_similarity",
            ]
            logged = {k: metrics[k] for k in metric_keys if k in metrics}
            if nosql_metrics:
                nosql_keys = [
                    "execution_accuracy",
                    "exact_match",
                    "structural_similarity",
                ]
                logged.update(
                    {f"nosql_{k}": nosql_metrics[k] for k in nosql_keys if k in nosql_metrics}
                )
            self.log_metrics(logged)
            return mlflow.active_run().info.run_id

    def end_run(self) -> None:
        """End active MLflow run."""
        if self._active_run:
            mlflow.end_run()
            self._active_run = None
