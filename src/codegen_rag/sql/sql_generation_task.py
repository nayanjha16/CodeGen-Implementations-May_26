"""Task 2: natural-language question + injected schema -> SQL query."""

from __future__ import annotations

import re
from typing import Any

from codegen_rag.sql.schema_injection import build_sql_prompt
from codegen_rag.tasks.base_task import BaseTask

_SQL_FENCE_RE = re.compile(r"```(?:sql)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


class SQLGenerationTask(BaseTask):
    task_name = "sql_generation"

    def __init__(self, *args: Any, include_sample_values: bool = True, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.include_sample_values = include_sample_values

    def build_prompt(self, record: dict[str, Any]) -> str:
        return build_sql_prompt(
            question=record["question"],
            schema=record["schema"],
            include_sample_values=self.include_sample_values,
            few_shot_examples=record.get("few_shot_examples"),
        )

    def postprocess(self, raw_completion: str) -> str:
        """Extract a single, executable SQL statement from the raw completion.

        Handles three common model behaviors: markdown code fences, trailing
        commentary after the statement, and multiple statements (we keep only
        the first, since execution accuracy is evaluated per single query).
        """
        text = raw_completion.strip()

        fence_match = _SQL_FENCE_RE.search(text)
        if fence_match:
            text = fence_match.group(1).strip()

        # Stop at the first blank line or a new '#'-style prompt marker —
        # anything after that is the model drifting onto a new example.
        for stop_marker in ("\n\n", "\n#", "\nQ:", "\n-- "):
            idx = text.find(stop_marker)
            if idx != -1:
                text = text[:idx]

        # Keep only the first statement if the model chained several with ';'.
        if ";" in text:
            text = text.split(";")[0] + ";"

        return text.strip().rstrip(";").strip() + ";" if text.strip() else ""
