"""Tests for utility modules."""

from pathlib import Path

from src.utils.config import get_project_root, load_config
from src.utils.logging import setup_logging
from src.utils.seeds import set_seeds


class TestConfig:
    def test_load_config(self):
        config = load_config()
        assert "model" in config
        assert config["model"]["name"] == "Salesforce/codegen-350M-multi"

    def test_load_config_custom_path(self):
        root = get_project_root()
        config = load_config(root / "configs" / "default.yaml")
        assert "seeds" in config

    def test_get_project_root(self):
        root = get_project_root()
        assert (root / "src").exists()


class TestSeeds:
    def test_set_seeds(self):
        set_seeds(seeds={"random": 1, "numpy": 1, "torch": 1})

    def test_set_seeds_from_config(self):
        config = load_config()
        set_seeds(config)


class TestLogging:
    def test_setup_logging(self):
        logger = setup_logging()
        assert logger.name == "codegen"
        logger.info("test message")
