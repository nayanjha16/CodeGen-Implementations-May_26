"""Load Spider's SQLite databases into MongoDB as the execution substrate.

Each Spider database folder holds one ``.sqlite`` file. For each, every table
becomes a Mongo collection and every row a document (column -> value). The
DocSpider gold MQL queries run against these collections.

Adapted fresh from docspider/migrate_spider_data_to_mongodb.py (SPEC §3), with:
  - batched insert_many instead of per-row insert_one
  - connection read from src.config
  - a required --confirm flag (this DROPS databases by name)
  - --only <db_id> to reload a single database
  - post-load verification that every DocSpider db_id is present and non-empty

Usage:
    python scripts/setup_mongo.py data/spider/database --confirm
    python scripts/setup_mongo.py data/spider/database --only concert_singer --confirm
"""

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
from pathlib import Path

from pymongo import MongoClient

# Make ``src`` importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import config  # noqa: E402
from src.logger import setup_logging  # noqa: E402

log = logging.getLogger("setup_mongo")

INSERT_BATCH = 1000
SKIP_NAMES = {".DS_Store"}


def _sqlite_path(db_folder: Path) -> Path | None:
    for f in sorted(db_folder.iterdir()):
        if f.suffix == ".sqlite":
            return f
    return None


def load_one(mongo: MongoClient, db_folder: Path) -> tuple[int, int]:
    """Load one Spider DB folder into Mongo. Returns (collections, documents)."""
    db_name = db_folder.name
    sqlite_file = _sqlite_path(db_folder)
    if sqlite_file is None:
        log.warning("skip %s: no .sqlite file", db_name)
        return (0, 0)

    # DROP then recreate — destructive, gated by --confirm at the CLI.
    mongo.drop_database(db_name)
    mdb = mongo[db_name]

    sconn = sqlite3.connect(str(sqlite_file))
    sconn.text_factory = lambda b: b.decode(errors="ignore")
    cur = sconn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]

    n_docs = 0
    for table in tables:
        cur.execute(f"PRAGMA table_info('{table}')")
        cols = [c[1] for c in cur.fetchall()]
        cur.execute(f"SELECT * FROM '{table}'")

        coll = mdb[table]
        batch: list[dict] = []
        while True:
            rows = cur.fetchmany(INSERT_BATCH)
            if not rows:
                break
            for row in rows:
                batch.append({col: row[i] for i, col in enumerate(cols)})
            if batch:
                coll.insert_many(batch)
                n_docs += len(batch)
                batch = []

    sconn.close()
    log.info("loaded %-30s collections=%2d docs=%d", db_name, len(tables), n_docs)
    return (len(tables), n_docs)


def verify(mongo: MongoClient) -> list[str]:
    """Return the list of DocSpider db_ids missing or empty in Mongo."""
    cols = json.loads((config.DOCSPIDER_DIR / "collections.json").read_text())
    doc_db_ids = sorted({c["db_id"] for c in cols})
    existing = set(mongo.list_database_names())
    missing = []
    for db_id in doc_db_ids:
        if db_id not in existing or not mongo[db_id].list_collection_names():
            missing.append(db_id)
    return missing


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("database_folder", help="Spider database/ folder (e.g. data/spider/database)")
    ap.add_argument("--only", help="load a single db_id instead of all")
    ap.add_argument("--confirm", action="store_true", help="required: this DROPS databases before loading")
    args = ap.parse_args()

    setup_logging(prefix="setup_mongo")

    folder = Path(args.database_folder)
    if not folder.is_dir():
        log.error("not a directory: %s", folder)
        return 2

    if not args.confirm:
        log.error(
            "refusing to run without --confirm: this DROPS and reloads Mongo "
            "databases named after Spider folders."
        )
        return 2

    mongo = MongoClient(host=config.CONFIG.mongo.host, port=config.CONFIG.mongo.port)

    if args.only:
        target = folder / args.only
        if not target.is_dir():
            log.error("no such database folder: %s", target)
            return 2
        load_one(mongo, target)
        log.info("done (single db: %s)", args.only)
        return 0

    db_folders = sorted(p for p in folder.iterdir() if p.is_dir() and p.name not in SKIP_NAMES)
    log.info("loading %d database folders from %s", len(db_folders), folder)
    processed = 0
    for db_folder in db_folders:
        colls, _ = load_one(mongo, db_folder)
        if colls:
            processed += 1

    missing = verify(mongo)
    log.info("processed %d/%d Spider folders", processed, len(db_folders))
    if missing:
        log.error("VERIFY FAILED — %d DocSpider db_ids missing/empty: %s",
                  len(missing), missing[:10])
        return 1
    log.info("VERIFY OK — all 159 DocSpider databases present and non-empty")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
