"""SQL generation using CodeGen model."""

from __future__ import annotations

import re
from typing import Any

from src.models.model_loader import CodeGenModel, load_model
from src.text2sql.prompt_builder import PromptBuilder


class SQLGenerator:
    """Generate SQL queries from natural language using CodeGen."""

    def __init__(
        self,
        model: CodeGenModel | None = None,
        prompt_builder: PromptBuilder | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.config = config or {}
        model_cfg = self.config.get("model", {})
        gen_cfg = self.config.get("generation", {})

        self.model = model or load_model(
            model_name=model_cfg.get("name", "Salesforce/codegen-350M-multi"),
            device=model_cfg.get("device", "auto"),
            max_length=model_cfg.get("max_length", 512),
        )
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.gen_config = gen_cfg

    def _extract_sql(self, raw_output: str) -> str:
        """Extract SQL from model output."""
        text = raw_output.strip()

        # Try fenced code block
        code_match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if code_match:
            return code_match.group(1).strip()

        # Take first SQL-like line
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for line in lines:
            if re.match(r"^(SELECT|INSERT|UPDATE|DELETE|WITH)\b", line, re.IGNORECASE):
                return line

        return lines[0] if lines else text

    def generate(
        self,
        question: str,
        schema: str,
        decoding_strategy: str | None = None,
    ) -> dict[str, str]:
        """Generate SQL for a single question."""
        prompt = self.prompt_builder.build(question, schema)
        raw = self.model.generate(
            prompt,
            max_new_tokens=self.gen_config.get("max_new_tokens", 256),
            temperature=self.gen_config.get("temperature", 0.2),
            top_p=self.gen_config.get("top_p", 0.95),
            num_beams=self.gen_config.get("num_beams", 4),
            do_sample=self.gen_config.get("do_sample", False),
            decoding_strategy=decoding_strategy
            or self.gen_config.get("decoding_strategy", "greedy"),
        )
        sql = self._extract_sql(raw)
        return {"prompt": prompt, "raw_output": raw, "sql": sql}

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
            results.append(result)
        return results
