"""MongoDB execution for TEND-loaded databases."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from agent.config.settings import AgentSettings, DatabaseProfileKind, get_settings
from agent.database._utils import mongo_collection_name
from agent.database.mongo_shell import ParsedShellQuery, ShellParseError, parse_shell_query
from agent.database.profiles import resolve_database_target


def _normalize_document(doc: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in doc.items():
        if isinstance(value, dict):
            normalized[str(key).lower()] = _normalize_document(value)
        elif isinstance(value, list):
            normalized[str(key).lower()] = [
                _normalize_document(item) if isinstance(item, dict) else item for item in value
            ]
        else:
            normalized[str(key).lower()] = value
    return normalized


@dataclass(frozen=True)
class MongoExecutionResult:
    rows: list[dict[str, Any]]
    scalar: int | float | None
    row_count: int
    truncated: bool = False
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


class MongoExecutor:
    """Execute Mongo shell queries on TEND or standalone Mongo databases."""

    def __init__(self, settings: AgentSettings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: MongoClient | None = None

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> MongoExecutor:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _client_or_connect(self) -> MongoClient:
        if self._client is None:
            self._client = MongoClient(
                self._settings.mongo.uri,
                serverSelectionTimeoutMS=5000,
            )
        return self._client

    def ping(self) -> bool:
        try:
            self._client_or_connect().admin.command("ping")
            return True
        except Exception:
            return False

    def list_collections(
        self,
        db_id: str | None = None,
        dataset: str | None = None,
        *,
        profile: DatabaseProfileKind | None = None,
    ) -> list[str]:
        target = resolve_database_target(
            db_id,
            dataset=dataset,
            profile=profile,
            settings=self._settings,
        )
        client = self._client_or_connect()
        return sorted(client[target.mongo_database].list_collection_names())

    def execute(
        self,
        query: str,
        db_id: str | None = None,
        dataset: str | None = None,
        *,
        profile: DatabaseProfileKind | None = None,
        max_rows: int | None = None,
    ) -> MongoExecutionResult:
        target = resolve_database_target(
            db_id,
            dataset=dataset,
            profile=profile,
            settings=self._settings,
        )
        max_rows = max_rows if max_rows is not None else self._settings.max_result_rows
        timeout_ms = self._settings.query_timeout_ms

        try:
            parsed = parse_shell_query(query)
        except ShellParseError as exc:
            return MongoExecutionResult([], None, 0, error=str(exc))

        client = self._client_or_connect()
        db = client[target.mongo_database]

        try:
            result = self._run_parsed(db, parsed, max_time_ms=timeout_ms, max_rows=max_rows)
        except Exception as exc:  # noqa: BLE001
            return MongoExecutionResult([], None, 0, error=str(exc))
        return result

    def _run_parsed(
        self,
        db: Database,
        parsed: ParsedShellQuery,
        *,
        max_time_ms: int,
        max_rows: int,
    ) -> MongoExecutionResult:
        collection_name = mongo_collection_name(parsed.collection)
        collection: Collection = db[collection_name]
        method = parsed.method

        if method == "find":
            filter_doc = parsed.args[0] if parsed.args else {}
            projection = parsed.args[1] if len(parsed.args) > 1 else None
            if not isinstance(filter_doc, dict):
                return MongoExecutionResult([], None, 0, error="find() filter must be an object")
            cursor = collection.find(filter_doc, projection, max_time_ms=max_time_ms)
            if parsed.sort:
                cursor = cursor.sort(list(parsed.sort.items()))
            if parsed.skip:
                cursor = cursor.skip(parsed.skip)
            limit = parsed.limit if parsed.limit is not None else max_rows + 1
            cursor = cursor.limit(limit)
            docs = [_normalize_document(doc) for doc in cursor]
            truncated = len(docs) > max_rows
            if truncated:
                docs = docs[:max_rows]
            return MongoExecutionResult(docs, None, len(docs), truncated=truncated)

        if method == "aggregate":
            pipeline = parsed.args[0] if parsed.args else []
            if not isinstance(pipeline, list):
                return MongoExecutionResult([], None, 0, error="aggregate() pipeline must be a list")
            docs = [
                _normalize_document(doc)
                for doc in collection.aggregate(pipeline, maxTimeMS=max_time_ms)
            ]
            truncated = len(docs) > max_rows
            if truncated:
                docs = docs[:max_rows]
            return MongoExecutionResult(docs, None, len(docs), truncated=truncated)

        if method == "countdocuments":
            filter_doc = parsed.args[0] if parsed.args else {}
            if not isinstance(filter_doc, dict):
                return MongoExecutionResult([], None, 0, error="countDocuments() filter must be an object")
            count = collection.count_documents(filter_doc, maxTimeMS=max_time_ms)
            return MongoExecutionResult([], count, 0)

        if method == "distinct":
            field = parsed.args[0] if parsed.args else None
            if not isinstance(field, str):
                return MongoExecutionResult([], None, 0, error="distinct() field must be a string")
            filter_doc = parsed.args[1] if len(parsed.args) > 1 else {}
            if filter_doc is not None and not isinstance(filter_doc, dict):
                return MongoExecutionResult([], None, 0, error="distinct() filter must be an object")
            values = collection.distinct(field, filter_doc or {}, maxTimeMS=max_time_ms)
            rows = [{field.lower(): value} for value in values[: max_rows + 1]]
            truncated = len(rows) > max_rows
            if truncated:
                rows = rows[:max_rows]
            return MongoExecutionResult(rows, None, len(rows), truncated=truncated)

        return MongoExecutionResult([], None, 0, error=f"Unsupported method: {method}")
