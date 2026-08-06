from src.generation_validation import GenerationOutputValidator
from src.realworld_rag_generation_eval import _first_generated_line


def test_single_line_completion_normalization():
    assert _first_generated_line("### Response\n```python\nreturn total\n```") == "return total"


def test_python_output_validation():
    validator = GenerationOutputValidator()
    result = validator.validate("T1", "def add(a, b):\n    return a + b")
    assert result["valid"] is True
    assert result["target"] == "python"


def test_python_output_rejects_bare_identifier_placeholder():
    validator = GenerationOutputValidator()
    result = validator.validate("T1", "s")
    assert result["valid"] is False
    assert result["status"] == "FAIL"
    assert result["reason"] == "trivial_python_expression"


def test_python_output_rejects_import_only_placeholder():
    validator = GenerationOutputValidator()
    result = validator.validate("T1", "import re")
    assert result["valid"] is False
    assert result["reason"] == "python_no_implementation"


def test_nl_output_rejects_code_fence():
    validator = GenerationOutputValidator()
    assert validator.validate("T5", "```python\npass\n```")["valid"] is False
