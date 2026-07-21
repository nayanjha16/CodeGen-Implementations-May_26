"""Task 1a: Program synthesis — natural language problem description -> code."""

from __future__ import annotations

import re
from typing import Any

from codegen_rag.tasks.base_task import BaseTask

_STOP_MARKERS = ("\nclass ", "\n\n\n", "\nif __name__")


class ProgramSynthesisTask(BaseTask):
    task_name = "program_synthesis"

    def __init__(self, *args: Any, language: str = "python", **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.language = language

    def build_prompt(self, record: dict[str, Any]) -> str:
        intent = record.get("intent") or record.get("problem_description", "")
        lang_comment = {
            "python": f'"""{intent}"""\n',
            "java": f"// {intent}\n",
            "cpp": f"// {intent}\n",
        }.get(self.language, f"// {intent}\n")
        return lang_comment

    def postprocess(self, raw_completion: str) -> str:
        text = raw_completion
        # Truncate at the first marker that signals the model has drifted onto
        # a new, unrelated top-level definition.
        cut_points = [text.find(marker) for marker in _STOP_MARKERS if marker in text]
        if cut_points:
            text = text[: min(cut_points)]
        # Drop trailing incomplete lines (dangling open brackets, etc.).
        text = re.sub(r"\n\s*$", "", text)
        return text.strip()
