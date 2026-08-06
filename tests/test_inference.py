"""Tests for inference generator and API."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "inference"))
sys.path.insert(0, str(PROJECT_ROOT / "data" / "scripts"))


class TestCodeGenerator:
    def test_extract_code_from_markdown(self):
        from generator import CodeGenerator
        text = '```python\ndef foo():\n    pass\n```'
        result = CodeGenerator._extract_code(text)
        assert "def foo" in result
        assert "```" not in result

    def test_extract_code_raw(self):
        from generator import CodeGenerator
        text = "def add(a, b):\n    return a + b"
        result = CodeGenerator._extract_code(text)
        assert result == text

    def test_extract_documentation(self):
        from generator import CodeGenerator
        text = "Returns the sum of two numbers.\n```"
        result = CodeGenerator._extract_documentation(text)
        assert "sum" in result
        assert "```" not in result

    def test_resolve_multitask_path(self, tmp_path):
        from generator import _resolve_model_path, MULTITASK_MODEL_DIR

        merged = tmp_path / MULTITASK_MODEL_DIR / "merged"
        merged.mkdir(parents=True)
        (merged / "config.json").write_text("{}")
        path, base = _resolve_model_path("nl2py", tmp_path)
        assert path == merged
        assert base is None

    def test_resolve_codegen_model_id_prefers_local_merged(self, tmp_path):
        from generator import MULTITASK_MODEL_DIR, resolve_codegen_model_id

        merged = tmp_path / MULTITASK_MODEL_DIR / "merged"
        merged.mkdir(parents=True)
        with patch.dict("os.environ", {}, clear=False):
            os.environ.pop("MODEL_ID", None)
            resolved = resolve_codegen_model_id(models_dir=tmp_path)
        assert resolved == str(merged.resolve())

    def test_resolve_codegen_model_id_hub_fallback(self, tmp_path):
        from generator import HF_FT_MODEL, resolve_codegen_model_id

        with patch.dict("os.environ", {}, clear=False):
            os.environ.pop("MODEL_ID", None)
            resolved = resolve_codegen_model_id(models_dir=tmp_path)
        assert resolved == HF_FT_MODEL
        assert "Qwen2.5-Coder" not in resolved

    @patch.dict("os.environ", {"MODEL_ID": "user/qwen-multitask"})
    @patch("generator.CodeGenerator")
    def test_load_generator_uses_model_id_env(self, mock_gen_cls, tmp_path):
        from generator import load_generator

        load_generator("nl2py", models_dir=tmp_path)
        mock_gen_cls.assert_called_once_with(model_path="user/qwen-multitask")

    @patch("generator.CodeGenerator")
    def test_load_generator_falls_back_to_hub_ft(self, mock_gen_cls, tmp_path):
        from generator import HF_FT_MODEL, load_generator

        with patch.dict("os.environ", {}, clear=False):
            os.environ.pop("MODEL_ID", None)
            load_generator("nl2py", models_dir=tmp_path)
        mock_gen_cls.assert_called_once_with(model_path=HF_FT_MODEL)

    @patch("generator.AutoModelForCausalLM")
    @patch("generator.AutoTokenizer")
    def test_generate_returns_string(self, mock_tokenizer_cls, mock_model_cls):
        from generator import CodeGenerator

        mock_tokenizer = MagicMock()
        mock_tokenizer.pad_token = None
        mock_tokenizer.eos_token_id = 0
        mock_tokenizer.pad_token_id = 0
        mock_tokenizer.decode.return_value = "def add(a, b):\n    return a + b"
        mock_tokenizer.return_value = {"input_ids": MagicMock()}
        mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer

        mock_model = MagicMock()
        mock_model.generate.return_value = MagicMock()
        mock_model_cls.from_pretrained.return_value = mock_model

        gen = CodeGenerator(model_path="test-model", device="cpu")
        result = gen.generate("### Instruction: add two numbers\n### Response:\n")
        assert isinstance(result, str)
        assert len(result) > 0


class TestRAGPipeline:
    def test_build_prompt_nl2py_no_index(self):
        from rag_pipeline import RAGPipeline
        with patch.object(RAGPipeline, "__init__", lambda self, **kw: None):
            rag = RAGPipeline.__new__(RAGPipeline)
            rag.task = "nl2py"
            rag.top_k = 3
            rag.index = None
            rag.examples = []
            rag.retrieve = lambda q: []

        from prompt_templates import format_nl2py_inference
        prompt = format_nl2py_inference("sort a list")
        assert "sort a list" in prompt

    def test_build_prompt_java2py_no_index(self):
        from prompt_templates import format_java2py_inference
        prompt = format_java2py_inference("int x = 1;")
        assert "int x = 1" in prompt
        assert "```python" in prompt

    def test_format_nl2java_inference(self):
        from prompt_templates import format_nl2java_inference
        prompt = format_nl2java_inference("check if a string is a palindrome")
        assert "Write Java for: check if a string is a palindrome" in prompt
        assert "```java" in prompt


class TestAPI:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        with patch("api.load_generator") as mock_load, \
             patch("api.RAGPipeline") as mock_rag:
            mock_gen = MagicMock()
            mock_gen.generate.return_value = "def add(a, b):\n    return a + b"
            mock_gen.model_path = "models/qwen_multitask/merged"
            mock_load.return_value = mock_gen
            mock_rag.return_value.build_prompt.return_value = "prompt"

            from api import app, _generators, _rag_pipelines
            import api as api_module

            for task in ("nl2py", "java2py", "code2doc", "comments", "nl2java2py"):
                _generators[task] = mock_gen
            api_module._generator = mock_gen
            api_module._model_path = "models/qwen_multitask/merged"
            _rag_pipelines["nl2py"] = mock_rag.return_value
            _rag_pipelines["java2py"] = mock_rag.return_value

            with TestClient(app, raise_server_exceptions=False) as c:
                yield c

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["shared_generator"] is True
        assert "model_path" in data
        assert "nl2java2py" in data["models_loaded"]

    def test_nl2py_endpoint(self, client):
        resp = client.post("/nl2py", json={"query": "add two numbers", "use_rag": False})
        assert resp.status_code == 200
        data = resp.json()
        assert data["task"] == "nl2py"
        assert "code" in data
        assert len(data["code"]) > 0

    def test_java2py_endpoint(self, client):
        resp = client.post(
            "/java2py",
            json={"java_code": "System.out.println(1);", "use_rag": False},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["task"] == "java2py"
        assert "code" in data

    def test_code2doc_endpoint(self, client):
        resp = client.post(
            "/code2doc",
            json={"python_code": "def add(a, b):\n    return a + b"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["task"] == "code2doc"
        assert "documentation" in data

    def test_comments_endpoint(self, client):
        resp = client.post(
            "/comments",
            json={"python_code": "def add(a, b):\n    return a + b"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["task"] == "comments"
        assert "code" in data

    def test_nl2java2py_pipeline(self, client):
        import api as api_module

        java_out = "public boolean isPalindrome(String s) { return true; }"
        python_out = "def is_palindrome(s):\n    return True"
        api_module._generators["nl2java2py"].generate.side_effect = [java_out, python_out]

        resp = client.post(
            "/nl2java2py",
            json={"prompt": "Write a function that checks if a string is a palindrome"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["task"] == "nl2java2py"
        assert data["java_code"] == java_out
        assert data["python_code"] == python_out
        assert "palindrome" in data["prompt"]
        assert api_module._generators["nl2java2py"].generate.call_count == 2

    def test_nl2java2py_empty_prompt(self, client):
        resp = client.post("/nl2java2py", json={"prompt": "   "})
        assert resp.status_code == 400
