from rustgen.config import Config
from rustgen.translator import get_translator
from rustgen.translator.base import TranslationTask
from rustgen.translator.mock import MockTranslator


def test_factory_returns_mock_by_default():
    assert isinstance(get_translator(Config()), MockTranslator)


def test_english_to_rust_returns_rust():
    task = TranslationTask(description="Add two integers and return the sum.")
    out = MockTranslator().generate(task)
    assert "fn " in out
    assert "Add two integers and return the sum." in out


def test_python_to_rust_returns_rust():
    task = TranslationTask(
        description="Add two numbers.",
        python_code="def add(a, b):\n    return a + b",
    )
    out = MockTranslator().generate(task)
    assert "fn " in out
    assert "Python -> Rust" in out


def test_mock_is_deterministic():
    task = TranslationTask(description="Reverse a string.")
    translator = MockTranslator()
    assert translator.generate(task) == translator.generate(task)
