"""Build TEND-style datasets from Spider/BIRD sources."""

from __future__ import annotations

import csv
import json
import logging
import re
from pathlib import Path
from typing import Any

from tqdm import tqdm

from TEND.paths import build_output_csv_path
from TEND.qwen_evaluator import DEFAULT_MODEL, QwenTENDEvaluator
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


class TENDDatasetBuilder:
    """Generate and evaluate TEND-style SQL/NoSQL dataset rows."""

    def __init__(
        self,
        dataset: str = "spider",
        split: str = "train",
        max_samples: int | None = None,
        evaluate: bool = True,
        model_name: str = DEFAULT_MODEL,
    ):
        self.dataset = dataset.lower()
        self.split = split
        self.max_samples = max_samples
        self.evaluate = evaluate
        self.model_name = model_name
        self._tables_by_db: dict[str, dict[str, Any]] | None = None
        self._evaluator: QwenTENDEvaluator | None = None

    def _load_spider_tables(self) -> dict[str, dict[str, Any]]:
        if self._tables_by_db is not None:
            return self._tables_by_db
        self._tables_by_db = SpiderSource().load_tables()
        return self._tables_by_db

    def _load_spider_samples(self) -> list[dict[str, str]]:
        samples = SpiderSource().load_split(self.split)
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

    def build_row(self, sample: dict[str, str], index: int) -> dict[str, Any]:
        """Convert one source sample into a TEND dataset row."""
        sql_schema = self._sql_schema_for_sample(sample)
        sql_query = sample.get("sql", "")
        nosql_schema = convert_schema_json(sql_schema)
        query_result = convert_query(sql_query)
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

        if self.evaluate:
            evaluation = self._get_evaluator().evaluate_sample(
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
    def _write_csv(output: Path, rows: list[dict[str, Any]]) -> None:
        if not rows:
            output.write_text("", encoding="utf-8")
            return
        fieldnames = list(rows[0].keys())
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
        return summary
