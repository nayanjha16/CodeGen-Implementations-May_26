"""Tests for dataset loaders and preprocessing."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.datasets.bird_loader import BirdLoader
from src.datasets.preprocess import DatasetPreprocessor, clean_sql, compute_statistics
from src.datasets.spider_loader import SpiderLoader


class TestPreprocess:
    def test_clean_sql(self):
        assert clean_sql("  SELECT * FROM t;  ") == "SELECT * FROM t"
        assert clean_sql("SELECT  *   FROM   t") == "SELECT * FROM t"

    def test_compute_statistics(self, sample_examples):
        stats = compute_statistics(sample_examples)
        assert stats["count"] == 2
        assert stats["avg_question_length"] > 0
        assert "SELECT" in stats["sql_keyword_distribution"]

    def test_dataset_preprocessor(self, sample_examples, tmp_path):
        preprocessor = DatasetPreprocessor(output_dir=tmp_path)
        cleaned = preprocessor.clean_examples(sample_examples)
        assert len(cleaned) == 2

        train, test = preprocessor.train_test_split(cleaned, test_ratio=0.5, seed=42)
        assert len(train) == 1
        assert len(test) == 1

        result = preprocessor.process_and_save(cleaned, "test_set")
        assert result["count"] == 2
        assert Path(result["path"]).exists()


class TestSpiderLoader:
    def test_standardize_format(self, tmp_path):
        loader = SpiderLoader(cache_dir=tmp_path)
        schemas = {"db1": "Table t(id, name)"}
        raw = [{"question": "List all", "query": "SELECT * FROM t", "db_id": "db1"}]
        result = loader._standardize(raw, schemas)
        assert result[0]["question"] == "List all"
        assert result[0]["sql"] == "SELECT * FROM t"
        assert result[0]["schema"] == "Table t(id, name)"

    @patch("src.datasets.spider_loader.requests.get")
    def test_download(self, mock_get, tmp_path):
        import io
        import zipfile

        loader = SpiderLoader(cache_dir=tmp_path)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            zf.writestr(
                "spider-master/train_spider.json",
                json.dumps([{"question": "q", "query": "SELECT 1", "db_id": "db1"}]),
            )
            zf.writestr("spider-master/dev.json", json.dumps([]))
            zf.writestr("spider-master/tables.json", json.dumps([]))
        mock_response = MagicMock()
        mock_response.content = buffer.getvalue()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        loader.download()
        assert (tmp_path / ".downloaded").exists()


class TestBirdLoader:
    def test_standardize_format(self, tmp_path):
        loader = BirdLoader(cache_dir=tmp_path / "data" / "bird")
        raw = [
            {
                "question": "What is the total?",
                "SQL": "SELECT COUNT(*) FROM t",
                "db_id": "test_db",
                "evidence": "count all rows",
            }
        ]
        result = loader._standardize(raw)
        assert result[0]["sql"] == "SELECT COUNT(*) FROM t"
        assert "test_db" in result[0]["schema"]

    def test_empty_statistics(self):
        stats = compute_statistics([])
        assert stats["count"] == 0
