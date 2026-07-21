"""Task 1b: Documentation generation — raw function -> docstring (args/returns/complexity)."""

from __future__ import annotations

from typing import Any

from codegen_rag.tasks.base_task import BaseTask


class DocumentationGenerationTask(BaseTask):
    task_name = "documentation_generation"

    def build_prompt(self, record: dict[str, Any]) -> str:
        code = record["code"]
        return (
            f"{code}\n"
            "# Generate a docstring describing purpose, args, returns, and time complexity:\n"
            '"""\n'
        )

    def postprocess(self, raw_completion: str) -> str:
        text = raw_completion
        # Model may emit the closing triple-quote; trim everything after it.
        if '"""' in text:
            text = text.split('"""')[0]
        return text.strip()
