"""BirdBench dataset loader with automatic download and schema parsing."""

from __future__ import annotations

import json
import logging
import shutil
import zipfile
from pathlib import Path
from typing import Any

import requests

from src.utils.config import get_bird_dataset_url, load_config
from src.utils.paths import get_bird_data_dir, resolve_project_path

logger = logging.getLogger("codegen")


class BirdLoader:
    """Load and standardize the BIRD text-to-SQL benchmark."""

    def __init__(
        self,
        cache_dir: str | Path | None = None,
        dataset_url: str | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.config = config or load_config()
        resolved = Path(cache_dir) if cache_dir else get_bird_data_dir()
        self.cache_dir = resolve_project_path(resolved)
        self.url = dataset_url or get_bird_dataset_url(self.config)
        self.data_dir = self.cache_dir / "bird_data"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._resolved_data_dir: Path | None = None
        self._announced: set[str] = set()

    def _announce_once(self, key: str, message: str) -> None:
        if key not in self._announced:
            print(message)
            self._announced.add(key)

    def _find_data_dir(self) -> Path | None:
        """Locate directory containing BIRD JSON splits."""
        candidates = [
            self.data_dir,
            self.cache_dir,
        ]
        for base in candidates:
            if not base.exists():
                continue
            if (base / "dev.json").exists() or (base / "train.json").exists():
                return base
            for nested in base.iterdir():
                if nested.is_dir() and (
                    (nested / "dev.json").exists() or (nested / "train.json").exists()
                ):
                    return nested
        return None

    def _flatten_nested_data(self, nested: Path) -> None:
        """Move split files from a nested extract folder into bird_data/."""
        for item in nested.iterdir():
            dest = self.data_dir / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.move(str(item), str(dest))
            else:
                shutil.copy2(item, dest)

    def _extract_databases(self, data_dir: Path) -> None:
        """Extract dev_databases.zip or train_databases.zip when present."""
        for zip_name in ("dev_databases.zip", "train_databases.zip"):
            db_zip = data_dir / zip_name
            if not db_zip.exists():
                continue
            target_name = zip_name.replace(".zip", "")
            target_dir = data_dir / target_name
            if target_dir.exists():
                continue
            with zipfile.ZipFile(db_zip, "r") as zf:
                zf.extractall(data_dir)

    def _download_bird_data(self, force: bool = False) -> Path:
        """Download official BIRD dev bundle (JSON + SQLite databases)."""
        marker = self.data_dir / ".downloaded"
        if marker.exists() and not force and self._find_data_dir() is not None:
            self._announce_once(
                "bird_data", f"Using cached BIRD data files: {self.data_dir}"
            )
            logger.info("Using cached BIRD data files at %s", self.data_dir)
            return self.data_dir

        self.data_dir.mkdir(parents=True, exist_ok=True)
        zip_path = self.cache_dir / "bird_dev.zip"
        self._announce_once(
            "bird_data",
            f"Downloading BIRD data files to {self.data_dir} ...",
        )
        logger.info("Downloading BIRD dataset from %s", self.url)

        response = requests.get(self.url, timeout=600, stream=True)
        response.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(self.data_dir)

        if not (self.data_dir / "dev.json").exists():
            for nested in self.data_dir.iterdir():
                if nested.is_dir() and (
                    (nested / "dev.json").exists() or (nested / "train.json").exists()
                ):
                    self._flatten_nested_data(nested)
                    if nested.exists() and not any(nested.iterdir()):
                        nested.rmdir()
                    break

        resolved = self._find_data_dir()
        if resolved is not None and resolved != self.data_dir:
            for item in resolved.iterdir():
                dest = self.data_dir / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.move(str(item), str(dest))
                elif not dest.exists():
                    shutil.move(str(item), str(dest))

        data_root = self._find_data_dir() or self.data_dir
        self._extract_databases(data_root)

        zip_path.unlink(missing_ok=True)
        marker.touch()
        (self.cache_dir / ".downloaded").touch()
        return self.data_dir

    def _resolve_data_dir(self) -> Path:
        """Find directory with BIRD JSON splits (dev.json, train.json)."""
        if self._resolved_data_dir is not None:
            return self._resolved_data_dir

        data_dir = self._find_data_dir()
        if data_dir is not None:
            self._extract_databases(data_dir)
            self._resolved_data_dir = data_dir
            return self._resolved_data_dir

        self._resolved_data_dir = self._download_bird_data()
        resolved = self._find_data_dir()
        if resolved is None:
            raise FileNotFoundError(
                f"BIRD data files not found under {self.data_dir} after download"
            )
        self._resolved_data_dir = resolved
        return self._resolved_data_dir

    def _tables_path(self, data_dir: Path, split: str) -> Path | None:
        """Resolve tables metadata file for a dataset split."""
        split_files = {
            "train": ["train_tables.json"],
            "validation": ["dev_tables.json"],
            "dev": ["dev_tables.json"],
            "test": ["test_tables.json", "dev_tables.json"],
        }
        for filename in split_files.get(split, []):
            candidate = data_dir / filename
            if candidate.exists():
                return candidate
        return None

    def _load_tables(self, data_dir: Path, split: str) -> dict[str, str]:
        """Build database_id -> schema string mapping from BIRD tables metadata."""
        tables_path = self._tables_path(data_dir, split)
        if tables_path is None:
            return {}

        with open(tables_path, encoding="utf-8") as f:
            tables_data = json.load(f)

        schemas: dict[str, str] = {}
        for db in tables_data:
            db_id = db["db_id"]
            lines = []
            table_names = db.get("table_names_original", db.get("table_names", []))
            column_names = db.get(
                "column_names_original", db.get("column_names", [])
            )
            column_types = db.get("column_types", [])
            for table_idx, table in enumerate(table_names):
                cols = []
                for col_pos, (col_table_idx, col_name) in enumerate(column_names):
                    if col_table_idx != table_idx:
                        continue
                    col_type = ""
                    if col_pos < len(column_types):
                        col_type = f" {column_types[col_pos]}"
                    cols.append(f"{col_name}{col_type}".strip())
                lines.append(f"Table {table}({', '.join(cols)})")
            schemas[db_id] = "\n".join(lines)
        return schemas

    def _build_schema(
        self, db_id: str, evidence: str, schemas: dict[str, str]
    ) -> str:
        """Combine table/column schema with optional BIRD evidence hints."""
        parts = []
        table_schema = schemas.get(db_id, "").strip()
        if table_schema:
            parts.append(table_schema)
        elif db_id:
            parts.append(f"Database: {db_id}")
        if evidence:
            parts.append(f"Evidence: {evidence}")
        return "\n".join(parts)

    def _standardize(
        self, examples: list[dict], schemas: dict[str, str]
    ) -> list[dict[str, str]]:
        """Convert raw BIRD examples to standard format."""
        standardized = []
        for ex in examples:
            db_id = ex.get("db_id", "")
            standardized.append(
                {
                    "question": ex.get("question", ""),
                    "schema": self._build_schema(
                        db_id, ex.get("evidence", ""), schemas
                    ),
                    "sql": ex.get("SQL", ex.get("sql", "")),
                    "db_id": db_id,
                    "difficulty": ex.get("difficulty", ""),
                }
            )
        return standardized

    def load_split(self, split: str = "train") -> list[dict[str, str]]:
        """Load train, validation (dev), or test split."""
        data_dir = self._resolve_data_dir()
        schemas = self._load_tables(data_dir, split)

        split_map = {
            "train": ["train.json"],
            "validation": ["dev.json"],
            "dev": ["dev.json"],
            "test": ["test.json"],
        }
        path = None
        for filename in split_map.get(split, []):
            candidate = data_dir / filename
            if candidate.exists():
                path = candidate
                break

        if path is None:
            raise FileNotFoundError(
                f"BIRD split '{split}' not found under {data_dir}"
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
                logger.warning("BIRD split %s unavailable", split)
        return result

    def get_database_path(self, db_id: str) -> Path | None:
        """Return path to SQLite database for a given db_id."""
        data_dir = self._resolve_data_dir()
        candidates = [
            data_dir / "dev_databases" / db_id / f"{db_id}.sqlite",
            data_dir / "train_databases" / db_id / f"{db_id}.sqlite",
            data_dir / "databases" / db_id / f"{db_id}.sqlite",
            data_dir.parent / "dev_databases" / db_id / f"{db_id}.sqlite",
            data_dir.parent / "train_databases" / db_id / f"{db_id}.sqlite",
        ]
        for db_path in candidates:
            if db_path.exists():
                return db_path
        return None
