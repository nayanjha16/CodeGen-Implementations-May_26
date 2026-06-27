"""Tests for judge backend resolution and Ollama availability checks."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from src.llm.judge_backend import (
    HfJudgeBackend,
    OllamaJudgeBackend,
    create_judge_backend,
    resolve_hf_judge_model,
)
from src.llm.ollama_client import OllamaClient


class ResolveHfJudgeModelTest(unittest.TestCase):
    def test_maps_gemma3_tag(self) -> None:
        self.assertEqual(
            resolve_hf_judge_model("gemma3:4b"),
            "google/gemma-3-4b-it",
        )

    def test_explicit_hf_override(self) -> None:
        self.assertEqual(
            resolve_hf_judge_model("gemma3:4b", "google/custom-gemma"),
            "google/custom-gemma",
        )

    def test_accepts_hf_model_id_directly(self) -> None:
        self.assertEqual(
            resolve_hf_judge_model("google/gemma-3-4b-it"),
            "google/gemma-3-4b-it",
        )


class OllamaClientModelLookupTest(unittest.TestCase):
    def test_has_model_matches_tag_prefix(self) -> None:
        client = OllamaClient()
        with patch.object(client, "list_model_names", return_value=["gemma3:4b"]):
            self.assertTrue(client.has_model("gemma3:4b"))
            self.assertTrue(client.has_model("gemma3:latest"))

    def test_has_model_false_when_missing(self) -> None:
        client = OllamaClient()
        with patch.object(client, "list_model_names", return_value=["qwen3:4b"]):
            self.assertFalse(client.has_model("gemma3:4b"))


class CreateJudgeBackendTest(unittest.TestCase):
    def test_prefers_ollama_when_model_available(self) -> None:
        client = MagicMock()
        client.is_available.return_value = True
        client.has_model.return_value = True

        backend = create_judge_backend("gemma3:4b", ollama_client=client)

        self.assertIsInstance(backend, OllamaJudgeBackend)
        self.assertEqual(backend.backend_name, "ollama")

    def test_falls_back_to_huggingface_when_ollama_unavailable(self) -> None:
        client = MagicMock()
        client.is_available.return_value = False
        client.base_url = "http://localhost:11434"

        with patch(
            "src.llm.judge_backend.HfJudgeBackend",
            return_value=MagicMock(spec=HfJudgeBackend),
        ) as hf_backend_cls:
            backend = create_judge_backend("gemma3:4b", ollama_client=client)

        hf_backend_cls.assert_called_once_with(
            "google/gemma-3-4b-it",
            device="auto",
        )
        self.assertIsNotNone(backend)


if __name__ == "__main__":
    unittest.main()
