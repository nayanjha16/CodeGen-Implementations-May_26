"""Persisted settings for database connections and FastAPI config."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from tool.config import LOCAL_DIR, SETTINGS_PATH, ToolConfig


@dataclass
class DatabaseConnection:
    id: str
    name: str
    host: str
    port: int
    database: str
    username: str
    password: str
    schema: str = "public"
    ssl_mode: str = "prefer"

    def to_sqlalchemy_url(self) -> str:
        from urllib.parse import quote_plus

        user = quote_plus(self.username)
        pwd = quote_plus(self.password)
        return f"postgresql+psycopg://{user}:{pwd}@{self.host}:{self.port}/{self.database}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DatabaseConnection:
        return cls(
            id=data["id"],
            name=data["name"],
            host=data["host"],
            port=int(data["port"]),
            database=data["database"],
            username=data["username"],
            password=data.get("password", ""),
            schema=data.get("schema", "public"),
            ssl_mode=data.get("ssl_mode", "prefer"),
        )


@dataclass
class FastApiSettings:
    base_url: str = "http://localhost:8000/v1"
    health_url: str = "http://localhost:8000/health"
    api_key: str = ""
    model: str = "codegen-text2sql"
    intent: str = "text2sql"
    timeout_sec: int = 60
    max_tokens: int = 256
    temperature: float = 0.2

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FastApiSettings:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


@dataclass
class SchemaSelectionSettings:
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    top_k: int = 8
    min_score: float = 0.3

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SchemaSelectionSettings:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


@dataclass
class ExecutionSettings:
    max_result_rows: int = 1000
    query_timeout_sec: int = 30
    schema_max_tables: int = 100

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExecutionSettings:
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


@dataclass
class AppSettings:
    active_connection_id: str | None = None
    connections: list[DatabaseConnection] = field(default_factory=list)
    fastapi: FastApiSettings = field(default_factory=FastApiSettings)
    schema_selection: SchemaSelectionSettings = field(default_factory=SchemaSelectionSettings)
    execution: ExecutionSettings = field(default_factory=ExecutionSettings)

    def get_active_connection(self) -> DatabaseConnection | None:
        if not self.active_connection_id:
            return None
        for conn in self.connections:
            if conn.id == self.active_connection_id:
                return conn
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_connection_id": self.active_connection_id,
            "connections": [c.to_dict() for c in self.connections],
            "fastapi": self.fastapi.to_dict(),
            "schema_selection": self.schema_selection.to_dict(),
            "execution": self.execution.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppSettings:
        return cls(
            active_connection_id=data.get("active_connection_id"),
            connections=[DatabaseConnection.from_dict(c) for c in data.get("connections", [])],
            fastapi=FastApiSettings.from_dict(data.get("fastapi", {})),
            schema_selection=SchemaSelectionSettings.from_dict(data.get("schema_selection", {})),
            execution=ExecutionSettings.from_dict(data.get("execution", {})),
        )


def _connection_from_database_url(url: str) -> DatabaseConnection | None:
    if not url:
        return None
    parsed = urlparse(url.replace("postgresql+psycopg://", "postgresql://"))
    if not parsed.hostname or not parsed.path:
        return None
    return DatabaseConnection(
        id=str(uuid.uuid4()),
        name="Default (from DATABASE_URL)",
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path.lstrip("/"),
        username=parsed.username or "postgres",
        password=parsed.password or "",
    )


def _default_settings(tool_config: ToolConfig | None = None) -> AppSettings:
    cfg = tool_config or ToolConfig.load()
    settings = AppSettings(
        fastapi=FastApiSettings(
            base_url=cfg.fastapi.base_url,
            health_url=cfg.fastapi.health_url,
            api_key=cfg.fastapi.api_key,
            model=cfg.fastapi.model,
            intent=cfg.fastapi.intent,
            timeout_sec=cfg.fastapi.timeout_sec,
            max_tokens=cfg.fastapi.max_tokens,
            temperature=cfg.fastapi.temperature,
        ),
        schema_selection=SchemaSelectionSettings(
            embedding_model=cfg.schema_selection.embedding_model,
            top_k=cfg.schema_selection.top_k,
            min_score=cfg.schema_selection.min_score,
        ),
        execution=ExecutionSettings(
            max_result_rows=cfg.execution.max_result_rows,
            query_timeout_sec=cfg.execution.query_timeout_sec,
            schema_max_tables=cfg.execution.schema_max_tables,
        ),
    )
    db_url = os.getenv("DATABASE_URL", "")
    conn = _connection_from_database_url(db_url)
    if conn:
        settings.connections.append(conn)
        settings.active_connection_id = conn.id
    return settings


class SettingsStore:
    """Load and save app settings to tool/.local/settings.json."""

    def __init__(self, path: Path | None = None):
        self.path = path or SETTINGS_PATH

    def load(self) -> AppSettings:
        LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            settings = _default_settings()
            self.save(settings)
            return settings
        with self.path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        return AppSettings.from_dict(data)

    def save(self, settings: AppSettings) -> None:
        LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(settings.to_dict(), fh, indent=2)

    def add_connection(self, settings: AppSettings, conn: DatabaseConnection) -> AppSettings:
        settings.connections.append(conn)
        if not settings.active_connection_id:
            settings.active_connection_id = conn.id
        self.save(settings)
        return settings

    def update_connection(self, settings: AppSettings, conn: DatabaseConnection) -> AppSettings:
        settings.connections = [c if c.id != conn.id else conn for c in settings.connections]
        self.save(settings)
        return settings

    def delete_connection(self, settings: AppSettings, conn_id: str) -> AppSettings:
        settings.connections = [c for c in settings.connections if c.id != conn_id]
        if settings.active_connection_id == conn_id:
            settings.active_connection_id = settings.connections[0].id if settings.connections else None
        self.save(settings)
        return settings
