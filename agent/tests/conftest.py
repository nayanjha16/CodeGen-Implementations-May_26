"""Shared pytest fixtures for agent tests."""

from __future__ import annotations

import os
from typing import Iterator

import pytest

from agent.config.settings import get_settings
from agent.database.mongodb import MongoExecutor
from agent.database.postgres import PostgresExecutor


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "integration: live Docker / demo DB tests")
    config.addinivalue_line("markers", "docker: requires TEND Postgres + Mongo")


@pytest.fixture(scope="module")
def chinook_env() -> Iterator[None]:
    """Point settings at the Chinook standalone demo."""
    get_settings.cache_clear()
    os.environ["AGENT_DB_PROFILE"] = "standalone"
    os.environ["AGENT_DEMO_DB_ID"] = "chinook"
    os.environ.pop("AGENT_DEMO_POSTGRES_DATABASE", None)
    os.environ.pop("AGENT_DEMO_MONGO_DATABASE", None)
    os.environ["AGENT_DEMO_POSTGRES_SCHEMA"] = "public"
    yield
    get_settings.cache_clear()


@pytest.fixture(scope="module")
def docker_stack(chinook_env: None) -> Iterator[None]:
    """Skip integration tests when TEND Docker is not reachable."""
    postgres = PostgresExecutor()
    mongo = MongoExecutor()
    try:
        if not postgres.ping(profile="standalone") or not mongo.ping():
            pytest.skip("TEND Docker (Postgres/Mongo) is not available on localhost")
        yield
    finally:
        postgres.close()
        mongo.close()
