"""Loads Spider and BirdBench into a common normalized record shape:

    {"question": str, "gold_sql": str, "db_id": str, "schema": DatabaseSchema}

Both datasets are distributed as (a) a HuggingFace split of question/SQL/db_id
rows and (b) a separate zip of the actual SQLite database files needed for
execution-accuracy evaluation. ``normalize_spider_row`` / ``normalize_bird_row``
are pure functions (no I/O) so the field-mapping logic is fully unit-testable
against the exact row shapes documented for each dataset, independent of
network access; ``load_split`` does the actual HF download + database lookup.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

import requests

from codegen_rag.data.downloaders import DownloadError
from codegen_rag.sql.schema import DatabaseSchema, introspect_sqlite_schema
from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


def normalize_spider_row(row: dict[str, Any]) -> dict[str, Any]:
    """Map a raw `xlangai/spider` row to the common shape (schema attached later)."""
    return {
        "question": row.get("question", ""),
        "gold_sql": row.get("query") or row.get("sql", ""),
        "db_id": row.get("db_id", ""),
        "source": "spider",
    }


def normalize_bird_row(row: dict[str, Any]) -> dict[str, Any]:
    """Map a raw `birdsql/bird` row to the common shape (schema attached later)."""
    return {
        "question": row.get("question", ""),
        "gold_sql": row.get("SQL") or row.get("query") or row.get("sql", ""),
        "db_id": row.get("db_id", ""),
        "evidence": row.get("evidence", ""),
        "source": "bird",
    }


def _is_google_drive_url(url: str) -> bool:
    return "drive.google.com" in url or "drive.usercontent.google.com" in url


def _download_via_requests(archive_url: str, zip_path: Path) -> None:
    with requests.get(archive_url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with open(zip_path, "wb") as fh:
            for chunk in response.iter_content(chunk_size=1 << 20):
                fh.write(chunk)


def _extract_google_drive_id(url: str) -> str | None:
    import re

    match = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    return None


def _extract_google_drive_id(url: str) -> str | None:
    import re

    match = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    return None


def _download_via_gdown(archive_url: str, zip_path: Path) -> None:
    import gdown

    file_id = _extract_google_drive_id(archive_url)
    if file_id:
        gdown.download(id=file_id, output=str(zip_path), quiet=False)
    else:
        gdown.download(url=archive_url, output=str(zip_path), quiet=False, fuzzy=True)


def download_and_extract_databases(archive_url: str, target_dir: Path) -> Path:
    """Download and unzip a `<db_id>/<db_id>.sqlite` database archive
    (Spider's ``testsuite_databases.zip`` or BirdBench's ``dev_databases.zip``).
    Idempotent: skips if already extracted.
    """
    marker = target_dir / ".extracted"
    if marker.exists():
        logger.info("Database archive already extracted at %s", target_dir)
        return target_dir

    target_dir.mkdir(parents=True, exist_ok=True)
    zip_path = target_dir / "databases.zip"

    if zip_path.exists() and zipfile.is_zipfile(zip_path):
        logger.info("Using pre-existing archive already at %s", zip_path)
    else:
        logger.info("Downloading database archive from %s", archive_url)
        if _is_google_drive_url(archive_url):
            _download_via_gdown(archive_url, zip_path)
        else:
            _download_via_requests(archive_url, zip_path)

    if not zipfile.is_zipfile(zip_path):
        preview = zip_path.read_bytes()[:200] if zip_path.exists() else b""
        zip_path.unlink(missing_ok=True)
        raise DownloadError(
            f"Downloaded file from {archive_url} is not a valid zip archive "
            f"(likely an HTML interstitial or expired link). First bytes: {preview!r}\n\n"
            f"Google Drive appears to be gating automated downloads of this specific file "
            f"(common for heavily-shared research archives). Workaround: open the link in "
            f"your own browser, click through the 'can't scan for viruses' warning, download "
            f"the zip, then upload it to exactly this path in your Drive project so this "
            f"function picks it up automatically on the next run:\n  {zip_path}"
        )

    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(target_dir)
    zip_path.unlink(missing_ok=True)
    _extract_nested_zips(target_dir)
    marker.write_text("ok")
    logger.info("Extracted database archive to %s", target_dir)
    return target_dir


def _extract_nested_zips(root: Path) -> None:
    for zip_path in list(root.rglob("*.zip")):
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(zip_path.parent)
        zip_path.unlink()
        _extract_nested_zips(zip_path.parent)

def find_db_path(databases_root: Path, db_id: str) -> Path | None:
    """Locate the `<db_id>.sqlite` file for a given database id, tolerating
    the couple of directory layouts these archives ship with."""
    candidates = [
        databases_root / db_id / f"{db_id}.sqlite",
        databases_root / f"{db_id}.sqlite",
        *databases_root.rglob(f"{db_id}.sqlite"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def attach_schemas(
    records: list[dict[str, Any]],
    databases_root: Path,
    schema_cache: dict[str, DatabaseSchema] | None = None,
) -> list[dict[str, Any]]:
    """Attach a `DatabaseSchema` (and resolved `db_path`) to each normalized
    record, skipping (with a warning) any record whose database file is
    missing rather than crashing the whole load.
    """
    schema_cache = schema_cache if schema_cache is not None else {}
    enriched: list[dict[str, Any]] = []

    for record in records:
        db_id = record["db_id"]
        if db_id not in schema_cache:
            db_path = find_db_path(databases_root, db_id)
            if db_path is None:
                logger.warning("Could not locate SQLite file for db_id=%s; skipping record", db_id)
                continue
            schema_cache[db_id] = introspect_sqlite_schema(db_path, db_id=db_id)
        schema = schema_cache[db_id]
        enriched.append({**record, "schema": schema, "db_path": schema.db_path})

    return enriched


def load_split(
    hf_dataset: str,
    split: str,
    databases_root: Path,
    dataset_kind: str = "spider",
) -> list[dict[str, Any]]:
    """Load one split (e.g. "train"/"validation") end to end: HF rows ->
    normalized records -> schema-attached records ready for SQLGenerationTask.
    """
    from datasets import load_dataset

    normalizer = normalize_spider_row if dataset_kind == "spider" else normalize_bird_row
    raw = load_dataset(hf_dataset, split=split, trust_remote_code=True)
    normalized = [normalizer(dict(row)) for row in raw]
    return attach_schemas(normalized, databases_root)
