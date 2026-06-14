"""Qwen-based evaluation of SQL to NoSQL schema and query equivalence."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from src.models.model_loader import CodeGenModel, ensure_model_cached

logger = logging.getLogger("tend")

DEFAULT_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

_EVAL_PROMPT = """You are a database expert. Compare the SQL input with the MongoDB output.

SQL schema:
{sql_schema}

SQL query:
{sql_query}

MongoDB schema:
{nosql_schema}

MongoDB query:
{nosql_query}

Decide whether the MongoDB schema and query are semantically equivalent to the SQL schema and query.
Respond with JSON only:
{{
  "schema_correct": true or false,
  "query_correct": true or false,
  "schema_reason": "short reason",
  "query_reason": "short reason"
}}"""


class QwenTENDEvaluator:
    """Use Qwen2.5-0.5B-Instruct to judge schema/query equivalence."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str = "auto",
        max_length: int = 2048,
        max_new_tokens: int = 256,
    ):
        self.model_name = model_name
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

    def _build_prompt(
        self,
        sql_schema: str,
        sql_query: str,
        nosql_schema: str,
        nosql_query: str,
    ) -> str:
        return _EVAL_PROMPT.format(
            sql_schema=sql_schema.strip(),
            sql_query=sql_query.strip(),
            nosql_schema=nosql_schema.strip(),
            nosql_query=nosql_query.strip(),
        )

    def _extract_eval_json(self, text: str) -> dict[str, Any] | None:
        """Find a JSON object with expected evaluation keys in model output."""
        decoder = json.JSONDecoder()
        candidates: list[dict[str, Any]] = []
        for index, char in enumerate(text):
            if char != "{":
                continue
            try:
                parsed, _ = decoder.raw_decode(text, index)
            except json.JSONDecodeError:
                continue
            if (
                isinstance(parsed, dict)
                and "schema_correct" in parsed
                and "query_correct" in parsed
            ):
                candidates.append(parsed)
        return candidates[-1] if candidates else None

    def _parse_response(self, text: str) -> dict[str, Any]:
        text = text.strip()
        # Chat templates may prefix assistant output with a role marker.
        if "assistant" in text.lower():
            text = re.split(r"\bassistant\b", text, flags=re.IGNORECASE)[-1].strip()

        parsed = self._extract_eval_json(text)
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

    def evaluate_sample(
        self,
        sql_schema: str,
        sql_query: str,
        nosql_schema: str,
        nosql_query: str,
    ) -> dict[str, Any]:
        """Evaluate one SQL/NoSQL pair with Qwen."""
        messages = [
            {
                "role": "user",
                "content": self._build_prompt(sql_schema, sql_query, nosql_schema, nosql_query),
            }
        ]
        prompt = self.model.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        response = self.model.generate(
            prompt,
            max_new_tokens=self.max_new_tokens,
            temperature=0.1,
            do_sample=False,
            decoding_strategy="greedy",
        )
        result = self._parse_response(response)
        result["overall_correct"] = result["schema_correct"] and result["query_correct"]
        return result

    def evaluate_batch(
        self,
        samples: list[dict[str, str]],
    ) -> list[dict[str, Any]]:
        """Evaluate multiple samples sequentially."""
        results: list[dict[str, Any]] = []
        for sample in samples:
            results.append(
                self.evaluate_sample(
                    sql_schema=sample.get("sql_schema", ""),
                    sql_query=sample.get("sql_query", ""),
                    nosql_schema=sample.get("nosql_schema", ""),
                    nosql_query=sample.get("nosql_query", ""),
                )
            )
        return results
