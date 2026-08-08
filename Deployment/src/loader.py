"""Dataset and schema loaders for the three tasks (SPEC §1, §10 step 5).

Everything the pipeline consumes is normalised into a single ``Example`` shape so
downstream stages (prompt builder, retriever, trainer, eval) never re-parse the
raw JSON. One DocSpider entry yields *two* examples — ``sql2nosql`` and
``text2nosql`` — since both NoSQL tasks share one file (SPEC §1.1).

Schema handling:
- Spider's ``tables.json`` is verbose and must be compacted with
  ``minify_sql_schema()`` to ``table(col1, col2) | ...`` form (plan §4). We use
  the *original* identifiers (``*_original``) because that is what the gold SQL
  references.
- DocSpider's ``collections.json`` is already compact; we render the same
  ``Coll(col1, col2) | ...`` string from it (``_id`` dropped), so both task
  families present schema to the model identically.

Each example carries a content-derived ``uid`` (task + db + input + gold) so the
train/valid split (``splits.py``) is reproducible and the dev-leak guard is a
genuine content check, not a filename coincidence (STATUS dev-leak rule).
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from . import config

log = logging.getLogger(__name__)

# Which raw file backs each (source, split).
_SPIDER_FILES = {"train": "train_spider.json", "dev": "dev.json"}
_DOCSPIDER_FILES = {"train": "train.json", "dev": "dev.json"}

# Tasks by source.
SQL_TASK = "text2sql"
NOSQL_TASKS = ("sql2nosql", "text2nosql")


@dataclass(frozen=True)
class Example:
    """One normalised training/eval instance for a single task.

    ``question`` is the NL question (text2sql / text2nosql input); ``source_sql``
    is the gold SQL fed as input for ``sql2nosql``. ``gold`` is the target query
    (SQL for text2sql, MQL shell syntax for the NoSQL tasks). ``schema`` is the
    compact schema string for ``db_id``.
    """

    task: str
    source: str  # "spider" | "docspider"
    split: str  # "train" | "valid" | "dev"
    db_id: str
    question: str | None
    source_sql: str | None
    gold: str
    schema: str
    difficulty: str | None
    origin_index: int  # position in the raw source file (provenance)
    aux_sql: str | None = None  # gold SQL, carried on NoSQL tasks for ORDER BY detection (not in uid)

    @property
    def uid(self) -> str:
        """Stable content hash — identity for splitting, self-exclusion, leak checks."""
        payload = "|".join(
            (
                self.task,
                self.db_id,
                self.question or "",
                self.source_sql or "",
                self.gold,
            )
        )
        return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


# --- Raw JSON ---------------------------------------------------------------
def _read_json_list(path: Path) -> list:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError(f"{path} is not a JSON list")
    return data


# --- Schema compaction ------------------------------------------------------
def minify_sql_schema(table_entry: dict) -> str:
    """Compact one ``tables.json`` entry to ``table(col1, col2) | table2(...)``.

    Uses original identifiers (``table_names_original`` / ``column_names_original``)
    so the string matches the identifiers used in the gold SQL. The ``[-1, "*"]``
    global column is skipped.
    """
    tables = table_entry["table_names_original"]
    cols_by_table: dict[int, list[str]] = {}
    for tidx, col in table_entry["column_names_original"]:
        if tidx < 0:  # the "*" pseudo-column
            continue
        cols_by_table.setdefault(tidx, []).append(col)
    parts = []
    for i, tbl in enumerate(tables):
        cols = cols_by_table.get(i, [])
        parts.append(f"{tbl}({', '.join(cols)})")
    return " | ".join(parts)


def _minify_collections(coll_entry: dict) -> str:
    """Compact one ``collections.json`` entry to ``Coll(col1, col2) | ...``.

    ``_id`` is dropped (it is Mongo's implicit key, not a schema column and
    ignored by the execution scorer).
    """
    colls = coll_entry["collection_names"]
    cols_by_coll: dict[int, list[str]] = {}
    for cidx, col in coll_entry["column_names"]:
        if col == "_id":
            continue
        cols_by_coll.setdefault(cidx, []).append(col)
    parts = []
    for i, coll in enumerate(colls):
        cols = cols_by_coll.get(i, [])
        parts.append(f"{coll}({', '.join(cols)})")
    return " | ".join(parts)


@lru_cache(maxsize=1)
def load_sql_schema_map() -> dict[str, str]:
    """db_id -> compact relational schema string (Spider ``tables.json``)."""
    entries = _read_json_list(config.SPIDER_DIR / "tables.json")
    return {e["db_id"]: minify_sql_schema(e) for e in entries}


@lru_cache(maxsize=1)
def load_nosql_schema_map() -> dict[str, str]:
    """db_id -> compact collection schema string (DocSpider ``collections.json``)."""
    entries = _read_json_list(config.DOCSPIDER_DIR / "collections.json")
    return {e["db_id"]: _minify_collections(e) for e in entries}


# --- Task loaders -----------------------------------------------------------
def load_spider(split: str) -> list[Example]:
    """Load Spider entries as ``text2sql`` examples. ``split`` in {train, dev}."""
    if split not in _SPIDER_FILES:
        raise ValueError(f"spider split must be train|dev, got {split!r}")
    entries = _read_json_list(config.SPIDER_DIR / _SPIDER_FILES[split])
    schema_map = load_sql_schema_map()
    out: list[Example] = []
    missing = 0
    for i, e in enumerate(entries):
        db_id = e["db_id"]
        schema = schema_map.get(db_id)
        if schema is None:
            missing += 1
            continue
        out.append(
            Example(
                task=SQL_TASK,
                source="spider",
                split=split,
                db_id=db_id,
                question=e["question"],
                source_sql=None,
                gold=e["query"],
                schema=schema,
                difficulty=None,  # Spider has no pre-bucketed difficulty
                origin_index=i,
            )
        )
    if missing:
        log.warning("spider %s: %d entries dropped (db_id not in tables.json)", split, missing)
    return out


def load_docspider(split: str) -> list[Example]:
    """Load DocSpider entries as BOTH ``sql2nosql`` and ``text2nosql`` examples.

    Each raw entry becomes two examples (SPEC §1.1). ``split`` in {train, dev}.
    """
    if split not in _DOCSPIDER_FILES:
        raise ValueError(f"docspider split must be train|dev, got {split!r}")
    entries = _read_json_list(config.DOCSPIDER_DIR / _DOCSPIDER_FILES[split])
    schema_map = load_nosql_schema_map()
    out: list[Example] = []
    missing = 0
    for i, e in enumerate(entries):
        db_id = e["db_id"]
        schema = schema_map.get(db_id)
        if schema is None:
            missing += 1
            continue
        gold_mql = e["query"]
        difficulty = e.get("difficulty")
        gold_sql = e["spider_gold_sql"]
        # sql2nosql: gold SQL -> MQL
        out.append(
            Example(
                task="sql2nosql",
                source="docspider",
                split=split,
                db_id=db_id,
                question=None,
                source_sql=gold_sql,
                gold=gold_mql,
                schema=schema,
                difficulty=difficulty,
                origin_index=i,
                aux_sql=gold_sql,
            )
        )
        # text2nosql: NL question -> MQL
        out.append(
            Example(
                task="text2nosql",
                source="docspider",
                split=split,
                db_id=db_id,
                question=e["question"],
                source_sql=None,
                gold=gold_mql,
                schema=schema,
                difficulty=difficulty,
                origin_index=i,
                aux_sql=gold_sql,
            )
        )
    if missing:
        log.warning("docspider %s: %d entries dropped (db_id not in collections.json)", split, missing)
    return out


def load_task(task: str, split: str) -> list[Example]:
    """Load one task's examples for a given split (train|dev)."""
    if task == SQL_TASK:
        return load_spider(split)
    if task in NOSQL_TASKS:
        return [e for e in load_docspider(split) if e.task == task]
    raise ValueError(f"unknown task {task!r}")


def load_all(split: str) -> dict[str, list[Example]]:
    """All three tasks for a split, keyed by task name."""
    docs = load_docspider(split)
    return {
        SQL_TASK: load_spider(split),
        "sql2nosql": [e for e in docs if e.task == "sql2nosql"],
        "text2nosql": [e for e in docs if e.task == "text2nosql"],
    }
