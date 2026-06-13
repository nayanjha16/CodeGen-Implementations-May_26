"""Benchmark runner for Spider and BirdBench evaluation."""

from __future__ import annotations

import logging
from typing import Any

from src.evaluation.metrics import EvaluationMetrics
from src.evaluation.mlflow_tracker import MLflowTracker
from src.text2sql.sql_generator import SQLGenerator
from src.utils.config import load_config
from src.utils.seeds import set_seeds

logger = logging.getLogger("codegen")


class BenchmarkRunner:
    """Run comprehensive benchmarks on text-to-SQL datasets."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        sql_generator: SQLGenerator | None = None,
        metrics: EvaluationMetrics | None = None,
        tracker: MLflowTracker | None = None,
        enable_mlflow: bool = True,
    ):
        self.config = config or load_config()
        set_seeds(self.config)
        self.sql_generator = sql_generator or SQLGenerator(config=self.config)
        self.metrics = metrics or EvaluationMetrics()
        eval_cfg = self.config.get("evaluation", {})
        self.enable_mlflow = enable_mlflow
        self.tracker = None
        if enable_mlflow:
            self.tracker = tracker or MLflowTracker(
                experiment_name=eval_cfg.get("experiment_name", "codegen-text2sql"),
                tracking_uri=eval_cfg.get("mlflow_tracking_uri"),
            )
        self.max_samples = eval_cfg.get("max_samples", 100)

    def run_on_dataset(
        self,
        examples: list[dict[str, str]],
        dataset_name: str,
        db_resolver=None,
    ) -> dict[str, Any]:
        """Evaluate on a list of standardized examples."""
        samples = examples[: self.max_samples]
        logger.info("Evaluating %d samples from %s", len(samples), dataset_name)

        gen_results = self.sql_generator.generate_batch(samples)
        for result, example in zip(gen_results, samples):
            result.setdefault("schema", example.get("schema", ""))
            result.setdefault("db_id", example.get("db_id", ""))

        predictions = [r["sql"] for r in gen_results]
        references = [r.get("ground_truth", ex["sql"]) for r, ex in zip(gen_results, samples)]

        db_paths = []
        if db_resolver:
            for result, example in zip(gen_results, samples):
                db_path = db_resolver(example.get("db_id", ""))
                db_paths.append(db_path)
                result["db_path"] = db_path
        else:
            db_paths = [None] * len(samples)

        eval_metrics = self.metrics.evaluate_all(predictions, references, db_paths)

        run_id = None
        if self.tracker:
            run_id = self.tracker.log_evaluation(
                model_name=self.config.get("model", {}).get("name", "codegen"),
                dataset=dataset_name,
                prompt_template=self.sql_generator.prompt_builder.get_template_name(),
                metrics=eval_metrics,
                extra_params={
                    "max_samples": len(samples),
                    "decoding_strategy": self.config.get("generation", {}).get(
                        "decoding_strategy", "greedy"
                    ),
                },
            )

        return {
            "dataset": dataset_name,
            "metrics": eval_metrics,
            "predictions": gen_results,
            "mlflow_run_id": run_id,
        }

    def run_spider(self, split: str = "validation") -> dict[str, Any]:
        """Run benchmark on Spider dataset."""
        from src.datasets.spider_loader import SpiderLoader

        spider_cfg = self.config.get("datasets", {}).get("spider", {})
        loader = SpiderLoader(config=self.config, cache_dir=spider_cfg.get("cache_dir"))
        examples = loader.load_split(split)
        return self.run_on_dataset(
            examples,
            dataset_name=f"spider_{split}",
            db_resolver=loader.get_database_path,
        )

    def run_bird(self, split: str = "validation") -> dict[str, Any]:
        """Run benchmark on BIRD dataset."""
        from src.datasets.bird_loader import BirdLoader

        bird_cfg = self.config.get("datasets", {}).get("bird", {})
        loader = BirdLoader(config=self.config, cache_dir=bird_cfg.get("cache_dir"))
        examples = loader.load_split(split)
        return self.run_on_dataset(
            examples,
            dataset_name=f"bird_{split}",
            db_resolver=loader.get_database_path,
        )
