"""Deterministic, non-executing validation of model outputs."""

from __future__ import annotations

from typing import Any, Dict

from src.code_extraction import extract_code, extract_natural_language
from src.config import CONFIG, AppConfig
from src.java_validator import JavaValidator
from src.python_validator import PythonValidator

PYTHON_TASKS = {"T1", "T4"}
JAVA_TASKS = {"T2", "T3"}
NL_TASKS = {"T5", "T6"}


class GenerationOutputValidator:
    def __init__(self, config: AppConfig = CONFIG):
        # extract_code() is pure text post-processing (src/code_extraction.py) --
        # deliberately not routed through GenerationEngine, which imports
        # torch/transformers at module level and would make this "deterministic,
        # non-executing validator" transitively require an ML framework just to
        # construct.
        self.python = PythonValidator()
        self.java = JavaValidator(config)

    def validate(self, task_id: str, output: str) -> Dict[str, Any]:
        if task_id in PYTHON_TASKS:
            code = extract_code(output, "python")
            result = self.python.validate(code)
            return {
                "target": "python",
                "valid": result.get("status") == "PASS",
                "status": result.get("status"),
                "reason": result.get("reason"),
                "normalized_output": code,
            }
        if task_id in JAVA_TASKS:
            code = extract_code(output, "java")
            result = self.java.validate(code)
            return {
                "target": "java",
                "valid": result.get("status") == "PASS",
                "status": result.get("status"),
                "reason": result.get("reason"),
                "compiler_stderr": result.get("stderr", ""),
                "normalized_output": code,
            }
        text = extract_natural_language(output)
        return {
            "target": "natural_language",
            "valid": bool(text) and "```" not in text,
            "status": "PASS" if text and "```" not in text else "FAIL",
            "reason": None if text and "```" not in text else "empty_or_code_fenced_output",
            "normalized_output": text,
        }
