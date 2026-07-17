"""Tests for data preprocessing and prompt templates."""

import subprocess
import sys
from pathlib import Path

import pytest
from datasets import Dataset, load_from_disk

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "data" / "scripts"


class TestPromptTemplates:
    def test_format_nl2py(self):
        from prompt_templates import format_nl2py, NL2PY_TEMPLATE
        result = format_nl2py("sort a list", "sorted(lst)")
        assert "sort a list" in result
        assert "sorted(lst)" in result
        assert "### Instruction" in result
        assert "### Response" in result

    def test_format_java2py(self):
        from prompt_templates import format_java2py
        result = format_java2py("int x = 1;", "x = 1")
        assert "```java" in result
        assert "```python" in result
        assert "int x = 1;" in result
        assert "x = 1" in result

    def test_nl2py_inference_prefix(self):
        from prompt_templates import format_nl2py_inference
        result = format_nl2py_inference("reverse a string")
        assert "reverse a string" in result
        assert "### Response" in result

    def test_java2py_inference_prefix(self):
        from prompt_templates import format_java2py_inference
        result = format_java2py_inference("public class Foo {}")
        assert "public class Foo" in result
        assert "```python" in result

    def test_format_code2doc(self):
        from prompt_templates import format_code2doc, format_code2doc_inference
        result = format_code2doc("def foo(): pass", "Does nothing.")
        assert "def foo" in result
        assert "Does nothing" in result
        assert "### Documentation" in result
        inf = format_code2doc_inference("def foo(): pass")
        assert "def foo" in inf
        assert "### Documentation" in inf

    def test_format_comment(self):
        from prompt_templates import format_comment, format_comment_inference
        result = format_comment("x = 1", "x = 1  # one")
        assert "x = 1" in result
        assert "# one" in result
        inf = format_comment_inference("x = 1")
        assert "x = 1" in inf
        assert "Commented code" in inf


class TestPreprocessMultitask:
    def test_build_dataset(self):
        sys.path.insert(0, str(SCRIPTS_DIR))
        import preprocess_multitask as mod

        records = mod._synthetic_fallback()
        train_ds, val_ds = mod.build_dataset(records, val_ratio=0.25)
        assert len(train_ds) >= 1
        assert {"text", "task", "source"}.issubset(set(train_ds.column_names))
        all_tasks = set(train_ds["task"]) | set(val_ds["task"])
        assert all_tasks == {"java2py", "nl2py", "code2doc", "comments"}

    def test_strip_comments(self):
        sys.path.insert(0, str(SCRIPTS_DIR))
        import preprocess_multitask as mod

        code = 'def foo():\n    """doc"""\n    x = 1  # inline\n    return x'
        stripped = mod._strip_comments_and_docstrings(code)
        assert '"""' not in stripped
        assert "#" not in stripped
        assert "return x" in stripped


class TestPreprocessNL2Py:
    def test_preprocess_creates_dataset(self, tmp_path, monkeypatch):
        processed = tmp_path / "processed" / "nl2py"
        monkeypatch.setattr(
            "preprocess_nl2py.PROCESSED_DIR",
            tmp_path / "processed",
        )
        sys.path.insert(0, str(SCRIPTS_DIR))
        import preprocess_nl2py as mod

        records = [
            {"nl_query": "add numbers", "python_code": "def add(a,b): return a+b", "source": "test"},
            {"nl_query": "multiply", "python_code": "def mul(a,b): return a*b", "source": "test"},
            {"nl_query": "subtract", "python_code": "def sub(a,b): return a-b", "source": "test"},
        ]
        train_ds, val_ds = mod.build_dataset(records, val_ratio=0.33)

        assert isinstance(train_ds, Dataset)
        assert isinstance(val_ds, Dataset)
        assert len(train_ds) >= 1
        assert "text" in train_ds.column_names
        assert "nl_query" in train_ds.column_names
        assert "python_code" in train_ds.column_names
        assert all(t.strip() for t in train_ds["text"])

    def test_no_empty_samples(self):
        sys.path.insert(0, str(SCRIPTS_DIR))
        import preprocess_nl2py as mod
        records = [
            {"nl_query": "test query", "python_code": "pass", "source": "test"},
        ]
        train_ds, _ = mod.build_dataset(records)
        for i in range(len(train_ds)):
            assert train_ds[i]["nl_query"].strip()
            assert train_ds[i]["python_code"].strip()
            assert train_ds[i]["text"].strip()

    def test_load_mbpp_maps_text_and_code(self, monkeypatch):
        sys.path.insert(0, str(SCRIPTS_DIR))
        import preprocess_nl2py as mod

        class FakeSplit:
            def __init__(self, rows):
                self._rows = rows

            def __iter__(self):
                return iter(self._rows)

        fake_ds = {
            "train": FakeSplit([
                {
                    "text": "Write a function to add two numbers.",
                    "code": "def add(a, b):\n    return a + b",
                    "test_setup_code": "",
                }
            ]),
            "validation": FakeSplit([]),
        }

        def fake_load_dataset(name, config):
            assert name == "google-research-datasets/mbpp"
            assert config == "full"
            return fake_ds

        monkeypatch.setattr(mod, "load_dataset", fake_load_dataset, raising=False)
        import datasets

        monkeypatch.setattr(datasets, "load_dataset", fake_load_dataset)

        records = mod.load_mbpp()
        assert len(records) == 1
        assert records[0]["source"] == "mbpp"
        assert "add two numbers" in records[0]["nl_query"]
        assert "def add" in records[0]["python_code"]


class TestPreprocessJava2Py:
    def test_preprocess_creates_dataset(self):
        sys.path.insert(0, str(SCRIPTS_DIR))
        import preprocess_java2py as mod

        records = [
            {"java_code": "int a = 1;", "python_code": "a = 1", "source": "test"},
            {"java_code": "return 0;", "python_code": "return 0", "source": "test"},
            {"java_code": "System.out.println(1);", "python_code": "print(1)", "source": "test"},
        ]
        train_ds, val_ds = mod.build_dataset(records, val_ratio=0.33)

        assert isinstance(train_ds, Dataset)
        assert "text" in train_ds.column_names
        assert "java_code" in train_ds.column_names
        assert "python_code" in train_ds.column_names
        assert all("```java" in t for t in train_ds["text"])

    def test_java_heuristic(self):
        sys.path.insert(0, str(SCRIPTS_DIR))
        import preprocess_java2py as mod
        java = 'System.out.println("hi");'
        result = mod._java_to_python_heuristic(java)
        assert result is not None
        assert "print" in result


class TestProcessedDatasetsOnDisk:
    """Integration tests requiring preprocessed data."""

    @pytest.fixture(autouse=True)
    def ensure_processed(self):
        nl2py_val = PROJECT_ROOT / "data" / "processed" / "nl2py" / "val"
        java2py_val = PROJECT_ROOT / "data" / "processed" / "java2py" / "val"
        if not nl2py_val.exists() or not java2py_val.exists():
            subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "preprocess_nl2py.py"), "--skip-hf"],
                check=True,
                cwd=str(PROJECT_ROOT),
            )
            subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "preprocess_java2py.py"), "--skip-hf"],
                check=True,
                cwd=str(PROJECT_ROOT),
            )

    def test_nl2py_schema(self):
        ds = load_from_disk(str(PROJECT_ROOT / "data" / "processed" / "nl2py" / "val"))
        required = {"text", "nl_query", "python_code", "source"}
        assert required.issubset(set(ds.column_names))
        for i in range(len(ds)):
            assert ds[i]["text"].strip()
            assert ds[i]["nl_query"].strip()
            assert ds[i]["python_code"].strip()

    def test_java2py_schema(self):
        ds = load_from_disk(str(PROJECT_ROOT / "data" / "processed" / "java2py" / "val"))
        required = {"text", "java_code", "python_code", "source"}
        assert required.issubset(set(ds.column_names))
        for i in range(len(ds)):
            assert ds[i]["text"].strip()
            assert ds[i]["java_code"].strip()
            assert ds[i]["python_code"].strip()
