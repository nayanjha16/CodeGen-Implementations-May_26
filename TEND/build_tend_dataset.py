"""Build TEND-style datasets from Spider/BIRD sources."""

from __future__ import annotations

import csv
import json
import logging
import re
from pathlib import Path
from typing import Any

from tqdm import tqdm

from src.sql2nosql.translator import SQLToNoSQLTranslator

from TEND.paths import build_output_csv_path
from TEND.qwen_doc_generator import QwenDocumentationGenerator
from TEND.qwen_evaluator import QwenTENDEvaluator, get_qwen_evaluator_model_name
from TEND.schema_to_sql import generate_sql_schema, generate_sql_schema_from_spider_schema
from TEND.spider_source import SpiderSource
from TEND.sql_schema_to_mongo_schema import convert_schema_json
from TEND.sql_to_mongo import convert_query
from TEND.validator import (
    validate_conversion,
    validate_mongo_query,
    validate_mongo_schema,
    validate_sql_query,
    validate_sql_schema,
)

logger = logging.getLogger("tend")

DOCUMENTATION_COLUMN = "documentation"
_BASE_FIELD_ORDER = [
    "source",
    "db_id",
    "question",
    "sql_schema",
    "sql_query",
    "nosql_schema",
    "nosql_query",
    DOCUMENTATION_COLUMN,
    "metadata",
    "conversion_success",
    "schema_correct",
    "query_correct",
    "overall_correct",
    "schema_reason",
    "query_reason",
    "evaluation_response",
]


class TENDDatasetBuilder:
    """Generate and evaluate TEND-style SQL/NoSQL dataset rows."""

    def __init__(
        self,
        dataset: str = "spider",
        split: str = "train",
        max_samples: int | None = None,
        evaluate: bool = True,
        generate_documentation: bool = True,
        model_name: str | None = None,
        evaluator: QwenTENDEvaluator | None = None,
        doc_generator: QwenDocumentationGenerator | None = None,
        spider_source: SpiderSource | None = None,
        tables_by_db: dict[str, dict[str, Any]] | None = None,
        translator: SQLToNoSQLTranslator | None = None,
    ):
        self.dataset = dataset.lower()
        self.split = split
        self.max_samples = max_samples
        self.evaluate = evaluate
        self.generate_documentation = generate_documentation
        self.model_name = model_name or get_qwen_evaluator_model_name()
        self._evaluator = evaluator
        self._doc_generator = doc_generator
        self._spider_source = spider_source or SpiderSource()
        self._tables_by_db = tables_by_db
        self._translator = translator

    def _load_spider_tables(self) -> dict[str, dict[str, Any]]:
        if self._tables_by_db is not None:
            return self._tables_by_db
        self._tables_by_db = self._spider_source.load_tables()
        return self._tables_by_db

    def _load_spider_samples(self) -> list[dict[str, str]]:
        samples = self._spider_source.load_split(self.split)
        if self.max_samples is not None:
            samples = samples[: self.max_samples]
        return samples

    def _load_samples(self) -> list[dict[str, str]]:
        if self.dataset == "spider":
            return self._load_spider_samples()
        raise ValueError(f"Unsupported dataset '{self.dataset}'. Start with spider.")

    def _sql_schema_for_sample(self, sample: dict[str, str]) -> str:
        db_id = sample.get("db_id", "")
        tables = self._load_spider_tables()
        if db_id in tables:
            return generate_sql_schema(tables[db_id])
        return generate_sql_schema_from_spider_schema(sample.get("schema", ""))

    @staticmethod
    def _query_metadata(sql_query: str) -> dict[str, Any]:
        upper = sql_query.upper()
        joins = len(re.findall(r"\bJOIN\b", upper))
        aggregations = len(
            re.findall(r"\b(COUNT|AVG|MIN|MAX|SUM)\s*\(", upper)
        )
        tables = len(re.findall(r"\bFROM\b", upper))
        return {
            "joins": joins,
            "aggregations": aggregations,
            "from_clauses": tables,
        }

    def _get_evaluator(self) -> QwenTENDEvaluator:
        if self._evaluator is None:
            self._evaluator = QwenTENDEvaluator(model_name=self.model_name)
        return self._evaluator

    def _get_translator(self) -> SQLToNoSQLTranslator:
        if self._translator is None:
            self._translator = SQLToNoSQLTranslator()
        return self._translator

    def _get_doc_generator(self) -> QwenDocumentationGenerator:
        if self._doc_generator is None:
            self._doc_generator = QwenDocumentationGenerator(
                model_name=self.model_name,
                evaluator=self._evaluator,
            )
        return self._doc_generator

    def build_row(self, sample: dict[str, str], index: int) -> dict[str, Any]:
        """Convert one source sample into a TEND dataset row."""
        sql_schema = self._sql_schema_for_sample(sample)
        sql_query = sample.get("sql", "")
        nosql_schema = convert_schema_json(sql_schema)
        query_result = convert_query(sql_query, self._get_translator())
        nosql_query = query_result["nosql_query"]

        sql_schema_check = validate_sql_schema(sql_schema)
        sql_query_check = validate_sql_query(sql_query)
        nosql_schema_check = validate_mongo_schema(nosql_schema)
        nosql_query_check = validate_mongo_query(nosql_query)
        conversion_check = validate_conversion(nosql_query, query_result["success"])

        metadata = {
            "index": index,
            "question": sample.get("question", ""),
            "tables": sql_schema_check["table_count"],
            **self._query_metadata(sql_query),
            "conversion_warnings": query_result.get("warnings", []),
            "sql_schema_valid": sql_schema_check["valid"],
            "sql_query_valid": sql_query_check["valid"],
            "nosql_schema_valid": nosql_schema_check["valid"],
            "nosql_query_valid": nosql_query_check["valid"],
            "conversion_success": conversion_check["conversion_success"],
        }

        row: dict[str, Any] = {
            "source": self.dataset,
            "db_id": sample.get("db_id", ""),
            "question": sample.get("question", ""),
            "sql_schema": sql_schema,
            "sql_query": sql_query,
            "nosql_schema": nosql_schema,
            "nosql_query": nosql_query,
            "metadata": json.dumps(metadata, sort_keys=True),
            "conversion_success": conversion_check["conversion_success"],
        }

        if self.generate_documentation:
            doc_result = self._get_doc_generator().generate(
                mongodb_query=nosql_query,
                nosql_schema=nosql_schema,
                schema=sql_schema,
                question=sample.get("question", ""),
            )
            row[DOCUMENTATION_COLUMN] = doc_result["documentation"]

        if self.evaluate:
            evaluation = self._get_evaluator().evaluate_tend_sample(
                sql_schema=sql_schema,
                sql_query=sql_query,
                nosql_schema=nosql_schema,
                nosql_query=nosql_query,
            )
            row.update(
                {
                    "schema_correct": evaluation["schema_correct"],
                    "query_correct": evaluation["query_correct"],
                    "overall_correct": evaluation["overall_correct"],
                    "schema_reason": evaluation["schema_reason"],
                    "query_reason": evaluation["query_reason"],
                    "evaluation_response": evaluation.get("raw_response", ""),
                }
            )

        return row

    def build(self, output_path: Path | None = None) -> Path:
        """Generate dataset rows and save CSV under ``data/TEND``."""
        samples = self._load_samples()
        if not samples:
            raise RuntimeError(f"No samples found for {self.dataset}/{self.split}")

        rows: list[dict[str, Any]] = []
        for index, sample in enumerate(
            tqdm(samples, desc=f"TEND {self.dataset}/{self.split}")
        ):
            rows.append(self.build_row(sample, index))

        output = output_path or build_output_csv_path(self.dataset, self.split)
        output.parent.mkdir(parents=True, exist_ok=True)
        self._write_csv(output, rows)
        logger.info("Saved TEND dataset to %s (%d rows)", output, len(rows))
        print(f"Saved TEND dataset: {output} ({len(rows)} rows)")
        return output

    @staticmethod
    def ordered_fieldnames(rows: list[dict[str, Any]]) -> list[str]:
        """Return stable CSV column order with documentation after nosql_query."""
        if not rows:
            return list(_BASE_FIELD_ORDER)
        present = set().union(*(row.keys() for row in rows))
        ordered = [field for field in _BASE_FIELD_ORDER if field in present]
        extras = sorted(present.difference(ordered))
        return ordered + extras

    @staticmethod
    def _write_csv(output: Path, rows: list[dict[str, Any]]) -> None:
        if not rows:
            output.write_text("", encoding="utf-8")
            return
        fieldnames = TENDDatasetBuilder.ordered_fieldnames(rows)
        with open(output, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def summarize_csv(csv_path: Path) -> dict[str, Any]:
        """Compute summary metrics from a generated CSV."""
        with open(csv_path, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))

        total = len(rows)
        summary: dict[str, Any] = {"total_rows": total}
        if not rows:
            return summary

        def _mean_bool(field: str) -> float:
            values = [str(row.get(field, "")).lower() in {"true", "1"} for row in rows]
            return sum(values) / len(values) if values else 0.0

        if "conversion_success" in rows[0]:
            summary["conversion_success_rate"] = _mean_bool("conversion_success")
        if "schema_correct" in rows[0]:
            summary["schema_correct_rate"] = _mean_bool("schema_correct")
            summary["query_correct_rate"] = _mean_bool("query_correct")
            summary["overall_correct_rate"] = _mean_bool("overall_correct")
        if DOCUMENTATION_COLUMN in rows[0]:
            filled = sum(
                1 for row in rows if str(row.get(DOCUMENTATION_COLUMN, "")).strip()
            )
            summary["documentation_fill_rate"] = filled / total if total else 0.0
        return summary

    @staticmethod
    def update_documentation_in_rows(
        rows: list[dict[str, Any]],
        doc_generator: QwenDocumentationGenerator,
        *,
        force: bool = False,
        max_samples: int | None = None,
    ) -> int:
        """Backfill documentation for existing TEND rows; returns rows updated."""
        updated = 0
        limit = len(rows) if max_samples is None else min(max_samples, len(rows))
        for index in tqdm(range(limit), desc="TEND documentation"):
            row = rows[index]
            if not force and str(row.get(DOCUMENTATION_COLUMN, "")).strip():
                continue
            doc_result = doc_generator.generate(
                mongodb_query=str(row.get("nosql_query", "")),
                nosql_schema=str(row.get("nosql_schema", "")),
                schema=str(row.get("sql_schema", "")),
                question=str(row.get("question", "")),
            )
            row[DOCUMENTATION_COLUMN] = doc_result["documentation"]
            updated += 1
        return updated

    @staticmethod
    def update_csv_documentation(
        csv_path: Path,
        doc_generator: QwenDocumentationGenerator,
        *,
        output_path: Path | None = None,
        force: bool = False,
        max_samples: int | None = None,
    ) -> Path:
        """Add or refresh documentation column in an existing TEND CSV."""
        with open(csv_path, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            raise RuntimeError(f"No rows found in {csv_path}")

        updated = TENDDatasetBuilder.update_documentation_in_rows(
            rows,
            doc_generator,
            force=force,
            max_samples=max_samples,
        )

        destination = output_path or csv_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        TENDDatasetBuilder._write_csv(destination, rows)

        summary = TENDDatasetBuilder.summarize_csv(destination)
        summary_path = destination.with_suffix(".summary.json")
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        logger.info(
            "Updated documentation for %d/%d rows in %s",
            updated,
            len(rows),
            destination,
        )
        print(
            f"Updated documentation for {updated}/{len(rows)} rows: {destination}"
        )
        print(f"Summary saved: {summary_path}")
        return destination
