"""SQL generation using CodeGen model."""

from __future__ import annotations

import re
from typing import Any

from src.models.model_loader import CodeGenModel, is_seq2seq_model, load_model
from src.text2sql.prompt_builder import PromptBuilder
from src.text2sql.sql_validator import SQLValidator


class SQLGenerator:
    """Generate SQL queries from natural language using a HuggingFace model."""

    _SELECT_FROM_RE = re.compile(
        r"^\s*SELECT\b.+\bFROM\b",
        re.IGNORECASE | re.DOTALL,
    )

    def __init__(
        self,
        model: CodeGenModel | None = None,
        prompt_builder: PromptBuilder | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.config = config or {}
        gen_cfg = self.config.get("generation", {})

        self.model = model or load_model(config=self.config)
        if prompt_builder is not None:
            self.prompt_builder = prompt_builder
        else:
            model_name = self.model.model_name
            self.prompt_builder = PromptBuilder.for_model(model_name, self.config)
        self.gen_config = gen_cfg
        self.validator = SQLValidator()
        self._seq2seq = is_seq2seq_model(self.model.model_name)

    def _looks_like_sql(self, text: str) -> bool:
        """Return True when text resembles a SELECT query with a FROM clause."""
        text = text.strip()
        if not text:
            return False
        return bool(self._SELECT_FROM_RE.match(text))

    def _extract_sql(self, raw_output: str) -> str:
        """Extract SQL from model output."""
        text = raw_output.strip()

        code_match = re.search(
            r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE
        )
        if code_match:
            candidate = code_match.group(1).strip()
            if self._looks_like_sql(candidate):
                return candidate
            if re.match(
                r"^(SELECT|INSERT|UPDATE|DELETE|WITH)\b", candidate, re.IGNORECASE
            ):
                return candidate

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for line in lines:
            if self._looks_like_sql(line):
                return line
            if re.match(
                r"^(SELECT|INSERT|UPDATE|DELETE|WITH)\b", line, re.IGNORECASE
            ):
                return line

        if self._looks_like_sql(text):
            return text.strip()

        return lines[0] if lines else text

    def _resolve_decoding_strategy(self, decoding_strategy: str | None) -> str:
        configured = (
            decoding_strategy
            or self.gen_config.get("decoding_strategy", "greedy")
        )
        if self._seq2seq and configured == "greedy":
            return self.gen_config.get("seq2seq_decoding_strategy", "beam")
        return configured

    def generate(
        self,
        question: str,
        schema: str,
        decoding_strategy: str | None = None,
    ) -> dict[str, str]:
        """Generate SQL for a single question."""
        prompt = self.prompt_builder.build(question, schema)
        strategy = self._resolve_decoding_strategy(decoding_strategy)
        raw = self.model.generate(
            prompt,
            max_new_tokens=self.gen_config.get("max_new_tokens", 256),
            temperature=self.gen_config.get("temperature", 0.2),
            top_p=self.gen_config.get("top_p", 0.95),
            num_beams=self.gen_config.get("num_beams", 4),
            do_sample=self.gen_config.get("do_sample", False),
            decoding_strategy=strategy,
        )
        sql = self._extract_sql(raw)
        return {"prompt": prompt, "raw_output": raw, "sql": sql}

    def is_valid_sql(self, sql: str) -> bool:
        """Return True when SQL passes syntax and completeness checks."""
        if not self._looks_like_sql(sql):
            return False
        syntax = self.validator.validate_syntax(sql)
        completeness = self.validator.validate_completeness(sql)
        return syntax["valid"] and completeness["complete"]

    def generate_batch(
        self,
        examples: list[dict[str, str]],
        decoding_strategy: str | None = None,
    ) -> list[dict[str, str]]:
        """Generate SQL for multiple examples."""
        results = []
        for ex in examples:
            result = self.generate(
                ex["question"],
                ex.get("schema", ""),
                decoding_strategy=decoding_strategy,
            )
            result["question"] = ex["question"]
            result["ground_truth"] = ex.get("sql", "")
            result["sql_valid"] = self.is_valid_sql(result["sql"])
            results.append(result)
        return results
