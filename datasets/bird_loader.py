"""BirdBench dataset loader with automatic download and schema parsing."""

from __future__ import annotations

import json
import logging
import zipfile
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger("codegen")


class BirdLoader:
    """Load and standardize the BIRD text-to-SQL benchmark."""

    DEFAULT_URL = (
        "https://github.com/AlibabaResearch/DAMO-ConvAI/archive/refs/heads/master.zip"
    )

    def __init__(self, cache_dir: str | Path = "data/bird", url: str | None = None):
        self.cache_dir = Path(cache_dir)
        self.url = url or self.DEFAULT_URL
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def download(self, force: bool = False) -> Path:
        """Download BIRD dataset archive if not cached."""
        marker = self.cache_dir / ".downloaded"
        if marker.exists() and not force:
            return self.cache_dir

        zip_path = self.cache_dir / "bird.zip"
        logger.info("Downloading BIRD from %s", self.url)
        response = requests.get(self.url, timeout=120)
        response.raise_for_status()
        zip_path.write_bytes(response.content)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(self.cache_dir)
        zip_path.unlink(missing_ok=True)
        marker.touch()
        return self.cache_dir

    def _find_bird_root(self) -> Path:
        """Locate BIRD dataset within extracted archive."""
        candidates = [
            self.cache_dir / "DAMO-ConvAI-master" / "bird" / "finetuning",
            self.cache_dir / "bird" / "finetuning",
        ]
        for path in candidates:
            if path.exists():
                return path
        for path in self.cache_dir.rglob("finetuning"):
            if (path / "train.json").exists() or (path / "dev.json").exists():
                return path
        return self.cache_dir

    def _schema_from_evidence(self, example: dict) -> str:
        """Extract schema hints from BIRD evidence and db_id."""
        parts = []
        if example.get("db_id"):
            parts.append(f"Database: {example['db_id']}")
        if example.get("evidence"):
            parts.append(f"Evidence: {example['evidence']}")
        return "\n".join(parts)

    def _standardize(self, examples: list[dict]) -> list[dict[str, str]]:
        """Convert raw BIRD examples to standard format."""
        standardized = []
        for ex in examples:
            standardized.append(
                {
                    "question": ex.get("question", ""),
                    "schema": self._schema_from_evidence(ex),
                    "sql": ex.get("SQL", ex.get("sql", "")),
                    "db_id": ex.get("db_id", ""),
                    "difficulty": ex.get("difficulty", ""),
                }
            )
        return standardized

    def load_split(self, split: str = "train") -> list[dict[str, str]]:
        """Load train, validation (dev), or test split."""
        self.download()
        root = self._find_bird_root()

        split_map = {
            "train": root / "train.json",
            "validation": root / "dev.json",
            "dev": root / "dev.json",
            "test": root / "test.json",
        }
        path = split_map.get(split)
        if path is None or not path.exists():
            raise FileNotFoundError(f"BIRD split '{split}' not found at {path}")

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        return self._standardize(data)

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
        root = self._find_bird_root()
        candidates = [
            root.parent / "train_databases" / db_id / f"{db_id}.sqlite",
            root.parent / "dev_databases" / db_id / f"{db_id}.sqlite",
            root / "databases" / db_id / f"{db_id}.sqlite",
        ]
        for db_path in candidates:
            if db_path.exists():
                return db_path
        return None
