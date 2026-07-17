"""SQLAlchemy database engine from saved connection settings."""

from __future__ import annotations

from sqlalchemy.engine import Engine

from tool.core.settings_store import AppSettings, DatabaseConnection, SettingsStore


def get_engine_from_connection(conn: DatabaseConnection, *, query_timeout_sec: int = 30) -> Engine:
    from sqlalchemy import create_engine

    return create_engine(
        conn.to_sqlalchemy_url(),
        connect_args={"connect_timeout": 5},
        pool_pre_ping=True,
        execution_options={"postgresql_readonly": True},
    )


def get_active_engine(settings: AppSettings | None = None) -> tuple[Engine, DatabaseConnection]:
    """Return engine for the active saved connection."""
    app_settings = settings or SettingsStore().load()
    conn = app_settings.get_active_connection()
    if conn is None:
        raise RuntimeError("No active database connection configured. Add one in Settings.")
    engine = get_engine_from_connection(conn, query_timeout_sec=app_settings.execution.query_timeout_sec)
    return engine, conn
