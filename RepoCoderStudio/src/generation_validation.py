"""Deterministic, non-executing validation of model outputs."""

from __future__ import annotations

import ast
from typing import Any, Dict

from src.code_extraction import extract_code, extract_natural_language
from src.config import CONFIG, AppConfig
from src.java_validator import JavaValidator
from src.python_validator import PythonValidator

PYTHON_TASKS = {"T1", "T4"}
JAVA_TASKS = {"T2", "T3"}
NL_TASKS = {"T5", "T6"}


def _is_trivial_python_expression(code: str) -> bool:
    """Return whether code is only a bare name or literal placeholder."""

    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError, TypeError):
        return False
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
        return False
    return isinstance(tree.body[0].value, (ast.Name, ast.Constant))


def _is_import_only_python(code: str) -> bool:
    """Return whether parseable output contains imports but no implementation."""

    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError, TypeError):
        return False
    meaningful = [
        node
        for node in tree.body
        if not isinstance(node, (ast.Import, ast.ImportFrom))
        and not (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        )
    ]
    return bool(tree.body) and not meaningful


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
            if result.get("status") == "PASS" and _is_trivial_python_expression(code):
                result = {"status": "FAIL", "reason": "trivial_python_expression"}
            elif result.get("status") == "PASS" and _is_import_only_python(code):
                result = {"status": "FAIL", "reason": "python_no_implementation"}
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
