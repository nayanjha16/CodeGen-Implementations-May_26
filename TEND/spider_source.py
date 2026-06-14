"""Load Spider dataset samples for TEND without importing src.datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.utils.paths import get_spider_data_dir, resolve_project_path


class SpiderSource:
    """Read Spider splits and tables.json from the local cache."""

    def __init__(self, cache_dir: str | Path | None = None):
        resolved = Path(cache_dir) if cache_dir else get_spider_data_dir()
        self.cache_dir = resolve_project_path(resolved)
        self.data_dir = self._resolve_data_dir()

    def _find_root(self) -> Path:
        candidates = list(self.cache_dir.glob("spider-*"))
        if candidates:
            return candidates[0]
        nested = self.cache_dir / "spider"
        if nested.exists():
            return nested
        return self.cache_dir

    def _resolve_data_dir(self) -> Path:
        if (self.cache_dir / "dev.json").exists():
            return self.cache_dir
        if (self.cache_dir / "spider_data" / "dev.json").exists():
            return self.cache_dir / "spider_data"

        root = self._find_root()
        for cand in (root, root / "evaluation_examples" / "examples", self.cache_dir):
            if (cand / "dev.json").exists() or (cand / "train_spider.json").exists():
                return cand
        raise FileNotFoundError(
            f"Spider data not found under {self.cache_dir}. "
            "Download Spider first via src.datasets.spider_loader.SpiderLoader()."
        )

    def _split_path(self, split: str) -> Path:
        split_files = {
            "train": ["train_spider.json", "train.json"],
            "validation": ["dev.json"],
            "dev": ["dev.json"],
            "test": ["test.json", "test_data.json"],
        }
        for filename in split_files.get(split, []):
            path = self.data_dir / filename
            if path.exists():
                return path
        raise FileNotFoundError(f"Spider split '{split}' not found under {self.data_dir}")

    def load_tables(self) -> dict[str, dict[str, Any]]:
        tables_path = self.data_dir / "tables.json"
        with open(tables_path, encoding="utf-8") as f:
            tables_data = json.load(f)
        return {entry["db_id"]: entry for entry in tables_data}

    def load_split(self, split: str = "train") -> list[dict[str, str]]:
        with open(self._split_path(split), encoding="utf-8") as f:
            examples = json.load(f)

        rows: list[dict[str, str]] = []
        for ex in examples:
            rows.append(
                {
                    "question": ex.get("question", ""),
                    "sql": ex.get("query", ex.get("sql", "")),
                    "db_id": ex.get("db_id", ""),
                }
            )
        return rows
