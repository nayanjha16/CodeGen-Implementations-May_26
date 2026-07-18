"""Connection testing for PostgreSQL and FastAPI endpoints."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from tool.core.activity_logger import ActivityLogger
from tool.core.inference.fastapi_client import format_timeout_error
from tool.core.settings_store import DatabaseConnection, FastApiSettings


@dataclass
class TestResult:
    success: bool
    latency_ms: float
    server_version: str | None = None
    error: str | None = None
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "latency_ms": self.latency_ms,
            "server_version": self.server_version,
            "error": self.error,
            "details": self.details or {},
        }


def _build_engine(conn: DatabaseConnection, *, connect_timeout: int = 5) -> Engine:
    return create_engine(
        conn.to_sqlalchemy_url(),
        connect_args={"connect_timeout": connect_timeout},
        pool_pre_ping=True,
    )


def run_database_test(
    conn: DatabaseConnection,
    *,
    logger: ActivityLogger | None = None,
) -> TestResult:
    """Test PostgreSQL connectivity with SELECT 1."""
    start = time.perf_counter()
    try:
        engine = _build_engine(conn)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1 AS ok"))
            version_row = connection.execute(text("SELECT version()")).fetchone()
        latency = (time.perf_counter() - start) * 1000
        version = version_row[0] if version_row else None
        result = TestResult(success=True, latency_ms=latency, server_version=version)
        if logger:
            logger.info(
                stage="settings",
                event="connection_test_passed",
                message="Database connection test passed",
                details={"connection": conn.name, "latency_ms": round(latency, 1), "version": version},
            )
        return result
    except Exception as exc:
        latency = (time.perf_counter() - start) * 1000
        result = TestResult(success=False, latency_ms=latency, error=str(exc))
        if logger:
            logger.warning(
                stage="settings",
                event="connection_test_failed",
                message="Database connection test failed",
                details={"connection": conn.name, "error": str(exc)},
            )
        return result


def run_fastapi_test(
    config: FastApiSettings,
    *,
    logger: ActivityLogger | None = None,
) -> TestResult:
    """Test FastAPI health endpoint and optionally list models."""
    start = time.perf_counter()
    headers: dict[str, str] = {}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"

    try:
        with httpx.Client(timeout=config.timeout_sec) as client:
            health_resp = client.get(config.health_url, headers=headers)
            health_resp.raise_for_status()
            health_data = health_resp.json()

            models_data: dict[str, Any] | None = None
            models_url = config.base_url.rstrip("/") + "/models"
            try:
                models_resp = client.get(models_url, headers=headers)
                if models_resp.status_code == 200:
                    models_data = models_resp.json()
            except Exception:
                pass

        latency = (time.perf_counter() - start) * 1000
        details = {"health": health_data, "models": models_data}
        result = TestResult(success=True, latency_ms=latency, details=details)
        if logger:
            logger.info(
                stage="settings",
                event="api_test_passed",
                message="FastAPI health check passed",
                details={"latency_ms": round(latency, 1), "health": health_data},
            )
        return result
    except Exception as exc:
        latency = (time.perf_counter() - start) * 1000
        error = format_timeout_error(exc, config.timeout_sec)
        result = TestResult(success=False, latency_ms=latency, error=error)
        if logger:
            logger.warning(
                stage="settings",
                event="api_test_failed",
                message="FastAPI health check failed",
                details={"error": error, "timeout_sec": config.timeout_sec},
            )
        return result
