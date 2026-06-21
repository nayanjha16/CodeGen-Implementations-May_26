"""Qwen-based semantic evaluation for text-to-SQL and SQL-to-NoSQL."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from src.models.model_loader import CodeGenModel, ensure_model_cached
from src.utils.config import get_qwen_evaluator_model_name

logger = logging.getLogger("codegen")

DEFAULT_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

_TEXT2SQL_PROMPT = """You are a strict SQL equivalence judge.

Compare the predicted SQL against the ground truth SQL. Use the text-to-SQL generation context below when judging whether the predicted query answers the question.

Rules:
- sql_correct is true ONLY if both queries are semantically equivalent and would return the same results on the schema.
- They must use the same base table(s), columns, filters, aggregations, ordering, and limits.
- If predicted SQL is empty, invalid, or incomplete, sql_correct must be false.
- Ignore formatting differences (case, whitespace, alias names) when the logic matches.
- Queries against catalog/system tables (e.g. sqlite_master, information_schema) are NOT equivalent to queries against user tables.
- Do not mark sql_correct true unless you are confident both queries answer the question the same way.
- If they differ in tables, columns, filters, or aggregates, sql_correct must be false.

{context}Predicted SQL:
{predicted_sql}

Ground truth SQL:
{ground_truth_sql}

Respond with JSON only:
{{
  "sql_correct": true or false,
  "reason": "short reason focused on differences between predicted and ground truth"
}}"""

_SQL2NOSQL_PROMPT = """You are a strict MongoDB query equivalence judge.

Compare the predicted MongoDB query against the reference MongoDB query. Judge whether both queries would return the same output (same documents, counts, aggregate values, sort order, and limits) when run on the same collection data.

Rules:
- query_correct is true ONLY if both queries are semantically equivalent and would produce the same results.
- Ignore formatting differences: whitespace, quote style, key ordering, and minor alias naming when the returned data matches.
- Different but equivalent MongoDB APIs are correct when they produce the same output, for example:
  - db.collection.countDocuments({{}}) vs db.collection.aggregate([{{"$group": {{"_id": null, "count": {{"$sum": 1}}}}}}])
  - db.collection.distinct("field", filter) vs equivalent find/distinct patterns with the same filter
  - db.collection.find(filter, projection).sort(sort).limit(n) vs find with equivalent sort/limit options
- For aggregates: same filters, grouping logic, and computed values matter; cosmetic output-field name differences in $group are acceptable when values match.
- query_correct must be false if the predicted query is empty, invalid shell syntax, targets a different collection, or differs in filters, sort direction, limit, distinct field, or aggregation logic.
- Do not mark query_correct true unless you are confident both queries return the same output.

{context}Predicted MongoDB query:
{predicted_mongodb_query}

Reference MongoDB query:
{reference_mongodb_query}

Respond with JSON only (no markdown fences). In reason, do not include curly braces or backticks:
{{
  "query_correct": true or false,
  "reason": "short reason focused on output differences, not syntax style"
}}"""

_DOCUMENTATION_PROMPT = """You are a strict MongoDB query documentation judge.

Decide whether the generated documentation accurately and completely explains the MongoDB query below.

Rules:
- doc_correct is true ONLY if the documentation correctly explains the collection, operation, filters, projections, sorting, limits, and aggregation behavior when present.
- Ignore stylistic differences when the meaning matches the query.
- doc_correct must be false if the output is empty, unrelated, or misses key query semantics.
- Brief mentions of the MongoDB query syntax inside the explanation are acceptable.
- Do not mark doc_correct true unless you are confident the documentation would help a developer understand what the query returns.

{context}MongoDB query:
{mongodb_query}

Generated documentation:
{generated_output}

Respond with JSON only (no markdown fences). In reason, do not include curly braces or backticks:
{{
  "doc_correct": true or false,
  "reason": "short reason focused on missing or incorrect explanation"
}}"""

_TEND_PROMPT = """You are a database expert. Compare the SQL input with the MongoDB output.

{sections}Decide whether the MongoDB schema and query are semantically equivalent to the SQL schema and query.
Respond with JSON only:
{{
  "schema_correct": true or false,
  "query_correct": true or false,
  "schema_reason": "short reason",
  "query_reason": "short reason"
}}"""


def _format_section(label: str, value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    return f"{label}:\n{text}\n\n"


def _build_sections(fields: dict[str, str]) -> str:
    return "".join(
        section
        for label, key in fields.items()
        if (section := _format_section(label, key))
    )


_SYSTEM_TABLES = frozenset(
    {
        "sqlite_master",
        "sqlite_temp_master",
        "information_schema",
        "pg_catalog",
        "mysql",
        "sys",
    }
)


def _extract_query_tables(sql: str) -> set[str]:
    """Extract table names referenced in FROM/JOIN clauses."""
    tables: set[str] = set()
    for match in re.finditer(
        r"\b(?:FROM|JOIN)\s+([`\"[]?(?:\w+\.)?\w+[`\"\]]?)",
        sql,
        re.IGNORECASE,
    ):
        name = match.group(1).strip("`\"[]")
        if "." in name:
            name = name.split(".")[-1]
        tables.add(name.lower())
    return tables


def _has_structural_table_mismatch(predicted_sql: str, ground_truth_sql: str) -> bool:
    """Return True when queries clearly target different tables."""
    predicted_tables = _extract_query_tables(predicted_sql)
    ground_truth_tables = _extract_query_tables(ground_truth_sql)
    if not predicted_tables or not ground_truth_tables:
        return False

    if predicted_tables & _SYSTEM_TABLES and not (ground_truth_tables & _SYSTEM_TABLES):
        return True
    if predicted_tables.isdisjoint(ground_truth_tables):
        return True
    return False


def _is_valid_select_sql(sql: str) -> bool:
    """Return True when SQL is a non-trivial SELECT ... FROM query."""
    from src.text2sql.sql_validator import SQLValidator

    sql = sql.strip()
    if not sql or not re.match(r"^\s*SELECT\b", sql, re.IGNORECASE):
        return False
    if not re.search(r"\bFROM\b", sql, re.IGNORECASE):
        return False

    validator = SQLValidator()
    syntax = validator.validate_syntax(sql)
    completeness = validator.validate_completeness(sql)
    return syntax["valid"] and completeness["complete"]


class QwenEvaluator:
    """Use Qwen2.5-0.5B-Instruct to judge semantic equivalence."""

    def __init__(
        self,
        model_name: str | None = None,
        device: str = "auto",
        max_length: int = 2048,
        max_new_tokens: int = 256,
    ):
        self.model_name = model_name or get_qwen_evaluator_model_name()
        self.max_new_tokens = max_new_tokens
        self._model: CodeGenModel | None = None
        self._device = device
        self._max_length = max_length

    def load(self) -> None:
        """Cache model locally once, then load from disk."""
        cache_path = ensure_model_cached(self.model_name, causal=True)
        self._model = CodeGenModel(
            model_name=self.model_name,
            device=self._device,
            max_length=self._max_length,
            model_path=cache_path,
        )
        self._model.load()

    @property
    def model(self) -> CodeGenModel:
        if self._model is None:
            self.load()
        assert self._model is not None
        return self._model

    def _generate(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        formatted = self.model.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        return self.model.generate(
            formatted,
            max_new_tokens=self.max_new_tokens,
            temperature=0.1,
            do_sample=False,
            decoding_strategy="greedy",
        )

    def _extract_eval_json(self, text: str, required_keys: set[str]) -> dict[str, Any] | None:
        decoder = json.JSONDecoder()
        candidates: list[dict[str, Any]] = []
        for index, char in enumerate(text):
            if char != "{":
                continue
            try:
                parsed, _ = decoder.raw_decode(text, index)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict) and required_keys.issubset(parsed.keys()):
                candidates.append(parsed)
        return candidates[-1] if candidates else None

    def _strip_assistant_prefix(self, text: str) -> str:
        text = text.strip()
        if "assistant" in text.lower():
            text = re.split(r"\bassistant\b", text, flags=re.IGNORECASE)[-1].strip()
        return text

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```\s*$", "", text)
        return text.strip()

    @staticmethod
    def _extract_bool_field(text: str, field: str) -> bool | None:
        match = re.search(
            rf'"{re.escape(field)}"\s*:\s*(true|false)',
            text,
            re.IGNORECASE,
        )
        if not match:
            return None
        return match.group(1).lower() == "true"

    @staticmethod
    def _extract_string_field(text: str, field: str) -> str:
        match = re.search(
            rf'"{re.escape(field)}"\s*:\s*"((?:\\.|[^"\\])*)"',
            text,
        )
        return match.group(1) if match else ""

    def _parse_text2sql_response(self, text: str) -> dict[str, Any]:
        text = self._strip_assistant_prefix(text)
        parsed = self._extract_eval_json(text, {"sql_correct"})
        if parsed is None:
            return {
                "sql_correct": False,
                "reason": "Unable to parse model response",
                "raw_response": text,
            }
        return {
            "sql_correct": bool(parsed.get("sql_correct")),
            "reason": str(parsed.get("reason", "")),
            "raw_response": text,
        }

    def _parse_sql2nosql_response(self, text: str) -> dict[str, Any]:
        raw_response = text
        text = self._strip_code_fences(self._strip_assistant_prefix(text))
        parsed = self._extract_eval_json(text, {"query_correct"})
        if parsed is not None:
            return {
                "query_correct": bool(parsed.get("query_correct")),
                "reason": str(parsed.get("reason", "")),
                "raw_response": raw_response,
            }

        query_correct = self._extract_bool_field(text, "query_correct")
        if query_correct is not None:
            return {
                "query_correct": query_correct,
                "reason": self._extract_string_field(text, "reason"),
                "raw_response": raw_response,
            }

        return {
            "query_correct": False,
            "reason": "Unable to parse model response",
            "raw_response": raw_response,
        }

    def _parse_documentation_response(self, text: str) -> dict[str, Any]:
        raw_response = text
        text = self._strip_code_fences(self._strip_assistant_prefix(text))
        parsed = self._extract_eval_json(text, {"doc_correct"})
        if parsed is not None:
            return {
                "doc_correct": bool(parsed.get("doc_correct")),
                "reason": str(parsed.get("reason", "")),
                "raw_response": raw_response,
            }

        doc_correct = self._extract_bool_field(text, "doc_correct")
        if doc_correct is not None:
            return {
                "doc_correct": doc_correct,
                "reason": self._extract_string_field(text, "reason"),
                "raw_response": raw_response,
            }

        return {
            "doc_correct": False,
            "reason": "Unable to parse model response",
            "raw_response": raw_response,
        }

    def evaluate_text2sql_sample(
        self,
        question: str = "",
        schema: str = "",
        predicted_sql: str = "",
        ground_truth_sql: str = "",
        raw_output: str = "",
        prompt: str = "",
        predicted_sql_valid: bool | None = None,
    ) -> dict[str, Any]:
        """Evaluate one text-to-SQL prediction with Qwen."""
        is_valid = (
            predicted_sql_valid
            if predicted_sql_valid is not None
            else _is_valid_select_sql(predicted_sql)
        )
        if not is_valid:
            skip_reason = "Skipped Qwen evaluation: predicted SQL is empty or not a valid SELECT query"
            return {
                "sql_correct": False,
                "reason": "Predicted SQL is empty or not a valid SELECT query",
                "raw_response": skip_reason,
                "predicted_sql_valid": False,
            }

        from src.evaluation.metrics import EvaluationMetrics

        metrics = EvaluationMetrics()
        if metrics.exact_match(predicted_sql, ground_truth_sql):
            return {
                "sql_correct": True,
                "reason": "Exact match after SQL normalization",
                "raw_response": "Skipped Qwen evaluation: exact match after normalization",
                "predicted_sql_valid": True,
            }

        if _has_structural_table_mismatch(predicted_sql, ground_truth_sql):
            predicted_tables = sorted(_extract_query_tables(predicted_sql))
            ground_truth_tables = sorted(_extract_query_tables(ground_truth_sql))
            reason = (
                "Predicted and ground truth reference different tables: "
                f"predicted={predicted_tables}, ground_truth={ground_truth_tables}"
            )
            return {
                "sql_correct": False,
                "reason": reason,
                "raw_response": f"Skipped Qwen evaluation: {reason}",
                "predicted_sql_valid": True,
            }

        context = _build_sections(
            {
                "Generation prompt": prompt,
                "Question": question,
                "Schema": schema,
            }
        )
        response = self._generate(
            _TEXT2SQL_PROMPT.format(
                context=context,
                predicted_sql=predicted_sql.strip(),
                ground_truth_sql=ground_truth_sql.strip(),
            )
        )
        result = self._parse_text2sql_response(response)
        result["predicted_sql_valid"] = True
        return result

    def evaluate_sql2nosql_sample(
        self,
        predicted_mongodb_query: str = "",
        reference_mongodb_query: str = "",
        reference_sql: str = "",
        **_kwargs: Any,
    ) -> dict[str, Any]:
        """Evaluate one SQL-to-MongoDB translation by comparing MongoDB queries."""
        if not predicted_mongodb_query.strip() or not reference_mongodb_query.strip():
            skip_reason = "Skipped Qwen evaluation: missing predicted or reference MongoDB query"
            return {
                "query_correct": False,
                "reason": "Missing predicted or reference MongoDB query",
                "raw_response": skip_reason,
            }

        context = _build_sections({"Source SQL": reference_sql})
        response = self._generate(
            _SQL2NOSQL_PROMPT.format(
                context=context,
                predicted_mongodb_query=predicted_mongodb_query.strip(),
                reference_mongodb_query=reference_mongodb_query.strip(),
            )
        )
        result = self._parse_sql2nosql_response(response)
        result["overall_correct"] = result["query_correct"]
        return result

    def evaluate_documentation_sample(
        self,
        mongodb_query: str = "",
        raw_output: str = "",
        reference_sql: str = "",
        predicted_documentation: str = "",
        **_kwargs: Any,
    ) -> dict[str, Any]:
        """Evaluate one MongoDB query documentation sample with Qwen."""
        generated_output = raw_output.strip() or predicted_documentation.strip()

        if not mongodb_query.strip():
            skip_reason = "Skipped Qwen evaluation: missing MongoDB query"
            return {
                "doc_correct": False,
                "reason": "Missing MongoDB query",
                "raw_response": skip_reason,
            }

        if not generated_output:
            skip_reason = "Skipped Qwen evaluation: missing model raw output"
            return {
                "doc_correct": False,
                "reason": "Missing model raw output",
                "raw_response": skip_reason,
            }

        context = _build_sections({"Source SQL": reference_sql})
        response = self._generate(
            _DOCUMENTATION_PROMPT.format(
                context=context,
                mongodb_query=mongodb_query.strip(),
                generated_output=generated_output,
            )
        )
        result = self._parse_documentation_response(response)
        result["overall_correct"] = result["doc_correct"]
        return result

    def evaluate_tend_sample(
        self,
        sql_schema: str,
        sql_query: str,
        nosql_schema: str,
        nosql_query: str,
    ) -> dict[str, Any]:
        """Evaluate one TEND-style SQL/NoSQL conversion pair."""
        sections = _build_sections(
            {
                "SQL schema": sql_schema,
                "SQL query": sql_query,
                "MongoDB schema": nosql_schema,
                "MongoDB query": nosql_query,
            }
        )
        response = self._generate(_TEND_PROMPT.format(sections=sections))
        result = self._parse_tend_response(response)
        result["overall_correct"] = result["schema_correct"] and result["query_correct"]
        return result

    def _parse_tend_response(self, text: str) -> dict[str, Any]:
        text = self._strip_assistant_prefix(text)
        parsed = self._extract_eval_json(text, {"schema_correct", "query_correct"})
        if parsed is None:
            return {
                "schema_correct": False,
                "query_correct": False,
                "schema_reason": "Unable to parse model response",
                "query_reason": "Unable to parse model response",
                "raw_response": text,
            }
        return {
            "schema_correct": bool(parsed.get("schema_correct")),
            "query_correct": bool(parsed.get("query_correct")),
            "schema_reason": str(parsed.get("schema_reason", "")),
            "query_reason": str(parsed.get("query_reason", "")),
            "raw_response": text,
        }

    def evaluate_text2sql_batch(
        self,
        samples: list[dict[str, str]],
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for sample in samples:
            results.append(
                self.evaluate_text2sql_sample(
                    question=sample.get("question", ""),
                    schema=sample.get("schema", ""),
                    predicted_sql=sample.get("predicted_sql", sample.get("sql", "")),
                    ground_truth_sql=sample.get("ground_truth", ""),
                    raw_output=sample.get("raw_output", ""),
                    prompt=sample.get("prompt", ""),
                )
            )
        return results

    def evaluate_sql2nosql_batch(
        self,
        samples: list[dict[str, str]],
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for sample in samples:
            results.append(
                self.evaluate_sql2nosql_sample(
                    predicted_mongodb_query=sample.get("predicted_mongodb_query", ""),
                    reference_mongodb_query=sample.get("reference_mongodb_query", ""),
                    reference_sql=sample.get("reference_sql", sample.get("ground_truth", "")),
                )
            )
        return results

    def evaluate_documentation_batch(
        self,
        samples: list[dict[str, str]],
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for sample in samples:
            results.append(
                self.evaluate_documentation_sample(
                    mongodb_query=sample.get(
                        "mongodb_query", sample.get("predicted_mongodb_query", "")
                    ),
                    raw_output=sample.get(
                        "doc_raw_output", sample.get("raw_output", "")
                    ),
                    reference_sql=sample.get("reference_sql", sample.get("ground_truth", "")),
                    predicted_documentation=sample.get(
                        "predicted_documentation", sample.get("documentation", "")
                    ),
                )
            )
        return results

    @staticmethod
    def summarize_text2sql(results: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(results)
        if total == 0:
            return {"sql_correct_rate": 0.0, "count": 0}
        correct = sum(1 for result in results if result.get("sql_correct"))
        return {
            "sql_correct_rate": correct / total,
            "count": total,
        }

    @staticmethod
    def summarize_sql2nosql(results: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(results)
        if total == 0:
            return {
                "query_correct_rate": 0.0,
                "overall_correct_rate": 0.0,
                "count": 0,
            }
        query_correct = sum(1 for result in results if result.get("query_correct"))
        return {
            "query_correct_rate": query_correct / total,
            "overall_correct_rate": query_correct / total,
            "count": total,
        }

    @staticmethod
    def summarize_documentation(results: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(results)
        if total == 0:
            return {
                "doc_correct_rate": 0.0,
                "overall_correct_rate": 0.0,
                "count": 0,
            }
        doc_correct = sum(1 for result in results if result.get("doc_correct"))
        return {
            "doc_correct_rate": doc_correct / total,
            "overall_correct_rate": doc_correct / total,
            "count": total,
        }


# Backward-compatible alias used by TEND.
QwenTENDEvaluator = QwenEvaluator
