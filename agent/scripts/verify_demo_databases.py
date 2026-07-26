"""Live verification for standalone demo databases."""

from __future__ import annotations

import os
import sys

from agent.config.settings import get_settings
from agent.database import MongoExecutor, PostgresExecutor


def check_demo(name: str, *, pg_sql: str, mongo_query: str) -> bool:
    get_settings.cache_clear()
    os.environ["AGENT_DB_PROFILE"] = "standalone"
    os.environ["AGENT_DEMO_DB_ID"] = name
    os.environ["AGENT_DEMO_POSTGRES_DATABASE"] = name
    os.environ["AGENT_DEMO_MONGO_DATABASE"] = name
    os.environ["AGENT_DEMO_POSTGRES_SCHEMA"] = "public"

    pg = PostgresExecutor()
    mg = MongoExecutor()
    ok = True
    try:
        if not pg.ping(profile="standalone"):
            print(f"{name}: FAIL postgres ping")
            return False
        if not mg.ping():
            print(f"{name}: FAIL mongo ping")
            return False

        schema = pg.introspect_schema(profile="standalone")
        pg_result = pg.execute(pg_sql, profile="standalone")
        cols = mg.list_collections(profile="standalone")
        mongo_result = mg.execute(mongo_query, profile="standalone")

        print(f"{name}:")
        print(f"  postgres tables: {len(schema.tables)}")
        print(f"  postgres exec: ok={pg_result.ok} rows={pg_result.row_count} err={pg_result.error}")
        print(f"  mongo collections: {len(cols)}")
        print(f"  mongo exec: ok={mongo_result.ok} rows={mongo_result.row_count} err={mongo_result.error}")

        if not pg_result.ok or not mongo_result.ok:
            ok = False
    finally:
        pg.close()
        mg.close()
    return ok


def main() -> int:
    demos = [
        (
            "chinook",
            'SELECT COUNT(*) AS c FROM "Customer"',
            "db.customer.find({})",
        ),
        (
            "northwind",
            "SELECT COUNT(*) AS c FROM customers",
            "db.customers.find({})",
        ),
    ]
    results = [check_demo(name, pg_sql=sql, mongo_query=mongo) for name, sql, mongo in demos]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
