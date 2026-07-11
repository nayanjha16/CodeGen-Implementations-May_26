"""API schema / routing tests without loading the CodeGen model."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from hf_deploy import CLARIFY_INTENT
import hf_deploy.api.app as api_app_module
from hf_deploy.classifier import ClassificationResult, IntentClassifier


@pytest.fixture
def client() -> TestClient:
    router = MagicMock()
    router.checkpoint_version = "v3"
    router.status.return_value = {
        "loaded": True,
        "base_model": "Salesforce/codegen-350M-multi",
        "checkpoint_version": "v3",
        "device": "cpu",
        "adapters": {},
    }
    router.generate.return_value = "SELECT 1;"

    classifier = IntentClassifier(use_embeddings=False, prefer_rules=True)

    # Pre-inject so lifespan skips real model load.
    api_app_module._manifest = {"checkpoint_version": "v3"}
    api_app_module._router = router
    api_app_module._classifier = classifier

    with TestClient(api_app_module.app) as test_client:
        yield test_client

    api_app_module._router = None
    api_app_module._classifier = None
    api_app_module._manifest = {}


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_models(client: TestClient) -> None:
    response = client.get("/v1/models")
    assert response.status_code == 200
    ids = {m["id"] for m in response.json()["data"]}
    assert "codegen-multi-adapter" in ids
    assert "codegen-text2sql" in ids


def test_chat_routes_text2sql(client: TestClient) -> None:
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "codegen-multi-adapter",
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Write a SQL query to list customers.\n\n"
                        "Schema:\ncustomers(id, name)\n\nSQL:"
                    ),
                }
            ],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["choices"][0]["message"]["content"] == "SELECT 1;"
    assert payload["codegen_routing"]["intent"] == "text2sql"
    assert payload["model"] == "codegen-text2sql"


def test_chat_clarifies_ambiguous(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def clarify(_text: str) -> ClassificationResult:
        return ClassificationResult(
            intent=CLARIFY_INTENT,
            confidence=0.1,
            method="embedding",
            scores={"text2sql": 0.1, "sql2nosql": 0.1, "nosql2doc": 0.1},
        )

    monkeypatch.setattr(api_app_module._classifier, "classify", clarify)
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "codegen-multi-adapter",
            "messages": [{"role": "user", "content": "do something useful"}],
        },
    )
    assert response.status_code == 200
    assert (
        "could not determine"
        in response.json()["choices"][0]["message"]["content"].lower()
    )


def test_intent_override(client: TestClient) -> None:
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "codegen-multi-adapter",
            "intent": "sql2nosql",
            "messages": [
                {
                    "role": "user",
                    "content": "SELECT 1;\n\nSchema:\nt(a)\n\nMongoDB:",
                }
            ],
        },
    )
    assert response.status_code == 200
    assert response.json()["codegen_routing"]["method"] == "override"
    assert response.json()["codegen_routing"]["intent"] == "sql2nosql"
