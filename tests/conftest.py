"""Shared pytest fixtures. No GPU, network, or model download is required to
run this suite — model calls are mocked via `FakeCodeGenModel`."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make `src/` importable without an editable install, so `pytest` works
# straight out of a fresh clone.
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class FakeCodeGenModel:
    """Drop-in stand-in for CodeGenModel that returns canned completions,
    so task/evaluator tests never need to download or run the real model."""

    def __init__(self, canned_completion: str = "def foo():\n    return 42\n"):
        self.canned_completion = canned_completion
        self.calls: list[str] = []

    def generate(self, prompt: str, gen_config=None) -> list[str]:  # noqa: ANN001
        self.calls.append(prompt)
        return [self.canned_completion]

    def batch_generate(self, prompts: list[str], gen_config=None) -> list[list[str]]:  # noqa: ANN001
        return [self.generate(p, gen_config) for p in prompts]


@pytest.fixture
def fake_model() -> FakeCodeGenModel:
    return FakeCodeGenModel()


@pytest.fixture
def sample_codocbench_record() -> dict:
    return {
        "code": "def add(a, b):\n    return a + b",
        "docstring": "Add two numbers and return the sum.",
        "language": "python",
        "function_name": "add",
        "intent": "Write a function that adds two numbers",
        "commit_diff": "- def add(a, b):\n-     pass\n+ def add(a, b):\n+     return a + b",
        "commit_message": "Implement add() to return the sum of two numbers",
    }
