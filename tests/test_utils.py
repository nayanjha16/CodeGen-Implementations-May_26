"""Tests for utility modules."""

from pathlib import Path

from src.utils.config import get_bertscore_model_name, get_model_name, load_config
from src.utils.logging import setup_logging
from src.utils.paths import get_bird_data_dir, get_model_cache_dir, get_spider_data_dir
from src.utils.seeds import set_seeds


class TestConfig:
    def test_load_config(self):
        config = load_config()
        assert "model" in config
        assert config["model"]["name"] == get_model_name(config)
        assert config["evaluation"]["bertscore_model"] == get_bertscore_model_name(config)
        assert config["model"]["base_dir"].endswith("models/base")
        assert config["model"]["checkpoints_dir"].endswith("models/checkpoints")

    def test_load_config_custom_path(self):
        root = Path(__file__).resolve().parents[1]
        config = load_config(root / "configs" / "default.yaml")
        assert "seeds" in config
        assert config["datasets"]["spider"]["cache_dir"] == "data/spider"
        assert config["datasets"]["bird"]["cache_dir"] == "data/bird"
        assert config["datasets"]["spider"]["repo_url"] == "https://example.com/spider.zip"
        assert config["datasets"]["bird"]["dataset_url"] == "https://example.com/bird.zip"

    def test_get_project_root(self):
        from src.utils.paths import get_project_root

        root = get_project_root()
        assert (root / "src").exists()


class TestPaths:
    def test_model_cache_dir(self):
        path = get_model_cache_dir("org/model-name")
        assert path.name == "org__model-name"
        assert "models/base" in str(path)

    def test_dataset_dirs(self):
        assert get_spider_data_dir().name == "spider"
        assert get_bird_data_dir().name == "bird"


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
