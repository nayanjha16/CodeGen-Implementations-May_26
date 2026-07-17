"""Pytest fixtures for tool tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tool.core.settings_store import AppSettings, DatabaseConnection, SettingsStore


@pytest.fixture
def settings_path(tmp_path: Path) -> Path:
    return tmp_path / "settings.json"


@pytest.fixture
def settings_store(settings_path: Path) -> SettingsStore:
    return SettingsStore(path=settings_path)


@pytest.fixture
def sample_connection() -> DatabaseConnection:
    return DatabaseConnection(
        id="conn-test",
        name="Test DB",
        host="localhost",
        port=5432,
        database="testdb",
        username="postgres",
        password="secret",
        schema="public",
    )


@pytest.fixture
def app_settings(sample_connection: DatabaseConnection) -> AppSettings:
    settings = AppSettings()
    settings.connections = [sample_connection]
    settings.active_connection_id = sample_connection.id
    return settings
