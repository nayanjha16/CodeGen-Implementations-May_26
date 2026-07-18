#!/usr/bin/env python3
"""Load tool/test.sql into PostgreSQL, then mirror the DVD database into MongoDB."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TOOL_DIR = Path(__file__).resolve().parents[1]
TEND_ROOT = Path(os.getenv("TEND_ROOT", "/Volumes/Work/TEND"))
TEND_ENV = TEND_ROOT / ".env"
SETUP_PG_SCRIPT = TOOL_DIR / "scripts" / "setup_dvd_database.sh"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        os.environ.setdefault(key, value)


def _normalize_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, memoryview):
        return bytes(value)
    return value


def _row_to_document(row: dict[str, Any]) -> dict[str, Any]:
    return {key.lower(): _normalize_value(value) for key, value in row.items()}


def _ensure_postgres_loaded(*, force: bool) -> None:
    args = [str(SETUP_PG_SCRIPT)]
    if force:
        args.append("--force")
    print(f"Ensuring PostgreSQL DVD database via {SETUP_PG_SCRIPT} ...")
    subprocess.run(args, check=True)


def _copy_postgres_to_mongo(*, force: bool) -> dict[str, int]:
    import psycopg
    from pymongo import MongoClient

    pg_host = os.getenv("POSTGRES_HOST", "localhost")
    pg_port = int(os.getenv("POSTGRES_PORT", "5432"))
    pg_user = os.getenv("POSTGRES_USER", "tend")
    pg_password = os.getenv("POSTGRES_PASSWORD", "tend")
    pg_database = os.getenv("DVD_DATABASE", "dvd")
    pg_schema = os.getenv("POSTGRES_SCHEMA", "public")

    mongo_host = os.getenv("MONGO_HOST", "localhost")
    mongo_port = int(os.getenv("MONGO_PORT", "27017"))
    mongo_user = os.getenv("MONGO_USER", "tend")
    mongo_password = os.getenv("MONGO_PASSWORD", "tend")
    mongo_database = os.getenv("MONGO_DATABASE", pg_database)
    auth_source = os.getenv("MONGO_AUTH_SOURCE", "admin")

    pg_dsn = f"host={pg_host} port={pg_port} dbname={pg_database} user={pg_user} password={pg_password}"
    mongo_client = MongoClient(
        host=mongo_host,
        port=mongo_port,
        username=mongo_user,
        password=mongo_password,
        authSource=auth_source,
        serverSelectionTimeoutMS=10_000,
    )
    mongo_client.admin.command("ping")
    mongo_db = mongo_client[mongo_database]

    counts: dict[str, int] = {}
    batch_size = 200

    with psycopg.connect(pg_dsn) as pg_conn:
        tables = [
            row[0]
            for row in pg_conn.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """,
                (pg_schema,),
            ).fetchall()
        ]

        if not tables:
            raise RuntimeError(f"No tables found in PostgreSQL schema {pg_schema!r} on database {pg_database!r}")

        existing = mongo_db.list_collection_names()
        if existing and not force:
            print(
                f"MongoDB database {mongo_database!r} already has {len(existing)} collections. "
                "Use --force to drop and reload."
            )
            return {}

        for table_name in tables:
            collection_name = table_name.lower()
            collection = mongo_db[collection_name]
            if force or collection_name in existing:
                collection.drop()

            doc_count = 0
            with pg_conn.cursor(name=f"mongo_{table_name}") as cur:
                cur.itersize = batch_size
                cur.execute(f'SELECT * FROM "{pg_schema}"."{table_name}"')
                columns = [desc.name for desc in cur.description]
                while True:
                    rows = cur.fetchmany(batch_size)
                    if not rows:
                        break
                    batch = [_row_to_document(dict(zip(columns, row, strict=True))) for row in rows]
                    collection.insert_many(batch, ordered=False)
                    doc_count += len(batch)

            if doc_count == 0:
                mongo_db.create_collection(collection_name)

            for index_col in ("id",):
                collection.create_index(index_col)

            counts[collection_name] = doc_count
            print(f"  {collection_name}: {doc_count} documents")

    mongo_client.close()
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Load tool/test.sql into PostgreSQL and mirror to MongoDB.")
    parser.add_argument("--force", action="store_true", help="Drop/reload PostgreSQL and MongoDB data")
    parser.add_argument("--skip-postgres", action="store_true", help="Skip PostgreSQL load step")
    parser.add_argument("--skip-mongo", action="store_true", help="Skip MongoDB mirror step")
    args = parser.parse_args()

    _load_env_file(TEND_ENV)
    tool_env = TOOL_DIR / ".env"
    _load_env_file(tool_env)

    if not args.skip_postgres:
        _ensure_postgres_loaded(force=args.force)

    if args.skip_mongo:
        print("Skipping MongoDB mirror.")
        return 0

    mongo_database = os.getenv("MONGO_DATABASE", os.getenv("DVD_DATABASE", "dvd"))
    print(f"Mirroring PostgreSQL DVD data to MongoDB database {mongo_database!r} ...")
    counts = _copy_postgres_to_mongo(force=args.force)
    if counts:
        print(f"Loaded {len(counts)} collections into MongoDB ({sum(counts.values())} documents total).")
    print(
        "\nConfigure the desktop app (Settings → MongoDB):\n"
        f"  host={os.getenv('MONGO_HOST', 'localhost')} "
        f"port={os.getenv('MONGO_PORT', '27017')} "
        f"database={mongo_database} "
        f"user={os.getenv('MONGO_USER', 'tend')}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"PostgreSQL setup failed with exit code {exc.returncode}", file=sys.stderr)
        raise SystemExit(exc.returncode) from exc
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
