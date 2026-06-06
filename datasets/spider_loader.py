"""Spider dataset loader with automatic download and schema parsing."""

from __future__ import annotations

import json
import logging
import zipfile
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger("codegen")


class SpiderLoader:
    """Load and standardize the Spider text-to-SQL benchmark."""

    DEFAULT_URL = "https://github.com/taoyds/spider/archive/refs/heads/master.zip"

    def __init__(self, cache_dir: str | Path = "data/spider", url: str | None = None):
        self.cache_dir = Path(cache_dir)
        self.url = url or self.DEFAULT_URL
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def download(self, force: bool = False) -> Path:
        """Download Spider dataset archive if not cached."""
        marker = self.cache_dir / ".downloaded"
        if marker.exists() and not force:
            return self.cache_dir

        zip_path = self.cache_dir / "spider.zip"
        logger.info("Downloading Spider from %s", self.url)
        response = requests.get(self.url, timeout=120)
        response.raise_for_status()
        zip_path.write_bytes(response.content)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(self.cache_dir)
        zip_path.unlink(missing_ok=True)
        marker.touch()
        return self.cache_dir

    def _find_root(self) -> Path:
        """Locate extracted Spider root directory."""
        candidates = list(self.cache_dir.glob("spider-*"))
        if candidates:
            return candidates[0]
        nested = self.cache_dir / "spider"
        if nested.exists():
            return nested
        return self.cache_dir

    def _load_tables(self, root: Path) -> dict[str, str]:
        """Build database_id -> schema string mapping."""
        tables_path = root / "tables.json"
        if not tables_path.exists():
            return {}

        with open(tables_path, encoding="utf-8") as f:
            tables_data = json.load(f)

        schemas: dict[str, str] = {}
        for db in tables_data:
            db_id = db["db_id"]
            lines = []
            for i, table in enumerate(db.get("table_names_original", db.get("table_names", []))):
                cols = []
                for col_idx, col_name in db.get("column_names_original", db.get("column_names", [])):
                    if col_idx == i:
                        col_type = ""
                        if "column_types" in db and col_idx < len(db["column_types"]):
                            col_type = f" {db['column_types'][col_idx]}"
                        cols.append(f"{col_name}{col_type}".strip())
                lines.append(f"Table {table}({', '.join(cols)})")
            schemas[db_id] = "\n".join(lines)
        return schemas

    def _standardize(
        self, examples: list[dict], schemas: dict[str, str]
    ) -> list[dict[str, str]]:
        """Convert raw examples to standard format."""
        standardized = []
        for ex in examples:
            db_id = ex.get("db_id", "")
            standardized.append(
                {
                    "question": ex.get("question", ""),
                    "schema": schemas.get(db_id, ""),
                    "sql": ex.get("query", ex.get("sql", "")),
                    "db_id": db_id,
                }
            )
        return standardized

    def load_split(self, split: str = "train") -> list[dict[str, str]]:
        """Load train, dev (validation), or test split."""
        self.download()
        root = self._find_root()
        schemas = self._load_tables(root)

        split_map = {
            "train": root / "train_spider.json",
            "validation": root / "dev.json",
            "dev": root / "dev.json",
            "test": root / "test.json",
        }
        path = split_map.get(split)
        if path is None or not path.exists():
            raise FileNotFoundError(f"Spider split '{split}' not found at {path}")

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        return self._standardize(data, schemas)

    def load(self) -> dict[str, list[dict[str, str]]]:
        """Load all available splits."""
        result: dict[str, list[dict[str, str]]] = {}
        for split in ("train", "validation", "test"):
            try:
                result[split] = self.load_split(split)
            except FileNotFoundError:
                logger.warning("Spider split %s unavailable", split)
        return result

    def get_database_path(self, db_id: str) -> Path | None:
        """Return path to SQLite database for a given db_id."""
        root = self._find_root()
        db_path = root / "database" / db_id / f"{db_id}.sqlite"
        return db_path if db_path.exists() else None
