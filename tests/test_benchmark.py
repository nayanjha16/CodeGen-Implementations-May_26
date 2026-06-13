"""Tests for benchmark runner."""

from unittest.mock import MagicMock, patch

from src.evaluation.benchmark import BenchmarkRunner
from src.text2sql.sql_generator import SQLGenerator


class TestBenchmarkRunner:
    def test_run_on_dataset_with_mock(self, sample_examples, mock_model, tmp_path):
        generator = SQLGenerator(model=mock_model)
        runner = BenchmarkRunner(
            config={
                "model": {"name": "mock"},
                "generation": {"decoding_strategy": "greedy"},
                "evaluation": {
                    "max_samples": 2,
                    "experiment_name": "test",
                    "mlflow_tracking_uri": f"sqlite:///{(tmp_path / 'mlflow.db').resolve().as_posix()}",
                },
                "seeds": {"random": 42, "numpy": 42, "torch": 42},
            },
            sql_generator=generator,
        )
        result = runner.run_on_dataset(sample_examples, "test_dataset")
        assert result["dataset"] == "test_dataset"
        assert "metrics" in result
        assert "nosql_metrics" in result
        assert len(result["predictions"]) == 2
        assert len(result["nosql_predictions"]) == 2

    @patch("src.datasets.spider_loader.SpiderLoader.load_split")
    def test_run_spider(self, mock_load, mock_model, tmp_path):
        mock_load.return_value = [
            {
                "question": "List students",
                "schema": "Table students(id, name)",
                "sql": "SELECT * FROM students",
                "db_id": "students",
            }
        ]
        generator = SQLGenerator(model=mock_model)
        runner = BenchmarkRunner(
            config={
                "model": {"name": "mock"},
                "generation": {},
                "datasets": {"spider": {"cache_dir": "data/spider"}},
                "evaluation": {
                    "max_samples": 1,
                    "experiment_name": "test",
                    "mlflow_tracking_uri": f"sqlite:///{(tmp_path / 'mlflow.db').resolve().as_posix()}",
                },
                "seeds": {"random": 42, "numpy": 42, "torch": 42},
            },
            sql_generator=generator,
        )
        result = runner.run_spider("validation")
        assert "spider" in result["dataset"]

    @patch("src.datasets.bird_loader.BirdLoader.load_split")
    def test_run_bird(self, mock_load, mock_model, tmp_path):
        mock_load.return_value = [
            {
                "question": "Count rows",
                "schema": "Database: test",
                "sql": "SELECT COUNT(*) FROM t",
                "db_id": "test",
            }
        ]
        generator = SQLGenerator(model=mock_model)
        runner = BenchmarkRunner(
            config={
                "model": {"name": "mock"},
                "generation": {},
                "datasets": {"bird": {"cache_dir": "data/bird"}},
                "evaluation": {
                    "max_samples": 1,
                    "experiment_name": "test",
                    "mlflow_tracking_uri": f"sqlite:///{(tmp_path / 'mlflow.db').resolve().as_posix()}",
                },
                "seeds": {"random": 42, "numpy": 42, "torch": 42},
            },
            sql_generator=generator,
        )
        result = runner.run_bird("validation")
        assert "bird" in result["dataset"]
