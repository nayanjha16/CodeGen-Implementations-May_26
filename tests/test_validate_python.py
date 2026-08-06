"""Tests for validate_python_code static and semantic checks."""

from agent.tools import validate_python_code


def test_validate_ok_simple():
    assert validate_python_code.invoke({"code": "x = 1\n"}) == "OK"


def test_validate_syntax_error():
    result = validate_python_code.invoke({"code": "print(2 +"})
    assert "SyntaxError" in result


def test_validate_missing_return_annotation():
    code = "def get_total() -> int:\n    pass\n"
    result = validate_python_code.invoke({"code": code})
    assert "Semantic" in result
    assert "get_total" in result


def test_validate_getter_only_pass():
    code = "def get_name():\n    pass\n"
    result = validate_python_code.invoke({"code": code})
    assert "Semantic" in result
    assert "get_name" in result


def test_validate_java_leakage():
    code = "public class Main:\n    pass\n"
    result = validate_python_code.invoke({"code": code})
    assert "Semantic" in result or "SyntaxError" in result


def test_validate_undefined_name():
    code = "print(undefined_var)\n"
    result = validate_python_code.invoke({"code": code})
    assert result != "OK"
    assert "undefined" in result.lower() or "Pyflakes" in result
