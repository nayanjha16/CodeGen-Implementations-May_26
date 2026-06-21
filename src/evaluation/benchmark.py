"""Benchmark runner for Spider and BirdBench evaluation."""

from __future__ import annotations

import logging
from typing import Any

from src.documentation.doc_generator import DocumentationGenerator
from src.documentation.evaluator import DocumentationEvaluator
from src.documentation.reference_builder import ReferenceDocumentationBuilder
from src.evaluation.metrics import EvaluationMetrics
from src.evaluation.mlflow_tracker import MLflowTracker
from src.sql2nosql.evaluator import NoSQLEvaluator
from src.sql2nosql.nosql_generator import NoSQLGenerator
from src.sql2nosql.translator import SQLToNoSQLTranslator
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
        nosql_evaluator: NoSQLEvaluator | None = None,
        nosql_generator: NoSQLGenerator | None = None,
        nosql_translator: SQLToNoSQLTranslator | None = None,
        doc_generator: DocumentationGenerator | None = None,
        doc_evaluator: DocumentationEvaluator | None = None,
        tracker: MLflowTracker | None = None,
        enable_mlflow: bool = True,
    ):
        self.config = config or load_config()
        set_seeds(self.config)
        self.sql_generator = sql_generator or SQLGenerator(config=self.config)
        self.metrics = metrics or EvaluationMetrics()
        self.nosql_evaluator = nosql_evaluator or NoSQLEvaluator()
        self.nosql_translator = nosql_translator or SQLToNoSQLTranslator()
        self.nosql_generator = nosql_generator or NoSQLGenerator(
            model=self.sql_generator.model,
            config=self.config,
        )
        self.doc_generator = doc_generator or DocumentationGenerator(
            model=self.sql_generator.model,
            config=self.config,
        )
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
        gen_results: list[dict[str, Any]],
        samples: list[dict[str, str]],
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Generate predicted MongoDB from reference SQL; derive reference MongoDB from the same SQL."""
        from src.text2sql.sql_validator import SQLValidator

        sql_validator = SQLValidator()
        pred_queries: list[str] = []
        ref_queries: list[str] = []
        structured_preds: list[dict[str, Any]] = []
        structured_refs: list[dict[str, Any]] = []
        nosql_results: list[dict[str, Any]] = []

        nosql_samples = []
        for result, example in zip(gen_results, samples):
            schema = result.get("schema", example.get("schema", ""))
            ref_sql = result.get("ground_truth", example.get("sql", ""))
            nosql_samples.append(
                {
                    "question": result.get("question", example.get("question", "")),
                    "schema": schema,
                    "nosql_schema": result.get("nosql_schema", ""),
                    "sql": ref_sql,
                    "ground_truth_sql": ref_sql,
                }
            )

        nosql_gen_results = self.nosql_generator.generate_batch(nosql_samples)

        for result, example, nosql_gen in zip(gen_results, samples, nosql_gen_results):
            pred_sql = result.get("sql", "")
            ref_sql = result.get("ground_truth", example.get("sql", ""))

            pred_sql_valid = self._is_valid_select_sql(pred_sql, sql_validator)
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

            ref_trans = self.nosql_translator.translate(ref_sql)

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
                    **result,
                    "reference_sql": ref_sql,
                    "predicted_sql": pred_sql,
                    "predicted_sql_valid": pred_sql_valid,
                    "reference_sql_valid": ref_sql_valid,
                    "nosql_schema": nosql_gen.get("nosql_schema", ""),
                    "nosql_prompt": nosql_gen.get("prompt", ""),
                    "nosql_raw_output": nosql_gen.get("raw_output", ""),
                    "predicted_mongodb_query": pred_mongo,
                    "reference_mongodb_query": ref_trans.get("mongodb_query", ""),
                    "reference_translation_success": ref_trans.get("success", False),
                    "mongodb_warnings": "; ".join(pred_warnings),
                    "mongodb_success": pred_structured["success"],
                    "collection": pred_structured.get("collection", ""),
                    "filter": pred_structured.get("filter", {}),
                    "projection": pred_structured.get("projection", {}),
                    "reference_collection": ref_trans.get("collection", ""),
                    "reference_filter": ref_trans.get("filter", {}),
                    "reference_projection": ref_trans.get("projection", {}),
                }
            )

        nosql_metrics = self.nosql_evaluator.evaluate_all(
            pred_queries,
            ref_queries,
            structured_preds,
            structured_refs,
        )
        nosql_metrics["total_count"] = len(nosql_results)
        nosql_metrics["scored_count"] = len(pred_queries)
        nosql_metrics["translation_success_rate"] = (
            sum(1 for r in nosql_results if r.get("mongodb_success")) / len(nosql_results)
            if nosql_results
            else 0.0
        )
        return nosql_metrics, nosql_results

    def evaluate_documentation(
        self,
        nosql_results: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Generate documentation for MongoDB queries produced during sql2nosql."""
        pred_docs: list[str] = []
        ref_docs: list[str] = []
        mongodb_queries: list[str] = []
        structured_preds: list[dict[str, Any]] = []
        structured_refs: list[dict[str, Any]] = []
        doc_results: list[dict[str, Any]] = []

        doc_samples = []
        for result in nosql_results:
            doc_samples.append(
                {
                    "question": result.get("question", ""),
                    "schema": result.get("schema", ""),
                    "nosql_schema": result.get("nosql_schema", ""),
                    "mongodb_query": result.get("predicted_mongodb_query", ""),
                    "predicted_mongodb_query": result.get("predicted_mongodb_query", ""),
                    "reference_mongodb_query": result.get("reference_mongodb_query", ""),
                    "reference_sql": result.get("reference_sql", result.get("ground_truth", "")),
                }
            )

        doc_gen_results = self.doc_generator.generate_batch(doc_samples)

        for result, doc_gen in zip(nosql_results, doc_gen_results):
            mongodb_query = doc_gen.get("mongodb_query", "")
            predicted_doc = doc_gen.get("documentation", "")
            reference_doc = doc_gen.get("reference_documentation", "")
            reference_mongodb = result.get("reference_mongodb_query", "")

            pred_warnings: list[str] = []
            if not mongodb_query.strip():
                pred_warnings.append("Missing MongoDB query for documentation generation")
            elif not predicted_doc:
                pred_warnings.append("Unable to extract documentation from model output")
            elif not doc_gen.get("documentation_valid", False):
                pred_warnings.append("Generated documentation failed structure validation")

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
                    **result,
                    "doc_prompt": doc_gen.get("prompt", ""),
                    "doc_raw_output": doc_gen.get("raw_output", ""),
                    "predicted_documentation": predicted_doc,
                    "reference_documentation": reference_doc,
                    "documentation_warnings": "; ".join(pred_warnings),
                    "documentation_success": pred_structured["success"],
                }
            )

        doc_metrics = self.doc_evaluator.evaluate_all(
            pred_docs,
            ref_docs,
            mongodb_queries=mongodb_queries,
            structured_preds=structured_preds,
            structured_refs=structured_refs,
        )
        doc_metrics["total_count"] = len(doc_results)
        doc_metrics["scored_count"] = len(pred_docs)
        doc_metrics["translation_success_rate"] = (
            sum(1 for r in doc_results if r.get("documentation_success")) / len(doc_results)
            if doc_results
            else 0.0
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
        logger.info("Evaluating %d samples from %s", len(samples), dataset_name)

        gen_results = self.sql_generator.generate_batch(samples)
        for result, example in zip(gen_results, samples):
            result.setdefault("schema", example.get("schema", ""))
            result.setdefault("db_id", example.get("db_id", ""))
            if not result.get("prompt"):
                result["prompt"] = self.sql_generator.build_prompt(
                    result.get("question", example.get("question", "")),
                    result.get("schema", ""),
                )

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
        nosql_metrics, nosql_results = self.evaluate_sql2nosql(gen_results, samples)
        doc_metrics, doc_results = self.evaluate_documentation(nosql_results)

        run_id = None
        if self.tracker:
            run_id = self.tracker.log_evaluation(
                model_name=self.config.get("model", {}).get("name", "codegen"),
                dataset=dataset_name,
                prompt_template=self.sql_generator.prompt_builder.get_template_name(),
                metrics=eval_metrics,
                nosql_metrics=nosql_metrics,
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
            "nosql_metrics": nosql_metrics,
            "doc_metrics": doc_metrics,
            "predictions": gen_results,
            "nosql_predictions": nosql_results,
            "doc_predictions": doc_results,
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
