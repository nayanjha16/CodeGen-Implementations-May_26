from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from codegen_rag.api.dependencies import AppState, get_app_state
from codegen_rag.api.main import create_app
from codegen_rag.config import load_settings
from codegen_rag.rag.ast_retrieval import ASTRetrievalIndex
from codegen_rag.rag.faiss_index import CodeSearchIndex
from codegen_rag.sql.schema import introspect_sqlite_schema


class FakeAPIModel:
    """Fake CodeGenModel: deterministic text generation + embeddings, no torch."""

    def generate(self, prompt: str, gen_config=None) -> list[str]:  # noqa: ANN001
        if "SQL" in prompt or "Question" in prompt:
            return ["SELECT COUNT(*) FROM singer;"]
        return ["def solution():\n    return 42"]

    def embed(self, texts: list[str], normalize: bool = True):
        class _T:
            def numpy(self_inner):
                return np.ones((len(texts), 8), dtype="float32")

        return _T()


@pytest.fixture
def concert_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "concert_singer.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE singer (Singer_ID INTEGER PRIMARY KEY, Name TEXT)")
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def populated_state(concert_db: Path) -> AppState:
    state = AppState()
    state.settings = load_settings()
    state.model = FakeAPIModel()

    dim = 8
    embeddings = np.ones((5, dim), dtype="float32")
    codes = ["def add(a, b):\n    return a + b"] * 5
    metadata = [{"code": codes[i], "chunk_id": i} for i in range(5)]

    dense = CodeSearchIndex(dim=dim, use_ivf=False)
    dense.build(embeddings, metadata)
    ast_index = ASTRetrievalIndex()
    ast_index.build(codes, [{"code": codes[i], "chunk_id": i} for i in range(5)])

    state.dense_index = dense
    state.ast_index = ast_index
    state.schema_cache["concert_singer"] = introspect_sqlite_schema(concert_db, db_id="concert_singer")
    return state


@pytest.fixture
def client(populated_state: AppState) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_app_state] = lambda: populated_state
    return TestClient(app)


def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "base_model" in body


def test_generate_endpoint_returns_code(client: TestClient):
    response = client.post("/generate", json={"problem_description": "add two numbers", "language": "python"})
    assert response.status_code == 200
    body = response.json()
    assert "def solution" in body["code"]
    assert body["language"] == "python"


def test_generate_endpoint_rejects_empty_description(client: TestClient):
    response = client.post("/generate", json={"problem_description": ""})
    assert response.status_code == 422  # pydantic min_length validation


def test_document_endpoint_returns_docstring(client: TestClient):
    response = client.post("/document", json={"code": "def add(a, b):\n    return a + b"})
    assert response.status_code == 200
    assert "docstring" in response.json()


def test_translate_endpoint_returns_translated_code(client: TestClient):
    response = client.post(
        "/translate",
        json={"source_code": "def add(a, b):\n    return a + b", "source_language": "python", "target_language": "java"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "def solution" in body["translated_code"]
    assert body["source_language"] == "python"
    assert body["target_language"] == "java"


def test_translate_endpoint_rejects_empty_source(client: TestClient):
    response = client.post("/translate", json={"source_code": ""})
    assert response.status_code == 422  # pydantic min_length validation


def test_sql_endpoint_returns_query_for_known_db(client: TestClient):
    response = client.post("/sql", json={"question": "How many singers?", "db_id": "concert_singer"})
    assert response.status_code == 200
    body = response.json()
    assert body["sql"].strip().upper().startswith("SELECT")
    assert body["db_id"] == "concert_singer"


def test_sql_endpoint_404_for_unknown_db(client: TestClient, populated_state: AppState):
    # Point settings at a nonexistent databases dir so the fallback file search finds nothing.
    response = client.post("/sql", json={"question": "How many?", "db_id": "totally_unknown_db"})
    assert response.status_code == 404


def test_rag_endpoint_dense_strategy(client: TestClient):
    response = client.post("/rag", json={"query": "add two numbers", "strategy": "dense", "top_k": 3})
    assert response.status_code == 200
    body = response.json()
    assert body["retrieved_count"] == 3
    assert body["strategy"] == "dense"
    assert body["used_llm"] is False


def test_rag_endpoint_hybrid_strategy(client: TestClient):
    response = client.post("/rag", json={"query": "add two numbers", "strategy": "hybrid", "top_k": 2})
    assert response.status_code == 200
    assert response.json()["strategy"] == "hybrid"


def test_rag_endpoint_llm_unavailable_returns_503(client: TestClient, populated_state: AppState, monkeypatch):
    from codegen_rag.models.model_registry import LLMUnavailableError, UpperBoundLLMClient

    def always_fail(self, prompt, system="x"):
        raise LLMUnavailableError("no api key configured")

    monkeypatch.setattr(UpperBoundLLMClient, "generate", always_fail)
    response = client.post("/rag", json={"query": "add two numbers", "use_llm": True})
    assert response.status_code == 503


def test_openapi_docs_available(client: TestClient):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "/generate" in schema["paths"]
    assert "/document" in schema["paths"]
    assert "/translate" in schema["paths"]
    assert "/sql" in schema["paths"]
    assert "/rag" in schema["paths"]
