#!/usr/bin/env python3
"""Load agent demo Postgres SQL and mirror tables into MongoDB."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

AGENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = AGENT_ROOT.parent


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


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


def _copy_postgres_to_mongo(*, force: bool) -> dict[str, int]:
    import psycopg
    from pymongo import MongoClient

    pg_host = os.getenv("POSTGRES_HOST", "localhost")
    pg_port = int(os.getenv("POSTGRES_PORT", "5432"))
    pg_user = os.getenv("POSTGRES_USER", "tend")
    pg_password = os.getenv("POSTGRES_PASSWORD", "tend")
    pg_database = os.getenv("AGENT_DEMO_POSTGRES_DATABASE") or os.getenv("AGENT_DEMO_DB_ID", "")
    pg_schema = os.getenv("AGENT_DEMO_POSTGRES_SCHEMA", "public")

    mongo_host = os.getenv("MONGO_HOST", "localhost")
    mongo_port = int(os.getenv("MONGO_PORT", "27017"))
    mongo_user = os.getenv("MONGO_USER", "tend")
    mongo_password = os.getenv("MONGO_PASSWORD", "tend")
    mongo_database = os.getenv("AGENT_DEMO_MONGO_DATABASE") or pg_database

    if not pg_database or not mongo_database:
        raise RuntimeError(
            "Set AGENT_DEMO_DB_ID (or AGENT_DEMO_POSTGRES_DATABASE / AGENT_DEMO_MONGO_DATABASE) "
            "before mirroring."
        )

    pg_dsn = f"host={pg_host} port={pg_port} dbname={pg_database} user={pg_user} password={pg_password}"
    mongo_client = MongoClient(
        host=mongo_host,
        port=mongo_port,
        username=mongo_user or None,
        password=mongo_password or None,
        authSource="admin",
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
            raise RuntimeError(
                f"No tables in schema {pg_schema!r} on database {pg_database!r}. "
                "Run setup_demo_postgres first."
            )

        existing = mongo_db.list_collection_names()
        if existing and not force:
            print(
                f"MongoDB {mongo_database!r} already has {len(existing)} collections. "
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
                    if batch:
                        collection.insert_many(batch, ordered=False)
                    doc_count += len(batch)

            if doc_count == 0:
                mongo_db.create_collection(collection_name)
            collection.create_index("id")
            counts[collection_name] = doc_count
            print(f"  {collection_name}: {doc_count} documents")

    mongo_client.close()
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror agent demo Postgres to MongoDB.")
    parser.add_argument("--force", action="store_true", help="Drop/reload Mongo collections")
    parser.add_argument("--skip-postgres", action="store_true", help="Skip Postgres load step")
    args = parser.parse_args()

    _load_env_file(REPO_ROOT / ".env")
    _load_env_file(AGENT_ROOT / ".env")

    setup_sh = AGENT_ROOT / "scripts" / "setup_demo_postgres.sh"
    if not args.skip_postgres and setup_sh.is_file():
        cmd = ["bash", str(setup_sh), "--use-tend", "--no-docker"]
        if args.force:
            cmd.append("--force")
        print("Ensuring Postgres demo via", setup_sh)
        try:
            subprocess.run(cmd, check=True, cwd=str(REPO_ROOT))
        except subprocess.CalledProcessError as exc:
            print(
                "Postgres setup failed. On Windows run: "
                ".\\agent\\scripts\\setup_demo_postgres.ps1 -UseTend",
                file=sys.stderr,
            )
            return exc.returncode

    mongo_database = os.getenv("AGENT_DEMO_MONGO_DATABASE") or os.getenv("AGENT_DEMO_DB_ID", "")
    if not mongo_database:
        print("Set AGENT_DEMO_DB_ID before running.", file=sys.stderr)
        return 1
    print(f"Mirroring Postgres demo to MongoDB database {mongo_database!r} ...")
    counts = _copy_postgres_to_mongo(force=args.force)
    if counts:
        print(f"Loaded {len(counts)} collections ({sum(counts.values())} documents).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
