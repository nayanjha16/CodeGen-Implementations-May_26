"""MLflow logging helpers for LoRA training runs."""

from __future__ import annotations

from typing import Any

from src.evaluation.mlflow_tracker import MLflowTracker


class TrainingMLflowLogger:
    """Log LoRA training hyperparameters and metrics to MLflow."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        eval_cfg = (config or {}).get("evaluation", {})
        self.tracker = MLflowTracker(
            experiment_name=str(eval_cfg.get("experiment_name", "codegen-text2sql")),
            tracking_uri=eval_cfg.get("mlflow_tracking_uri"),
        )

    def log_training_run(
        self,
        *,
        task: str,
        model_name: str,
        output_dir: str,
        train_rows: int,
        eval_rows: int,
        hyperparams: dict[str, Any],
        metrics: dict[str, float],
        run_name: str | None = None,
    ) -> str:
        """Start a run, log params/metrics, and return the MLflow run id."""
        with self.tracker.start_run(
            run_name=run_name or f"lora-{task}",
            tags={"run_type": "lora", "task": task},
        ):
            self.tracker.log_params(
                {
                    "model_name": model_name,
                    "task": task,
                    "adapter_path": output_dir,
                    "train_rows": train_rows,
                    "eval_rows": eval_rows,
                    **hyperparams,
                }
            )
            self.tracker.log_metrics(metrics)
            from mlflow import active_run

            run = active_run()
            return run.info.run_id if run is not None else ""
