#!/usr/bin/env python3
"""Export a Postgres database/schema to a plain SQL dump for agent demo data."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Postgres demo SQL via pg_dump.")
    parser.add_argument("--host", default=os.getenv("POSTGRES_HOST", "localhost"))
    parser.add_argument("--port", default=os.getenv("POSTGRES_PORT", "5432"))
    parser.add_argument("--user", default=os.getenv("POSTGRES_USER", "tend"))
    parser.add_argument("--database", required=True, help="Postgres database name (e.g. dvd)")
    parser.add_argument("--schema", default="public", help="Schema to dump (default: public)")
    parser.add_argument(
        "--output",
        required=True,
        help="Output .sql path (e.g. agent/data/dvd/test.sql)",
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Dump DDL only (no INSERT data)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("POSTGRES_PASSWORD", "tend"),
        help="Postgres password (or set POSTGRES_PASSWORD)",
    )
    args = parser.parse_args()

    pg_dump = shutil.which("pg_dump")
    if pg_dump is None:
        print(
            "pg_dump not found on PATH.\n"
            "Install PostgreSQL client tools OR run via Docker, e.g.:\n"
            "  docker exec CONTAINER pg_dump -U tend -d dvd --schema=public ...",
            file=sys.stderr,
        )
        return 1

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        pg_dump,
        "-h",
        args.host,
        "-p",
        str(args.port),
        "-U",
        args.user,
        "-d",
        args.database,
        f"--schema={args.schema}",
        "--no-owner",
        "--no-privileges",
        "--format=plain",
        "-f",
        str(output),
    ]
    if args.schema_only:
        cmd.insert(-2, "--schema-only")

    env = os.environ.copy()
    env["PGPASSWORD"] = args.password

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True, env=env)
    print(f"Wrote {output} ({output.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
