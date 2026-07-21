"""Thin HTTP client for the FastAPI backend, used by the Streamlit app.

Kept separate from the Streamlit UI code so it's testable with plain
``unittest.mock`` — no Streamlit runtime needed to verify request/response
handling and error surfacing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class APIClientError(RuntimeError):
    """Raised when the backend returns a non-2xx response or is unreachable."""


@dataclass
class APIClient:
    base_url: str = "http://localhost:8000"
    timeout_seconds: float = 60.0

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}{path}"
        try:
            response = requests.post(url, json=payload, timeout=self.timeout_seconds)
        except requests.RequestException as exc:
            raise APIClientError(f"Could not reach backend at {url}: {exc}") from exc

        if response.status_code >= 400:
            detail = _extract_detail(response)
            raise APIClientError(f"{path} returned {response.status_code}: {detail}")
        return response.json()

    def health(self) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/health"
        try:
            response = requests.get(url, timeout=self.timeout_seconds)
        except requests.RequestException as exc:
            raise APIClientError(f"Could not reach backend at {url}: {exc}") from exc
        if response.status_code >= 400:
            raise APIClientError(f"/health returned {response.status_code}")
        return response.json()

    def generate(self, problem_description: str, language: str = "python") -> dict[str, Any]:
        return self._post("/generate", {"problem_description": problem_description, "language": language})

    def document(self, code: str, language: str = "python") -> dict[str, Any]:
        return self._post("/document", {"code": code, "language": language})

    def translate(
        self, source_code: str, source_language: str = "python", target_language: str = "java"
    ) -> dict[str, Any]:
        return self._post(
            "/translate",
            {
                "source_code": source_code,
                "source_language": source_language,
                "target_language": target_language,
            },
        )

    def sql(self, question: str, db_id: str) -> dict[str, Any]:
        return self._post("/sql", {"question": question, "db_id": db_id})

    def rag(
        self,
        query: str,
        task: str = "program_synthesis",
        top_k: int = 5,
        strategy: str = "hybrid",
        use_llm: bool = False,
    ) -> dict[str, Any]:
        return self._post(
            "/rag",
            {"query": query, "task": task, "top_k": top_k, "strategy": strategy, "use_llm": use_llm},
        )


def _extract_detail(response: requests.Response) -> str:
    try:
        body = response.json()
        return str(body.get("detail", body))
    except ValueError:
        return response.text
