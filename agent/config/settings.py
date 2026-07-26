"""Agent configuration loaded from environment / .env."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from typing import Literal

_REPO_ROOT = Path(__file__).resolve().parents[2]
_AGENT_ROOT = Path(__file__).resolve().parents[1]

DatabaseProfileKind = Literal["tend", "standalone"]


def _load_env_files() -> None:
    agent_env = _AGENT_ROOT / ".env"
    repo_env = _REPO_ROOT / ".env"
    if agent_env.is_file():
        load_dotenv(agent_env, override=True)
    if repo_env.is_file():
        load_dotenv(repo_env, override=False)


@dataclass(frozen=True)
class PostgresSettings:
    host: str
    port: int
    user: str
    password: str
    admin_db: str

    def dsn(self, database: str) -> str:
        return (
            f"host={self.host} port={self.port} dbname={database} "
            f"user={self.user} password={self.password}"
        )

    def catalog_name(self, dataset: str) -> str:
        return f"tend_{dataset}"


@dataclass(frozen=True)
class MongoSettings:
    host: str
    port: int
    user: str
    password: str

    @property
    def uri(self) -> str:
        if self.user:
            return (
                f"mongodb://{self.user}:{self.password}"
                f"@{self.host}:{self.port}/?authSource=admin"
            )
        return f"mongodb://{self.host}:{self.port}/"


@dataclass(frozen=True)
class StandaloneDatabaseSettings:
    """Custom Postgres DB loaded from your own SQL dump — not TEND tend_{dataset}."""

    db_id: str
    postgres_database: str
    postgres_schema: str
    mongo_database: str
    sql_dump: Path | None


@dataclass(frozen=True)
class AgentSettings:
    postgres: PostgresSettings
    mongo: MongoSettings
    demo: StandaloneDatabaseSettings
    codegen_api_url: str
    codegen_api_key: str
    codegen_model: str
    codegen_timeout_sec: int
    codegen_max_tokens: int
    codegen_temperature: float
    ollama_base_url: str
    ollama_model: str
    database_profile: DatabaseProfileKind
    default_dataset: str
    max_result_rows: int
    max_retries: int
    query_timeout_ms: int

    @classmethod
    def from_env(cls) -> AgentSettings:
        _load_env_files()
        return cls(
            postgres=PostgresSettings(
                host=os.environ.get("POSTGRES_HOST", "localhost"),
                port=int(os.environ.get("POSTGRES_PORT", "5432")),
                user=os.environ.get("POSTGRES_USER", "tend"),
                password=os.environ.get("POSTGRES_PASSWORD", "tend"),
                admin_db=os.environ.get("POSTGRES_ADMIN_DB", "postgres"),
            ),
            mongo=MongoSettings(
                host=os.environ.get("MONGO_HOST", "localhost"),
                port=int(os.environ.get("MONGO_PORT", "27017")),
                user=os.environ.get("MONGO_USER", "tend"),
                password=os.environ.get("MONGO_PASSWORD", "tend"),
            ),
            demo=_standalone_settings_from_env(),
            codegen_api_url=os.environ.get(
                "CODEGEN_API_URL",
                "https://codegen-api-161349047936.asia-south2.run.app",
            ).rstrip("/"),
            codegen_api_key=os.environ.get("CODEGEN_API_KEY", ""),
            codegen_model=os.environ.get("CODEGEN_MODEL", "codegen-text2sql"),
            codegen_timeout_sec=int(os.environ.get("CODEGEN_TIMEOUT_SEC", "120")),
            codegen_max_tokens=int(os.environ.get("CODEGEN_MAX_TOKENS", "256")),
            codegen_temperature=float(os.environ.get("CODEGEN_TEMPERATURE", "0.2")),
            ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip(
                "/"
            ),
            ollama_model=os.environ.get("AGENT_ORCHESTRATOR_MODEL", "gemma3:4b"),
            database_profile=_parse_database_profile(
                os.environ.get("AGENT_DB_PROFILE", "tend")
            ),
            default_dataset=os.environ.get("AGENT_DEFAULT_DATASET", "spider"),
            max_result_rows=int(os.environ.get("AGENT_MAX_RESULT_ROWS", "100")),
            max_retries=int(os.environ.get("AGENT_MAX_RETRIES", "3")),
            query_timeout_ms=int(os.environ.get("AGENT_QUERY_TIMEOUT_MS", "10000")),
        )


def _standalone_settings_from_env() -> StandaloneDatabaseSettings:
    dump_raw = os.environ.get("AGENT_DEMO_SQL_DUMP", "").strip()
    sql_dump = Path(dump_raw) if dump_raw else None
    db_id = os.environ.get("AGENT_DEMO_DB_ID", "").strip()
    return StandaloneDatabaseSettings(
        db_id=db_id,
        postgres_database=os.environ.get("AGENT_DEMO_POSTGRES_DATABASE", db_id).strip(),
        postgres_schema=os.environ.get("AGENT_DEMO_POSTGRES_SCHEMA", "public"),
        mongo_database=os.environ.get("AGENT_DEMO_MONGO_DATABASE", db_id).strip(),
        sql_dump=sql_dump,
    )


def _parse_database_profile(value: str) -> DatabaseProfileKind:
    normalized = value.strip().lower()
    if normalized in {"tend", "standalone", "demo"}:
        if normalized == "demo":
            return "standalone"
        return normalized  # type: ignore[return-value]
    raise ValueError(
        f"Invalid AGENT_DB_PROFILE={value!r}. Expected tend or standalone."
    )


@lru_cache(maxsize=1)
def get_settings() -> AgentSettings:
    return AgentSettings.from_env()
