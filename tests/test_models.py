"""Tests for model loader."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.models.model_loader import (
    CodeGenModel,
    ensure_model_cached,
    is_model_cached,
    load_model,
    resolve_model_path,
)
from src.utils.config import get_model_name, load_config


class TestModelLoader:
    def test_resolve_device_cpu(self):
        model = CodeGenModel(model_name="test/mock", device="cpu")
        assert model.device == "cpu"

    def test_load_model_factory(self):
        config = load_config()
        model = load_model(config=config, device="cpu", eager=False)
        assert model.model_name == get_model_name(config)
        assert model._loaded is False

    def test_model_not_loaded_initially(self):
        model = CodeGenModel(model_name="test/mock", device="cpu")
        assert model._loaded is False

    def test_is_model_cached(self, tmp_path):
        assert not is_model_cached(tmp_path)
        (tmp_path / "config.json").write_text("{}", encoding="utf-8")
        assert not is_model_cached(tmp_path)
        (tmp_path / ".downloaded").touch()
        assert not is_model_cached(tmp_path)
        (tmp_path / "model.safetensors").write_bytes(b"")
        assert is_model_cached(tmp_path)

    def test_ensure_model_cached_downloads_once(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MODELS_BASE_DIR", str(tmp_path / "models" / "base"))
        cache_dir = tmp_path / "models" / "base" / "test__mock"
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()

        with patch("transformers.AutoTokenizer") as mock_tokenizer_cls, patch(
            "transformers.AutoModelForCausalLM"
        ) as mock_model_cls:
            mock_tokenizer_cls.from_pretrained.return_value = mock_tokenizer
            mock_model_cls.from_pretrained.return_value = mock_model

            first = ensure_model_cached("test/mock", cache_dir)
            second = ensure_model_cached("test/mock", cache_dir)

        assert first == cache_dir
        assert second == cache_dir
        mock_tokenizer_cls.from_pretrained.assert_called_once_with("test/mock")
        mock_model_cls.from_pretrained.assert_called_once_with("test/mock")
        mock_tokenizer.save_pretrained.assert_called_once_with(cache_dir)
        mock_model.save_pretrained.assert_called_once_with(cache_dir)
        assert (cache_dir / ".downloaded").exists()

    def test_resolve_model_path_uses_checkpoint(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MODELS_CHECKPOINTS_DIR", str(tmp_path / "models" / "checkpoints"))
        checkpoint_dir = tmp_path / "models" / "checkpoints" / "run-1"
        checkpoint_dir.mkdir(parents=True)
        (checkpoint_dir / "config.json").write_text("{}", encoding="utf-8")

        config = load_config()
        config["model"]["checkpoint"] = "run-1"
        path = resolve_model_path(config)
        assert path == checkpoint_dir

    def test_resolve_model_path_requires_checkpoint_exists(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MODELS_CHECKPOINTS_DIR", str(tmp_path / "models" / "checkpoints"))
        config = load_config()
        config["model"]["checkpoint"] = "missing-run"
        with pytest.raises(FileNotFoundError):
            resolve_model_path(config)
