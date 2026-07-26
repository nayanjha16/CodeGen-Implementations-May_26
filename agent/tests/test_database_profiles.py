"""Tests for database profile resolution (TEND vs standalone demo)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent.config.settings import (
    AgentSettings,
    MongoSettings,
    PostgresSettings,
    StandaloneDatabaseSettings,
)
from agent.database.profiles import resolve_database_target


def _settings(**overrides: object) -> AgentSettings:
    base = AgentSettings(
        postgres=PostgresSettings("localhost", 5432, "tend", "tend", "postgres"),
        mongo=MongoSettings("localhost", 27017, "tend", "tend"),
        demo=StandaloneDatabaseSettings(
            "northwind",
            "northwind",
            "public",
            "northwind",
            Path("agent/data/standalone/northwind.sql"),
        ),
        codegen_api_url="http://example",
        codegen_api_key="",
        codegen_model="codegen-text2sql",
        codegen_timeout_sec=30,
        codegen_max_tokens=256,
        codegen_temperature=0.2,
        ollama_base_url="http://localhost:11434",
        ollama_model="gemma3:4b",
        database_profile="tend",
        default_dataset="spider",
        max_result_rows=100,
        max_retries=3,
        query_timeout_ms=10000,
    )
    for key, value in overrides.items():
        object.__setattr__(base, key, value)
    return base


def test_tend_profile_resolves_schema_and_mongo() -> None:
    target = resolve_database_target(
        "concert_singer",
        settings=_settings(),
    )
    assert target.profile == "tend"
    assert target.postgres_catalog == "tend_spider"
    assert target.postgres_schema == "concert_singer"
    assert target.mongo_database == "spider_concert_singer"


def test_standalone_profile_uses_configured_database() -> None:
    target = resolve_database_target(
        settings=_settings(database_profile="standalone"),
    )
    assert target.profile == "standalone"
    assert target.db_id == "northwind"
    assert target.postgres_catalog == "northwind"
    assert target.postgres_schema == "public"
    assert target.mongo_database == "northwind"


def test_standalone_cli_db_id_overrides_default_catalog() -> None:
    target = resolve_database_target(
        "chinook",
        settings=_settings(database_profile="standalone"),
    )
    assert target.db_id == "chinook"
    assert target.postgres_catalog == "chinook"
    assert target.mongo_database == "chinook"


def test_tend_requires_db_id() -> None:
    with pytest.raises(ValueError, match="db_id is required"):
        resolve_database_target(settings=_settings())


def test_standalone_requires_env_config() -> None:
    empty_demo = StandaloneDatabaseSettings("", "", "public", "", None)
    with pytest.raises(ValueError, match="AGENT_DEMO_POSTGRES_DATABASE"):
        resolve_database_target(
            settings=_settings(database_profile="standalone", demo=empty_demo),
        )
