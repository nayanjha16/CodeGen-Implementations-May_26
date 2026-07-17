#!/usr/bin/env python3
"""Smoke-test Space task handlers without loading the full model."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

SPACE_DIR = Path(__file__).resolve().parent.parent / "deploy" / "hf_space"
sys.path.insert(0, str(SPACE_DIR))


def test_prompt_templates() -> None:
    from prompt_templates import (
        format_code2doc_inference,
        format_java2py_inference,
        format_nl2py_inference,
    )

    nl = format_nl2py_inference("factorial of n")
    assert "Write Python for: factorial of n" in nl
    assert nl.endswith("### Response:\n")

    java = format_java2py_inference("int x = 1;")
    assert "```java" in java
    assert "```python" in java

    doc = format_code2doc_inference("def add(a, b): pass")
    assert "Generate documentation" in doc
    assert "def add(a, b): pass" in doc


def test_task_handlers() -> None:
    with patch("app.get_generator") as mock_get:
        mock_gen = MagicMock()
        mock_gen.generate.return_value = "def factorial(n):\n    ..."
        mock_get.return_value = mock_gen

        import app

        out = app.run_nl2py("factorial", 512, 0.2, 0.95)
        assert "factorial" in out
        mock_gen.generate.assert_called_once()
        assert mock_gen.generate.call_args.kwargs["response_type"] == "code"

        mock_gen.generate.reset_mock()
        out = app.run_java2py("class Main {}", 512, 0.2, 0.95)
        assert mock_gen.generate.call_args.kwargs["response_type"] == "code"

        mock_gen.generate.reset_mock()
        mock_gen.generate.return_value = "Returns the sum of two numbers."
        out = app.run_code2doc("def add(a, b): return a + b", 512, 0.2, 0.95)
        assert "sum" in out
        assert mock_gen.generate.call_args.kwargs["response_type"] == "doc"


def test_generator_postprocessing() -> None:
    from generator import CodeGenerator

    code = CodeGenerator._extract_code("def foo():\n    pass\n```\nextra")
    assert code == "def foo():\n    pass"

    doc = CodeGenerator._extract_documentation("Returns sum.\n```")
    assert doc == "Returns sum."


if __name__ == "__main__":
    test_prompt_templates()
    test_task_handlers()
    test_generator_postprocessing()
    print("All smoke tests passed.")
