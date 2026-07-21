"""Task 1d: PL-to-PL translation — function in one language -> equivalent in another."""

from __future__ import annotations

from typing import Any

from codegen_rag.tasks.base_task import BaseTask

_STOP_MARKERS = ("\n# Translate", "\n\n\n")


class CodeTranslationTask(BaseTask):
    task_name = "code_translation"

    def __init__(
        self, *args: Any, source_language: str = "python", target_language: str = "java", **kwargs: Any
    ):
        super().__init__(*args, **kwargs)
        self.source_language = source_language
        self.target_language = target_language

    def build_prompt(self, record: dict[str, Any]) -> str:
        source_code = record.get("source_code") or record.get("code", "")
        return (
            f"# Translate the following {self.source_language} function to "
            f"{self.target_language}:\n{source_code}\n# {self.target_language} version:\n"
        )

    def postprocess(self, raw_completion: str) -> str:
        text = raw_completion
        cut_points = [text.find(marker) for marker in _STOP_MARKERS if marker in text]
        if cut_points:
            text = text[: min(cut_points)]
        return text.strip()
