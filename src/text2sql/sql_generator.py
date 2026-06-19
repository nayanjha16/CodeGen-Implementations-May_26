"""SQL generation using CodeGen model."""

from __future__ import annotations

import re
from typing import Any

from src.models.model_loader import CodeGenModel, is_seq2seq_model, load_model
from src.text2sql.prompt_builder import PromptBuilder
from src.text2sql.sql_validator import SQLValidator
from src.utils.schema_conversion import derive_mongo_schema_json


class SQLGenerator:
    """Generate SQL queries from natural language using a HuggingFace model."""

    _SELECT_FROM_RE = re.compile(
        r"^\s*SELECT\b.+\bFROM\b",
        re.IGNORECASE | re.DOTALL,
    )
    _NON_SQL_MARKER_RE = re.compile(
        r"\n(?:Output:|MongoDB:|Python:|JavaScript:|import\s+|#include\b|\"\"\"|SQL:\n)",
        re.IGNORECASE,
    )
    _NON_SQL_LINE_RE = re.compile(
        r"^(?:Output:|MongoDB:|Python:|JavaScript:|import\s+|#include\b|\"\"\"|conn\s*=|for\s+\w+\s+in|print\s*\(|SQL:)",
        re.IGNORECASE,
    )
    _SQL_KEYWORD_LINE_RE = re.compile(
        r"^(?:SELECT|FROM|WHERE|GROUP\s+BY|ORDER\s+BY|HAVING|LIMIT|OFFSET|"
        r"JOIN|INNER\s+JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|ON|AND|OR|UNION|WITH|"
        r"DISTINCT|\)|\(|,)",
        re.IGNORECASE,
    )
    _SQL_FRAGMENT_LINE_RE = re.compile(r"^[\w\s.*'\",=<>!+\-/%()?;[\]]+$")
    _SQL_STOP_STRINGS = [
        "\nOutput:",
        "\nMongoDB:",
        "\nPython:",
        "\nJavaScript:",
        "\nimport ",
        "\n#include",
        '\n"""',
        "\n\nSQL:",
        "\nSQL:\n",
        "\n\nMongoDB:",
        "\n\nPython:",
    ]

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

    def _trim_non_sql_suffix(self, text: str) -> str:
        """Drop generation artifacts such as Output blocks and host-language code."""
        match = self._NON_SQL_MARKER_RE.search(text)
        if match:
            text = text[: match.start()]
        return text.strip()

    def _is_sql_fragment_line(self, line: str) -> bool:
        if self._NON_SQL_LINE_RE.match(line):
            return False
        if self._SQL_KEYWORD_LINE_RE.match(line):
            return True
        return bool(self._SQL_FRAGMENT_LINE_RE.match(line))

    def _normalize_sql(self, sql: str) -> str:
        return re.sub(r"\s+", " ", sql).strip()

    def _extract_multiline_select(self, text: str) -> str:
        """Collect a multi-line SELECT statement before non-SQL continuation."""
        text = self._trim_non_sql_suffix(text)
        if not re.match(r"^\s*SELECT\b", text, re.IGNORECASE):
            return ""

        lines: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                if lines:
                    break
                continue
            if lines and not self._is_sql_fragment_line(stripped):
                break
            if (
                lines
                and re.match(r"^SELECT\b", stripped, re.IGNORECASE)
                and self._looks_like_sql(self._normalize_sql(" ".join(lines)))
            ):
                break
            if not lines and not re.match(r"^SELECT\b", stripped, re.IGNORECASE):
                continue
            lines.append(stripped)

        if not lines:
            return ""

        candidate = self._normalize_sql(" ".join(lines))
        if self._looks_like_sql(candidate):
            return candidate
        return ""

    def _extract_sql(self, raw_output: str) -> str:
        """Extract SQL from model output."""
        text = self._trim_non_sql_suffix(raw_output.strip())

        code_match = re.search(
            r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE
        )
        if code_match:
            candidate = self._normalize_sql(code_match.group(1))
            if self._looks_like_sql(candidate):
                return candidate
            if re.match(
                r"^(SELECT|INSERT|UPDATE|DELETE|WITH)\b", candidate, re.IGNORECASE
            ):
                return candidate

        multiline = self._extract_multiline_select(text)
        if multiline:
            return multiline

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for line in lines:
            if self._looks_like_sql(line):
                return line
            if re.match(
                r"^(SELECT|INSERT|UPDATE|DELETE|WITH)\b", line, re.IGNORECASE
            ):
                return line

        if self._looks_like_sql(text):
            return self._normalize_sql(text)

        return ""

    def _resolve_decoding_strategy(self, decoding_strategy: str | None) -> str:
        configured = (
            decoding_strategy
            or self.gen_config.get("decoding_strategy", "greedy")
        )
        if self._seq2seq and configured == "greedy":
            return self.gen_config.get("seq2seq_decoding_strategy", "beam")
        return configured

    def build_prompt(
        self,
        question: str,
        schema: str,
    ) -> str:
        """Build the SQL-only generation prompt for a question and schema."""
        return self.prompt_builder.build(question, schema)

    def generate(
        self,
        question: str,
        schema: str,
        decoding_strategy: str | None = None,
    ) -> dict[str, str]:
        """Generate SQL for a single question."""
        nosql_schema = derive_mongo_schema_json(schema)
        prompt = self.build_prompt(question, schema)
        strategy = self._resolve_decoding_strategy(decoding_strategy)
        generate_kwargs: dict[str, Any] = {
            "max_new_tokens": self.gen_config.get("max_new_tokens", 256),
            "temperature": self.gen_config.get("temperature", 0.2),
            "top_p": self.gen_config.get("top_p", 0.95),
            "num_beams": self.gen_config.get("num_beams", 4),
            "do_sample": self.gen_config.get("do_sample", False),
            "decoding_strategy": strategy,
        }
        if not self._seq2seq:
            generate_kwargs["stop_strings"] = self._SQL_STOP_STRINGS

        raw = self.model.generate(prompt, **generate_kwargs)
        sql = self._extract_sql(raw)
        trimmed_raw = self._trim_non_sql_suffix(raw)
        return {
            "prompt": prompt,
            "raw_output": trimmed_raw or raw.strip(),
            "sql": sql,
            "nosql_schema": nosql_schema,
        }

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
            schema = ex.get("schema", "")
            result = self.generate(
                ex["question"],
                schema,
                decoding_strategy=decoding_strategy,
            )
            result["question"] = ex["question"]
            result["schema"] = schema
            result["ground_truth"] = ex.get("sql", "")
            result["sql_valid"] = self.is_valid_sql(result["sql"])
            results.append(result)
        return results
