"""Spider dataset loader with automatic download and schema parsing."""

from __future__ import annotations

import json
import logging
import zipfile
from pathlib import Path
from typing import Any

import requests

from src.utils.config import (
    get_bird_dataset_url,
    get_spider_dataset_url,
    get_spider_repo_url,
    load_config,
)
from src.utils.paths import get_bird_data_dir, get_spider_data_dir, resolve_project_path

logger = logging.getLogger("codegen")


class SpiderLoader:
    """Load and standardize the Spider text-to-SQL benchmark."""

    def __init__(
        self,
        cache_dir: str | Path | None = None,
        repo_url: str | None = None,
        dataset_url: str | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.config = config or load_config()
        spider_cfg = self.config.get("datasets", {}).get("spider", {})
        resolved = Path(cache_dir) if cache_dir else get_spider_data_dir()
        self.cache_dir = resolve_project_path(resolved)
        self.url = repo_url or get_spider_repo_url(self.config)
        self.dataset_url = dataset_url or get_spider_dataset_url(self.config)
        self.data_dir = self.cache_dir / "spider_data"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._resolved_data_dir: Path | None = None
        self._announced: set[str] = set()

    def _announce_once(self, key: str, message: str) -> None:
        if key not in self._announced:
            print(message)
            self._announced.add(key)

    def download(self, force: bool = False) -> Path:
        """Download Spider dataset archive if not cached."""
        marker = self.cache_dir / ".downloaded"
        if marker.exists() and not force:
            self._announce_once(
                "download", f"Using cached dataset: {self.cache_dir}"
            )
            logger.info("Using cached Spider dataset at %s", self.cache_dir)
            return self.cache_dir

        zip_path = self.cache_dir / "spider.zip"
        self._announce_once(
            "download", f"Downloading Spider dataset to {self.cache_dir} ..."
        )
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
        """Locate extracted Spider GitHub repo root directory."""
        candidates = list(self.cache_dir.glob("spider-*"))
        if candidates:
            return candidates[0]
        nested = self.cache_dir / "spider"
        if nested.exists():
            return nested
        return self.cache_dir

    def _download_spider_data(self, force: bool = False) -> Path:
        """Download full Spider dataset (JSON + SQLite databases)."""
        marker = self.data_dir / ".downloaded"
        if marker.exists() and not force and (self.data_dir / "dev.json").exists():
            self._announce_once(
                "spider_data", f"Using cached Spider data files: {self.data_dir}"
            )
            logger.info("Using cached Spider data files at %s", self.data_dir)
            return self.data_dir

        self.data_dir.mkdir(parents=True, exist_ok=True)
        zip_path = self.cache_dir / "spider_data.zip"
        self._announce_once(
            "spider_data",
            f"Downloading full Spider data files to {self.data_dir} ...",
        )
        logger.info("Downloading full Spider dataset from %s", self.dataset_url)

        try:
            import gdown

            gdown.download(self.dataset_url, str(zip_path), quiet=False, fuzzy=True)
        except Exception:
            logger.info("gdown unavailable, using requests fallback")
            response = requests.get(self.dataset_url, timeout=300)
            response.raise_for_status()
            zip_path.write_bytes(response.content)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(self.data_dir)

        # Handle zip that extracts into a nested folder
        if not (self.data_dir / "dev.json").exists():
            for nested in self.data_dir.iterdir():
                if nested.is_dir() and (nested / "dev.json").exists():
                    for item in nested.iterdir():
                        dest = self.data_dir / item.name
                        if item.is_dir():
                            if dest.exists():
                                import shutil

                            shutil.copytree(item, dest, dirs_exist_ok=True)
                        else:
                            import shutil

                            shutil.copy2(item, dest)
                    break

        zip_path.unlink(missing_ok=True)
        marker.touch()
        return self.data_dir

    def _resolve_data_dir(self) -> Path:
        """Find directory with Spider JSON splits (dev.json, tables.json)."""
        if self._resolved_data_dir is not None:
            return self._resolved_data_dir

        self.download()

        if (self.data_dir / "dev.json").exists():
            self._resolved_data_dir = self.data_dir
            return self._resolved_data_dir

        root = self._find_root()
        candidates = [
            root,
            root / "evaluation_examples" / "examples",
            self.cache_dir,
        ]
        for cand in candidates:
            if (cand / "dev.json").exists() or (cand / "train_spider.json").exists():
                self._resolved_data_dir = cand
                return self._resolved_data_dir

        self._resolved_data_dir = self._download_spider_data()
        return self._resolved_data_dir

    def _split_path(self, data_dir: Path, split: str) -> Path | None:
        """Resolve path for a dataset split."""
        split_files = {
            "train": ["train_spider.json", "train.json"],
            "validation": ["dev.json"],
            "dev": ["dev.json"],
            "test": ["test.json", "test_data.json"],
        }
        for filename in split_files.get(split, []):
            path = data_dir / filename
            if path.exists():
                return path
        return None

    def _load_tables(self, data_dir: Path) -> dict[str, str]:
        """Build database_id -> schema string mapping."""
        tables_path = data_dir / "tables.json"
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
        data_dir = self._resolve_data_dir()
        schemas = self._load_tables(data_dir)

        path = self._split_path(data_dir, split)
        if path is None:
            raise FileNotFoundError(
                f"Spider split '{split}' not found under {data_dir}"
            )

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
        data_dir = self._resolve_data_dir()
        candidates = [
            data_dir / "database" / db_id / f"{db_id}.sqlite",
            self._find_root() / "database" / db_id / f"{db_id}.sqlite",
        ]
        for db_path in candidates:
            if db_path.exists():
                return db_path
        return None
