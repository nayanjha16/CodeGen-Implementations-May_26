"""Load the published TEND silver dataset from Hugging Face."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

import requests

DEFAULT_TEND_DATASET_ID = "care2achieve/tend"
TEND_CONFIGS = frozenset({"spider", "bird"})
TEND_SPLITS = frozenset({"train", "test"})
GOLD_VALIDATION_DATASET_NAME = "spider_gold_validation"


def load_gold_validation(path: str | Path | None = None) -> list[dict[str, str]]:
    """Load the frozen Spider gold validation JSONL used for baseline eval."""
    from src.utils.paths import get_spider_gold_validation_path

    jsonl_path = Path(path) if path else get_spider_gold_validation_path()
    if not jsonl_path.is_absolute():
        from src.utils.paths import get_project_root

        jsonl_path = get_project_root() / jsonl_path
    if not jsonl_path.exists():
        raise FileNotFoundError(
            f"Spider gold validation set not found at {jsonl_path}. "
            "Expected data/spider_gold_validation.jsonl."
        )

    rows: list[dict[str, str]] = []
    with jsonl_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if "schema" not in row and "sql_schema" in row:
                row = TENDLoader.standardize(row)
            rows.append(row)

    if not rows:
        raise ValueError(f"Spider gold validation set is empty: {jsonl_path}")

    logger.info(
        "Loaded spider gold validation (%d rows) from %s",
        len(rows),
        jsonl_path,
    )
    return rows

logger = logging.getLogger("codegen")


class TENDLoader:
    """Load judge-approved TEND examples from Hugging Face."""

    def __init__(
        self,
        dataset_id: str | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.dataset_id = (
            dataset_id
            or os.environ.get("TEND_DATASET_ID")
            or DEFAULT_TEND_DATASET_ID
        )
        self.config = (config or "spider").strip().lower()
        if self.config not in TEND_CONFIGS:
            allowed = ", ".join(sorted(TEND_CONFIGS))
            raise ValueError(
                f"Unknown TEND config '{config}'. Expected one of: {allowed}"
            )

    @staticmethod
    def standardize(row: dict[str, Any]) -> dict[str, str]:
        """Map a Hugging Face record to the project example schema."""
        return {
            "id": str(row.get("id", "")),
            "source_dataset": str(
                row.get("source_dataset", row.get("dataset", "spider"))
            ).strip()
            or "spider",
            "split": str(row.get("split", "")),
            "db_id": str(row.get("db_id", "")),
            "question": str(row.get("question", "")).strip(),
            "schema": str(row.get("sql_schema", "")).strip(),
            "sql": str(row.get("sql_query", "")).strip(),
            "nosql_schema": str(row.get("nosql_schema", "")).strip(),
            "nosql_query": str(row.get("nosql_query", "")).strip(),
            "documentation": str(row.get("documentation", "")).strip(),
            "evaluation_summary": str(row.get("evaluation_summary", "")).strip(),
            "execution_accuracy": str(row.get("execution_accuracy", "")).strip(),
            "execution_comparison": str(row.get("execution_comparison", "")).strip(),
        }

    def _cache_dir(self) -> Path:
        override = os.environ.get("TEND_CACHE_DIR")
        if override:
            base = Path(override)
            if not base.is_absolute():
                from src.utils.paths import get_project_root

                base = get_project_root() / base
        else:
            base = Path.home() / ".cache" / "codegen" / "tend"
        safe_id = self.dataset_id.replace("/", "__")
        return base / safe_id / self.config

    def _cache_path(self, split: str) -> Path:
        return self._cache_dir() / f"{split}.jsonl"

    def _read_cache(self, split: str) -> list[dict[str, str]] | None:
        cache_path = self._cache_path(split)
        if not cache_path.exists() or cache_path.stat().st_size == 0:
            return None

        rows: list[dict[str, str]] = []
        with cache_path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))

        if not rows:
            return None

        if "schema" not in rows[0] and "sql_schema" in rows[0]:
            rows = [self.standardize(row) for row in rows]
            self._write_cache(split, rows)

        return rows

    def _write_cache(self, split: str, rows: list[dict[str, str]]) -> None:
        cache_path = self._cache_path(split)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    def _load_from_huggingface(self, split: str) -> list[dict[str, str]]:
        from datasets import load_dataset

        dataset = load_dataset(self.dataset_id, self.config, split=split)
        return [self.standardize(row) for row in dataset]

    def _download_jsonl_via_http(self, split: str) -> list[dict[str, str]]:
        """Download JSONL directly when the HF datasets client fails."""
        url = (
            f"https://huggingface.co/datasets/{self.dataset_id}/resolve/main/"
            f"{self.config}/{split}.jsonl"
        )
        response = requests.get(
            url,
            headers={"Accept-Encoding": "identity"},
            timeout=120,
        )
        response.raise_for_status()

        rows: list[dict[str, str]] = []
        for line in response.text.splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(self.standardize(json.loads(line)))
        return rows

    def _fetch_split(self, split: str) -> list[dict[str, str]]:
        """Download one split from Hugging Face (datasets API with HTTP fallback)."""
        try:
            rows = self._load_from_huggingface(split)
        except Exception as exc:
            logger.warning(
                "load_dataset failed for %s/%s (%s); falling back to direct JSONL download",
                self.dataset_id,
                self.config,
                exc,
            )
            rows = self._download_jsonl_via_http(split)
        return rows

    def refresh_split(self, split: str = "test") -> list[dict[str, str]]:
        """Force-download a split from Hugging Face and overwrite the local cache."""
        normalized = split.strip().lower()
        if normalized == "validation":
            normalized = "test"
        if normalized not in TEND_SPLITS:
            allowed = ", ".join(sorted(TEND_SPLITS))
            raise ValueError(
                f"Unknown TEND split '{split}'. Expected one of: {allowed} "
                "(or 'validation' as an alias for 'test')."
            )

        cache_path = self._cache_path(normalized)
        if cache_path.exists():
            cache_path.unlink()

        rows = self._fetch_split(normalized)
        self._write_cache(normalized, rows)
        logger.info(
            "Refreshed TEND %s/%s (%d rows) at %s",
            self.config,
            normalized,
            len(rows),
            cache_path,
        )
        return rows

    def load_split(self, split: str = "test", *, force_refresh: bool = False) -> list[dict[str, str]]:
        """Load one split (`train` or `test`) for the configured subset."""
        if force_refresh:
            return self.refresh_split(split)

        normalized = split.strip().lower()
        if normalized == "validation":
            normalized = "test"
        if normalized not in TEND_SPLITS:
            allowed = ", ".join(sorted(TEND_SPLITS))
            raise ValueError(
                f"Unknown TEND split '{split}'. Expected one of: {allowed} "
                "(or 'validation' as an alias for 'test')."
            )

        cached = self._read_cache(normalized)
        if cached is not None:
            logger.info(
                "Loaded TEND %s/%s from cache (%d rows, %s)",
                self.config,
                normalized,
                len(cached),
                self._cache_path(normalized),
            )
            return cached

        rows = self._fetch_split(normalized)
        self._write_cache(normalized, rows)
        logger.info(
            "Cached TEND %s/%s (%d rows) at %s",
            self.config,
            normalized,
            len(rows),
            self._cache_path(normalized),
        )
        return rows

    def load_all(self) -> dict[str, list[dict[str, str]]]:
        """Load both train and test splits for the configured subset."""
        return {
            split: self.load_split(split)
            for split in sorted(TEND_SPLITS)
        }
