"""Resolve Postgres catalog / schema / Mongo database for TEND vs standalone demos."""

from __future__ import annotations

from dataclasses import dataclass

from agent.config.settings import AgentSettings, DatabaseProfileKind, get_settings
from agent.database._utils import mongo_database_name, sanitize_pg_schema_name


@dataclass(frozen=True)
class ResolvedDatabaseTarget:
    """Connection target for schema introspection and query execution."""

    profile: DatabaseProfileKind
    db_id: str
    dataset: str
    postgres_catalog: str
    postgres_schema: str
    mongo_database: str


def resolve_database_target(
    db_id: str | None = None,
    *,
    dataset: str | None = None,
    profile: DatabaseProfileKind | None = None,
    settings: AgentSettings | None = None,
) -> ResolvedDatabaseTarget:
    """Map db_id + profile to concrete Postgres/Mongo locations."""
    cfg = settings or get_settings()
    active_profile = profile or cfg.database_profile
    active_dataset = dataset or cfg.default_dataset

    if active_profile == "standalone":
        if not cfg.demo.postgres_database and not cfg.demo.db_id:
            raise ValueError(
                "AGENT_DB_PROFILE=standalone requires AGENT_DEMO_DB_ID (and optionally "
                "AGENT_DEMO_POSTGRES_DATABASE / AGENT_DEMO_MONGO_DATABASE) in agent/.env"
            )
        demo_db_id = db_id or cfg.demo.db_id
        if not demo_db_id:
            raise ValueError("AGENT_DEMO_DB_ID is required when AGENT_DB_PROFILE=standalone")
        return ResolvedDatabaseTarget(
            profile="standalone",
            db_id=demo_db_id,
            dataset=active_dataset,
            postgres_catalog=db_id or cfg.demo.postgres_database or demo_db_id,
            postgres_schema=cfg.demo.postgres_schema,
            mongo_database=db_id or cfg.demo.mongo_database or demo_db_id,
        )

    if not db_id:
        raise ValueError("db_id is required when AGENT_DB_PROFILE=tend")

    schema = sanitize_pg_schema_name(db_id)
    return ResolvedDatabaseTarget(
        profile="tend",
        db_id=db_id,
        dataset=active_dataset,
        postgres_catalog=cfg.postgres.catalog_name(active_dataset),
        postgres_schema=schema,
        mongo_database=mongo_database_name(active_dataset, db_id),
    )
