"""Tool configuration loaded from config.yaml and environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parent
LOCAL_DIR = TOOL_DIR / ".local"
SETTINGS_PATH = LOCAL_DIR / "settings.json"


@dataclass
class FastApiConfig:
    base_url: str = "http://localhost:8000/v1"
    health_url: str = "http://localhost:8000/health"
    api_key: str = ""
    model: str = "codegen-text2sql"
    intent: str = "text2sql"
    timeout_sec: int = 60
    max_tokens: int = 256
    temperature: float = 0.2


@dataclass
class SchemaSelectionConfig:
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    top_k: int = 8
    min_score: float = 0.3


@dataclass
class ExecutionConfig:
    max_result_rows: int = 1000
    query_timeout_sec: int = 30
    schema_max_tables: int = 100


@dataclass
class AppConfig:
    title: str = "AI SQL Assistant"
    page_icon: str = "🗄️"
    layout: str = "wide"


@dataclass
class ToolConfig:
    app: AppConfig = field(default_factory=AppConfig)
    fastapi: FastApiConfig = field(default_factory=FastApiConfig)
    schema_selection: SchemaSelectionConfig = field(default_factory=SchemaSelectionConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)

    @classmethod
    def load(cls, config_path: Path | None = None) -> ToolConfig:
        load_dotenv(TOOL_DIR / ".env")
        path = config_path or TOOL_DIR / "config.yaml"
        raw: dict[str, Any] = {}
        if path.exists():
            with path.open(encoding="utf-8") as fh:
                raw = yaml.safe_load(fh) or {}

        app_raw = raw.get("app", {})
        fastapi_raw = raw.get("fastapi", {})
        schema_raw = raw.get("schema_selection", {})
        exec_raw = raw.get("execution", {})

        return cls(
            app=AppConfig(
                title=app_raw.get("title", "AI SQL Assistant"),
                page_icon=app_raw.get("page_icon", "🗄️"),
                layout=app_raw.get("layout", "wide"),
            ),
            fastapi=FastApiConfig(
                base_url=os.getenv("FASTAPI_BASE_URL", fastapi_raw.get("base_url", "http://localhost:8000/v1")),
                health_url=os.getenv(
                    "FASTAPI_HEALTH_URL",
                    fastapi_raw.get("health_url", "http://localhost:8000/health"),
                ),
                api_key=os.getenv("FASTAPI_API_KEY", fastapi_raw.get("api_key", "")),
                model=os.getenv("FASTAPI_MODEL", fastapi_raw.get("model", "codegen-text2sql")),
                intent=os.getenv("FASTAPI_INTENT", fastapi_raw.get("intent", "text2sql")),
                timeout_sec=int(os.getenv("FASTAPI_TIMEOUT_SEC", fastapi_raw.get("timeout_sec", 60))),
                max_tokens=int(os.getenv("FASTAPI_MAX_TOKENS", fastapi_raw.get("max_tokens", 256))),
                temperature=float(fastapi_raw.get("temperature", 0.2)),
            ),
            schema_selection=SchemaSelectionConfig(
                embedding_model=os.getenv(
                    "SCHEMA_EMBEDDING_MODEL",
                    schema_raw.get("embedding_model", "BAAI/bge-small-en-v1.5"),
                ),
                top_k=int(os.getenv("SCHEMA_TOP_K", schema_raw.get("top_k", 8))),
                min_score=float(os.getenv("SCHEMA_MIN_SCORE", schema_raw.get("min_score", 0.3))),
            ),
            execution=ExecutionConfig(
                max_result_rows=int(os.getenv("MAX_RESULT_ROWS", exec_raw.get("max_result_rows", 1000))),
                query_timeout_sec=int(os.getenv("QUERY_TIMEOUT_SEC", exec_raw.get("query_timeout_sec", 30))),
                schema_max_tables=int(os.getenv("SCHEMA_MAX_TABLES", exec_raw.get("schema_max_tables", 100))),
            ),
        )
