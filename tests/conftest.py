"""Shared pytest fixtures."""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "utils"))
sys.path.insert(0, str(PROJECT_ROOT / "data" / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "inference"))
sys.path.insert(0, str(PROJECT_ROOT / "evaluation"))


@pytest.fixture
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def sample_nl2py_record():
    return {
        "nl_query": "Write a function that adds two numbers",
        "python_code": "def add(a, b):\n    return a + b",
        "source": "synthetic",
    }


@pytest.fixture
def sample_java2py_record():
    return {
        "java_code": 'System.out.println("Hello");',
        "python_code": 'print("Hello")',
        "source": "synthetic",
    }
