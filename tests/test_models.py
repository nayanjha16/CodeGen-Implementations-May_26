"""Tests for model loader."""

from src.models.model_loader import CodeGenModel, load_model


class TestModelLoader:
    def test_resolve_device_cpu(self):
        model = CodeGenModel(device="cpu")
        assert model.device == "cpu"

    def test_load_model_factory(self):
        model = load_model(device="cpu", eager=False)
        assert model.model_name == "Salesforce/codegen-350M-multi"
        assert model._loaded is False

    def test_model_not_loaded_initially(self):
        model = CodeGenModel(device="cpu")
        assert model._loaded is False
