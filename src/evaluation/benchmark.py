"""Benchmark runner for TEND dataset evaluation."""

from __future__ import annotations

import logging
from typing import Any

from src.documentation.doc_generator import DocumentationGenerator
from src.documentation.evaluator import DocumentationEvaluator
from src.documentation.reference_builder import ReferenceDocumentationBuilder
from src.evaluation.metrics import EvaluationMetrics
from src.evaluation.mlflow_tracker import MLflowTracker
from src.models.model_loader import CodeGenModel, load_model
from src.sql2nosql.evaluator import NoSQLEvaluator
from src.sql2nosql.nosql_generator import NoSQLGenerator
from src.text2sql.sql_generator import SQLGenerator
from src.training.tasks import TRAINING_TASKS
from src.utils.config import get_adapter_path, load_config
from src.utils.logging import log_step, setup_logging, task_label
from src.utils.seeds import set_seeds

logger = logging.getLogger("codegen")


def load_task_model(
    task: str,
    config: dict[str, Any],
    *,
    adapter_run: str | None = None,
    eager: bool = True,
) -> CodeGenModel:
    """Load base model with a task-specific LoRA adapter when ``adapter_run`` is set."""
    normalized = task.strip().lower()
    if normalized not in TRAINING_TASKS:
        allowed = ", ".join(sorted(TRAINING_TASKS))
        raise ValueError(f"Unknown task '{task}'. Expected one of: {allowed}")
    if adapter_run:
        adapter_path = get_adapter_path(normalized, config, run=adapter_run)
        return load_model(config=config, adapter_path=adapter_path, eager=eager)
    return load_model(config=config, eager=eager)


class BenchmarkRunner:
    """Run independent benchmarks for text2sql, sql2nosql, and nosql2doc on gold rows."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        sql_generator: SQLGenerator | None = None,
        metrics: EvaluationMetrics | None = None,
        nosql_evaluator: NoSQLEvaluator | None = None,
        nosql_generator: NoSQLGenerator | None = None,
        doc_generator: DocumentationGenerator | None = None,
        doc_evaluator: DocumentationEvaluator | None = None,
        tracker: MLflowTracker | None = None,
        enable_mlflow: bool = True,
        adapter_run: str | None = None,
    ):
        setup_logging()
        self.config = config or load_config()
        set_seeds(self.config)
        self.adapter_run = adapter_run
        logger.info(
            "BenchmarkRunner init: adapter_run=%s max_samples=%s",
            adapter_run or "baseline",
            self.config.get("evaluation", {}).get("max_samples", 100),
        )

        if sql_generator is not None:
            self.sql_generator = sql_generator
        elif adapter_run:
            logger.info("[%s] Loading model with LoRA adapter", task_label("text2sql"))
            text2sql_model = load_task_model("text2sql", self.config, adapter_run=adapter_run)
            self.sql_generator = SQLGenerator(model=text2sql_model, config=self.config)
        else:
            logger.info("[%s] Loading base model (no adapter)", task_label("text2sql"))
            self.sql_generator = SQLGenerator(config=self.config)

        self.metrics = metrics or EvaluationMetrics()
        self.nosql_evaluator = nosql_evaluator or NoSQLEvaluator()

        if nosql_generator is not None:
            self.nosql_generator = nosql_generator
        elif adapter_run:
            logger.info("[%s] Loading model with LoRA adapter", task_label("sql2nosql"))
            sql2nosql_model = load_task_model("sql2nosql", self.config, adapter_run=adapter_run)
            self.nosql_generator = NoSQLGenerator(model=sql2nosql_model, config=self.config)
        else:
            logger.info("[%s] Loading base model (no adapter)", task_label("sql2nosql"))
            self.nosql_generator = NoSQLGenerator(config=self.config)

        if doc_generator is not None:
            self.doc_generator = doc_generator
        elif adapter_run:
            logger.info("[%s] Loading model with LoRA adapter", task_label("nosql2doc"))
            nosql2doc_model = load_task_model("nosql2doc", self.config, adapter_run=adapter_run)
            self.doc_generator = DocumentationGenerator(
                model=nosql2doc_model,
                config=self.config,
            )
        else:
            logger.info("[%s] Loading base model (no adapter)", task_label("nosql2doc"))
            self.doc_generator = DocumentationGenerator(config=self.config)
        self.doc_evaluator = doc_evaluator or DocumentationEvaluator()
        self.reference_doc_builder = ReferenceDocumentationBuilder()
        eval_cfg = self.config.get("evaluation", {})
        self.enable_mlflow = enable_mlflow
        self.tracker = None
        if enable_mlflow:
            self.tracker = tracker or MLflowTracker(
                experiment_name=eval_cfg.get("experiment_name", "codegen-text2sql"),
                tracking_uri=eval_cfg.get("mlflow_tracking_uri"),
            )
        self.max_samples = eval_cfg.get("max_samples", 100)

    @staticmethod
    def _is_valid_select_sql(sql: str, validator) -> bool:
        """Return True when SQL is a complete SELECT ... FROM query."""
        import re

        if not sql.strip():
            return False
        if not re.match(r"^\s*SELECT\b", sql, re.IGNORECASE):
            return False
        if not re.search(r"\bFROM\b", sql, re.IGNORECASE):
            return False
        syntax = validator.validate_syntax(sql)
        completeness = validator.validate_completeness(sql)
        return syntax["valid"] and completeness["complete"]

    def evaluate_sql2nosql(
        self,
        samples: list[dict[str, str]],
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Generate MongoDB from gold SQL in each sample (independent of text2sql output)."""
        from src.text2sql.sql_validator import SQLValidator

        log_step("sql2nosql", "Evaluating SQL-to-MongoDB on %d samples", len(samples))
        sql_validator = SQLValidator()
        pred_queries: list[str] = []
        ref_queries: list[str] = []
        structured_preds: list[dict[str, Any]] = []
        structured_refs: list[dict[str, Any]] = []
        nosql_results: list[dict[str, Any]] = []

        nosql_samples = []
        for example in samples:
            ref_sql = example.get("sql", "")
            nosql_samples.append(
                {
                    "question": example.get("question", ""),
                    "schema": example.get("schema", ""),
                    "nosql_schema": example.get("nosql_schema", ""),
                    "sql": ref_sql,
                    "ground_truth_sql": ref_sql,
                }
            )

        nosql_gen_results = self.nosql_generator.generate_batch(nosql_samples)

        for example, nosql_gen in zip(samples, nosql_gen_results):
            ref_sql = example.get("sql", "")
            ref_sql_valid = self._is_valid_select_sql(ref_sql, sql_validator)

            pred_mongo = nosql_gen.get("mongodb_query", "")
            pred_warnings: list[str] = []
            if not pred_mongo:
                pred_warnings.append(
                    "Unable to extract MongoDB query from model output"
                )
            elif not nosql_gen.get("mongodb_valid", False):
                pred_warnings.append(
                    "Model output is not valid MongoDB shell syntax"
                )

            ref_mongo = example.get("nosql_query", "").strip()
            if ref_mongo:
                ref_trans = {
                    "mongodb_query": ref_mongo,
                    "collection": NoSQLGenerator._parse_collection(ref_mongo),
                    "filter": {},
                    "projection": {},
                    "warnings": [],
                    "success": True,
                }
            else:
                ref_trans = {
                    "mongodb_query": "",
                    "collection": "",
                    "filter": {},
                    "projection": {},
                    "warnings": ["Missing gold nosql_query in dataset example"],
                    "success": False,
                }

            pred_structured = {
                "mongodb_query": pred_mongo,
                "collection": NoSQLGenerator._parse_collection(pred_mongo),
                "filter": {},
                "projection": {},
                "warnings": pred_warnings,
                "success": bool(pred_mongo) and nosql_gen.get("mongodb_valid", False),
            }

            pred_queries.append(pred_mongo)
            ref_queries.append(ref_trans.get("mongodb_query", ""))
            structured_preds.append(pred_structured)
            structured_refs.append(ref_trans)

            nosql_results.append(
                {
                    "question": example.get("question", ""),
                    "schema": example.get("schema", ""),
                    "db_id": example.get("db_id", ""),
                    "source_dataset": example.get("source_dataset", "spider"),
                    "reference_sql": ref_sql,
                    "reference_sql_valid": ref_sql_valid,
                    "nosql_schema": nosql_gen.get("nosql_schema", ""),
                    "nosql_prompt": nosql_gen.get("prompt", ""),
                    "nosql_raw_output": nosql_gen.get("raw_output", ""),
                    "predicted_mongodb_query": pred_mongo,
                    "reference_mongodb_query": ref_trans.get("mongodb_query", ""),
                    "reference_documentation": example.get("documentation", ""),
                    "reference_translation_success": ref_trans.get("success", False),
                    "mongodb_warnings": "; ".join(pred_warnings),
                    "mongodb_success": pred_structured["success"],
                    "collection": pred_structured.get("collection", ""),
                    "filter": pred_structured.get("filter", {}),
                    "projection": pred_structured.get("projection", {}),
                    "reference_collection": ref_trans.get("collection", ""),
                    "reference_filter": ref_trans.get("filter", {}),
                    "reference_projection": ref_trans.get("projection", {}),
                    "gold_sql_output": example.get("sql_output", ""),
                    "gold_nosql_output": example.get("nosql_output", ""),
                }
            )

        execution_contexts = [
            {
                "db_id": example.get("db_id", ""),
                "dataset": example.get("source_dataset", "spider") or "spider",
                "sql_output": example.get("sql_output", ""),
                "nosql_output": example.get("nosql_output", ""),
            }
            for example in samples
        ]
        reference_sql_queries = [example.get("sql", "") for example in samples]
        nosql_metrics = self.nosql_evaluator.evaluate_all(
            pred_queries,
            ref_queries,
            reference_sql_queries=reference_sql_queries,
            execution_contexts=execution_contexts,
        )
        valid = sum(1 for r in nosql_results if r.get("mongodb_success"))
        log_step(
            "sql2nosql",
            "Metrics complete: %d/%d valid MongoDB queries",
            valid,
            len(nosql_results),
        )
        return nosql_metrics, nosql_results

    def evaluate_documentation(
        self,
        samples: list[dict[str, str]],
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Generate documentation from gold MongoDB queries (independent of sql2nosql output)."""
        log_step("nosql2doc", "Evaluating NoSQL-to-Documentation on %d samples", len(samples))
        pred_docs: list[str] = []
        ref_docs: list[str] = []
        mongodb_queries: list[str] = []
        structured_preds: list[dict[str, Any]] = []
        structured_refs: list[dict[str, Any]] = []
        doc_results: list[dict[str, Any]] = []

        doc_samples = []
        for example in samples:
            gold_nosql = example.get("nosql_query", "").strip()
            doc_samples.append(
                {
                    "question": example.get("question", ""),
                    "schema": example.get("schema", ""),
                    "nosql_schema": example.get("nosql_schema", ""),
                    "mongodb_query": gold_nosql,
                    "nosql_query": gold_nosql,
                    "reference_mongodb_query": gold_nosql,
                    "reference_sql": example.get("sql", ""),
                }
            )

        doc_gen_results = self.doc_generator.generate_batch(doc_samples)

        for example, doc_gen in zip(samples, doc_gen_results):
            mongodb_query = doc_gen.get("mongodb_query", "")
            predicted_doc = doc_gen.get("documentation", "")
            reference_doc = example.get("documentation", "").strip()
            if not reference_doc:
                reference_doc = doc_gen.get("reference_documentation", "")
            reference_mongodb = example.get("nosql_query", "").strip()

            pred_warnings: list[str] = []
            if not mongodb_query.strip():
                pred_warnings.append("Missing MongoDB query for documentation generation")
            elif not predicted_doc:
                pred_warnings.append("Unable to extract documentation from model output")

            pred_structured = {
                **self.reference_doc_builder.to_structured(mongodb_query),
                "documentation": predicted_doc,
                "warnings": pred_warnings,
                "success": bool(predicted_doc) and doc_gen.get("documentation_valid", False),
            }
            ref_structured = {
                **self.reference_doc_builder.to_structured(reference_mongodb),
                "documentation": reference_doc,
            }

            pred_docs.append(predicted_doc)
            ref_docs.append(reference_doc)
            mongodb_queries.append(mongodb_query)
            structured_preds.append(pred_structured)
            structured_refs.append(ref_structured)

            doc_results.append(
                {
                    "question": example.get("question", ""),
                    "schema": example.get("schema", ""),
                    "reference_sql": example.get("sql", ""),
                    "reference_mongodb_query": reference_mongodb,
                    "input_mongodb_query": mongodb_query,
                    "doc_prompt": doc_gen.get("prompt", ""),
                    "doc_raw_output": doc_gen.get("raw_output", ""),
                    "predicted_documentation": predicted_doc,
                    "reference_documentation": reference_doc,
                    "documentation_warnings": "; ".join(pred_warnings),
                    "documentation_success": pred_structured["success"],
                }
            )

        doc_metrics = self.doc_evaluator.evaluate_all(pred_docs, ref_docs)
        doc_metrics["judge_score"] = 0.0
        valid = sum(1 for r in doc_results if r.get("documentation_success"))
        log_step(
            "nosql2doc",
            "Metrics complete: %d/%d valid documentation outputs",
            valid,
            len(doc_results),
        )
        return doc_metrics, doc_results

    def run_on_dataset(
        self,
        examples: list[dict[str, str]],
        dataset_name: str,
        db_resolver=None,
    ) -> dict[str, Any]:
        """Evaluate on a list of standardized examples."""
        samples = examples[: self.max_samples]
        logger.info(
            "=== Evaluation pipeline: %d samples from %s ===",
            len(samples),
            dataset_name,
        )
        log_step("text2sql", "Starting Text-to-SQL evaluation")

        gen_results = self.sql_generator.generate_batch(samples)
        for result, example in zip(gen_results, samples):
            result.setdefault("schema", example.get("schema", ""))
            result.setdefault("db_id", example.get("db_id", ""))
            result.setdefault("source_dataset", example.get("source_dataset", "spider"))
            result.setdefault("sql_output", example.get("sql_output", ""))
            result.setdefault("ground_truth", example.get("sql", ""))
            if not result.get("prompt"):
                result["prompt"] = self.sql_generator.build_prompt(
                    result.get("question", example.get("question", "")),
                    result.get("schema", ""),
                )

        predictions = [r["sql"] for r in gen_results]
        references = [r.get("ground_truth", ex["sql"]) for r, ex in zip(gen_results, samples)]

        execution_contexts = [
            {
                "db_id": example.get("db_id", ""),
                "dataset": example.get("source_dataset", "spider") or "spider",
                "sql_output": example.get("sql_output", ""),
            }
            for example in samples
        ]

        log_step("text2sql", "Computing metrics (execution accuracy, exact match, structural similarity)")
        eval_metrics = self.metrics.evaluate_all(
            predictions,
            references,
            execution_contexts,
        )
        valid_sql = sum(1 for r in gen_results if r.get("sql_valid"))
        log_step(
            "text2sql",
            "Metrics complete: %d/%d valid SQL queries",
            valid_sql,
            len(gen_results),
        )

        nosql_metrics, nosql_results = self.evaluate_sql2nosql(samples)
        doc_metrics, doc_results = self.evaluate_documentation(samples)
        logger.info("=== Evaluation pipeline complete ===")

        run_id = None
        if self.tracker:
            extra_params: dict[str, Any] = {
                "max_samples": len(samples),
                "decoding_strategy": self.config.get("generation", {}).get(
                    "decoding_strategy", "greedy"
                ),
            }
            if self.adapter_run:
                extra_params["run_type"] = "lora"
                extra_params["adapter_run"] = self.adapter_run
                for task in ("text2sql", "sql2nosql", "nosql2doc"):
                    extra_params[f"adapter_path_{task}"] = str(
                        get_adapter_path(task, self.config, run=self.adapter_run)
                    )
            run_id = self.tracker.log_evaluation(
                model_name=self.config.get("model", {}).get("name", "codegen"),
                dataset=dataset_name,
                prompt_template=self.sql_generator.prompt_builder.get_template_name(),
                metrics=eval_metrics,
                nosql_metrics=nosql_metrics,
                extra_params=extra_params,
            )

        return {
            "dataset": dataset_name,
            "metrics": eval_metrics,
            "nosql_metrics": nosql_metrics,
            "doc_metrics": doc_metrics,
            "predictions": gen_results,
            "nosql_predictions": nosql_results,
            "doc_predictions": doc_results,
            "mlflow_run_id": run_id,
        }

    def run_tend(
        self,
        config: str = "spider",
        split: str = "test",
        *,
        use_gold_validation: bool = True,
    ) -> dict[str, Any]:
        """Run benchmark on TEND data.

        Spider baseline eval always uses the frozen gold validation JSONL
        under ``data/spider_gold_validation.jsonl``. Other configs load from
        Hugging Face when ``use_gold_validation`` is False or no gold file
        applies.
        """
        from src.datasets.tend_loader import (
            GOLD_VALIDATION_DATASET_NAME,
            TENDLoader,
            load_gold_validation,
        )

        if use_gold_validation and config == "spider":
            examples = load_gold_validation()
            return self.run_on_dataset(
                examples,
                dataset_name=GOLD_VALIDATION_DATASET_NAME,
            )

        tend_cfg = self.config.get("datasets", {}).get("tend", {})
        dataset_id = tend_cfg.get("dataset_id")
        loader = TENDLoader(dataset_id=dataset_id, config=config)
        examples = loader.load_split(split)
        return self.run_on_dataset(
            examples,
            dataset_name=f"tend_{config}_{split}",
        )
