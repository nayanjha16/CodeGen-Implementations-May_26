"""MongoDB client helpers from saved connection settings."""

from __future__ import annotations

from pymongo import MongoClient

from tool.core.settings_store import AppSettings, MongoConnection, SettingsStore


def mongo_client_from_connection(conn: MongoConnection, *, server_selection_timeout_ms: int = 5000) -> MongoClient:
    return MongoClient(
        host=conn.host,
        port=conn.port,
        username=conn.username or None,
        password=conn.password or None,
        authSource=conn.auth_source,
        serverSelectionTimeoutMS=server_selection_timeout_ms,
    )


def get_active_mongo_client(settings: AppSettings | None = None) -> tuple[MongoClient, MongoConnection]:
    app_settings = settings or SettingsStore().load()
    conn = app_settings.get_active_mongo_connection()
    if conn is None:
        raise RuntimeError("No active MongoDB connection configured. Add one in Settings.")
    client = mongo_client_from_connection(conn)
    return client, conn
