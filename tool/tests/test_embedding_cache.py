"""Tests for local Hugging Face embedding model cache."""

from pathlib import Path

import pytest

from tool.core import embedding_cache


def test_model_slug():
    assert embedding_cache.model_slug("BAAI/bge-small-en-v1.5") == "BAAI__bge-small-en-v1.5"


def test_is_embedding_model_cached_false_when_missing(tmp_path: Path):
    cache_dir = tmp_path / "models"
    cache_dir.mkdir()
    monkeypatched = tmp_path / "models" / "BAAI__bge-small-en-v1.5"
    monkeypatched.mkdir()

    original = embedding_cache.get_embedding_cache_dir
    embedding_cache.get_embedding_cache_dir = lambda: cache_dir
    try:
        assert embedding_cache.is_embedding_model_cached("BAAI/bge-small-en-v1.5") is False
    finally:
        embedding_cache.get_embedding_cache_dir = original


def test_is_embedding_model_cached_true_with_snapshot(tmp_path: Path):
    cache_dir = tmp_path / "models" / "BAAI__bge-small-en-v1.5"
    cache_dir.mkdir(parents=True)
    (cache_dir / "config.json").write_text("{}")
    (cache_dir / "modules.json").write_text("[]")
    (cache_dir / "model.safetensors").write_bytes(b"weights")

    original = embedding_cache.get_embedding_cache_dir
    embedding_cache.get_embedding_cache_dir = lambda: tmp_path / "models"
    try:
        assert embedding_cache.is_embedding_model_cached("BAAI/bge-small-en-v1.5") is True
    finally:
        embedding_cache.get_embedding_cache_dir = original


def test_load_sentence_model_uses_local_cache(monkeypatch, tmp_path: Path):
    cache_dir = tmp_path / "models" / "demo__model"
    cache_dir.mkdir(parents=True)
    (cache_dir / "config.json").write_text("{}")
    (cache_dir / "modules.json").write_text("[]")
    (cache_dir / "model.safetensors").write_bytes(b"weights")

    calls: list[tuple[str, bool]] = []

    class FakeModel:
        def encode(self, texts, normalize_embeddings=True, show_progress_bar=False):
            return [[1.0, 0.0] for _ in texts]

    def fake_sentence_transformer(path, local_files_only=False):
        calls.append((path, local_files_only))
        return FakeModel()

    monkeypatch.setattr(embedding_cache, "get_embedding_cache_dir", lambda: tmp_path / "models")
    monkeypatch.setattr(embedding_cache, "is_embedding_model_cached", lambda _name: True)
    monkeypatch.setattr(
        "sentence_transformers.SentenceTransformer",
        fake_sentence_transformer,
        raising=False,
    )
    embedding_cache.load_sentence_model.cache_clear()

    model = embedding_cache.load_sentence_model("demo/model")
    assert model.encode(["hello"]) == [[1.0, 0.0]]
    assert calls == [(str(cache_dir), True)]


def test_ensure_embedding_model_cached_downloads_once(monkeypatch, tmp_path: Path):
    cache_dir = tmp_path / "models" / "demo__model"
    saved_paths: list[str] = []

    class FakeModel:
        def save(self, path: str) -> None:
            saved_paths.append(path)
            Path(path).mkdir(parents=True, exist_ok=True)
            (Path(path) / "config.json").write_text("{}")
            (Path(path) / "modules.json").write_text("[]")
            (Path(path) / "model.safetensors").write_bytes(b"weights")

    monkeypatch.setattr(embedding_cache, "get_embedding_cache_dir", lambda: tmp_path / "models")
    monkeypatch.setattr(
        "sentence_transformers.SentenceTransformer",
        lambda _name: FakeModel(),
        raising=False,
    )
    embedding_cache.load_sentence_model.cache_clear()

    first = embedding_cache.ensure_embedding_model_cached("demo/model")
    second = embedding_cache.ensure_embedding_model_cached("demo/model")

    assert first == cache_dir
    assert second == cache_dir
    assert saved_paths == [str(cache_dir)]
    assert (cache_dir / ".downloaded").is_file()
