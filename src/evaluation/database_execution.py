"""Execute SQL and MongoDB queries against TEND database environments."""

from __future__ import annotations

import importlib
import logging
import os
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger("codegen")

DEFAULT_TEND_REPO_PATH = "/Volumes/Work/TEND"
DEFAULT_EXECUTION_TIMEOUT_MS = 10_000


@dataclass(frozen=True)
class ExecutionComparison:
    """Outcome of comparing two query execution results."""

    match: bool
    error: str | None = None
    diff_summary: str | None = None


def _resolve_tend_repo_path() -> Path:
    raw = os.environ.get("TEND_REPO_PATH", DEFAULT_TEND_REPO_PATH).strip()
    return Path(raw).expanduser().resolve()


@lru_cache(maxsize=1)
def _load_tend_modules() -> dict[str, Any]:
    """Import TEND database modules without conflicting with this project's ``src`` package."""
    tend_root = _resolve_tend_repo_path()
    if not tend_root.is_dir():
        raise ImportError(f"TEND repository not found at {tend_root}")

    saved_path = sys.path[:]
    saved_src_modules = {
        key: value for key, value in sys.modules.items() if key == "src" or key.startswith("src.")
    }
    for key in saved_src_modules:
        del sys.modules[key]

    try:
        sys.path.insert(0, str(tend_root))
        return {
            "load_database_config": importlib.import_module(
                "src.database.config"
            ).load_database_config,
            "mongo_client": importlib.import_module("src.database.connections").mongo_client,
            "compare_query_results": importlib.import_module(
                "src.database.execution.result_comparator"
            ).compare_query_results,
            "execute_mongo_query": importlib.import_module(
                "src.database.mongodb.executor"
            ).execute_mongo_query,
            "execute_sql_query": importlib.import_module(
                "src.database.postgres.executor"
            ).execute_sql_query,
            "text_columns_for_schema": importlib.import_module(
                "src.database.postgres.executor"
            ).text_columns_for_schema,
            "sanitize_pg_schema_name": importlib.import_module(
                "src.database.utils"
            ).sanitize_pg_schema_name,
            "ComparisonResult": importlib.import_module(
                "src.database.execution.result_comparator"
            ).ComparisonResult,
            "_build_diff_summary": importlib.import_module(
                "src.database.execution.result_comparator"
            )._build_diff_summary,
            "_sql_signature": importlib.import_module(
                "src.database.execution.result_comparator"
            )._sql_signature,
            "_mongo_signature": importlib.import_module(
                "src.database.execution.result_comparator"
            )._mongo_signature,
            "is_order_sensitive": importlib.import_module(
                "src.database.execution.result_comparator"
            ).is_order_sensitive,
            "SqlExecutionResult": importlib.import_module(
                "src.database.postgres.executor"
            ).SqlExecutionResult,
            "MongoExecutionResult": importlib.import_module(
                "src.database.mongodb.executor"
            ).MongoExecutionResult,
        }
    finally:
        for key, value in saved_src_modules.items():
            sys.modules[key] = value
        sys.path[:] = saved_path


def is_database_available() -> bool:
    """Return True when TEND database execution modules can be imported."""
    try:
        _load_tend_modules()
        return True
    except ImportError:
        return False


class _ExecutionSession:
    """Reuse PostgreSQL and MongoDB connections for a batch of comparisons."""

    def __init__(self) -> None:
        import psycopg

        modules = _load_tend_modules()
        self._psycopg = psycopg
        self._config = modules["load_database_config"]()
        self._compare_query_results = modules["compare_query_results"]
        self._execute_sql_query = modules["execute_sql_query"]
        self._execute_mongo_query = modules["execute_mongo_query"]
        self._text_columns_for_schema = modules["text_columns_for_schema"]
        self._sanitize_pg_schema_name = modules["sanitize_pg_schema_name"]
        self._ComparisonResult = modules["ComparisonResult"]
        self._build_diff_summary = modules["_build_diff_summary"]
        self._sql_signature = modules["_sql_signature"]
        self._mongo_signature = modules["_mongo_signature"]
        self._is_order_sensitive = modules["is_order_sensitive"]
        self._mongo = modules["mongo_client"](self._config.mongo)
        self._pg: dict[str, Any] = {}

    def close(self) -> None:
        for conn in self._pg.values():
            conn.close()
        self._pg.clear()
        self._mongo.close()

    def __enter__(self) -> _ExecutionSession:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _pg_conn(self, dataset: str) -> Any:
        catalog = self._config.postgres.catalog_name(dataset)
        if catalog not in self._pg:
            self._pg[catalog] = self._psycopg.connect(
                self._config.postgres.dsn(catalog),
                autocommit=False,
                connect_timeout=5,
            )
        return self._pg[catalog]

    def compare_sql(
        self,
        *,
        dataset: str,
        db_id: str,
        predicted_sql: str,
        reference_sql: str,
        query_timeout_ms: int = DEFAULT_EXECUTION_TIMEOUT_MS,
    ) -> ExecutionComparison:
        """Execute predicted and reference SQL on PostgreSQL and compare results."""
        conn = self._pg_conn(dataset)
        pred_result = self._execute_sql_query(
            self._config.postgres,
            dataset=dataset,
            db_id=db_id,
            sql_query=predicted_sql,
            conn=conn,
            statement_timeout_ms=query_timeout_ms,
        )
        ref_result = self._execute_sql_query(
            self._config.postgres,
            dataset=dataset,
            db_id=db_id,
            sql_query=reference_sql,
            conn=conn,
            statement_timeout_ms=query_timeout_ms,
        )

        if not pred_result.ok:
            return ExecutionComparison(
                match=False,
                error=pred_result.error,
                diff_summary=f"predicted sql error: {pred_result.error}",
            )
        if not ref_result.ok:
            return ExecutionComparison(
                match=False,
                error=ref_result.error,
                diff_summary=f"reference sql error: {ref_result.error}",
            )

        comparison = self._compare_sql_results(
            pred_result,
            ref_result,
            predicted_sql=predicted_sql,
            reference_sql=reference_sql,
        )
        return ExecutionComparison(
            match=comparison.match,
            diff_summary=comparison.diff_summary,
        )

    def compare_sql_to_mongo(
        self,
        *,
        dataset: str,
        db_id: str,
        reference_sql: str,
        predicted_mongo: str,
        query_timeout_ms: int = DEFAULT_EXECUTION_TIMEOUT_MS,
    ) -> ExecutionComparison:
        """Compare reference SQL (PostgreSQL) against predicted MongoDB query."""
        conn = self._pg_conn(dataset)
        sql_result = self._execute_sql_query(
            self._config.postgres,
            dataset=dataset,
            db_id=db_id,
            sql_query=reference_sql,
            conn=conn,
            statement_timeout_ms=query_timeout_ms,
        )
        if not sql_result.ok:
            return ExecutionComparison(
                match=False,
                error=sql_result.error,
                diff_summary=f"reference sql error: {sql_result.error}",
            )

        mongo_result = self._execute_mongo_query(
            self._config.mongo,
            dataset=dataset,
            db_id=db_id,
            nosql_query=predicted_mongo,
            client=self._mongo,
            max_time_ms=query_timeout_ms,
            string_columns=self._text_columns_for_schema(
                conn,
                self._sanitize_pg_schema_name(db_id),
            ),
        )
        comparison = self._compare_query_results(
            sql_result=sql_result,
            mongo_result=mongo_result,
            sql_query=reference_sql,
            nosql_query=predicted_mongo,
        )
        return ExecutionComparison(
            match=comparison.match,
            diff_summary=comparison.diff_summary,
        )

    def _compare_sql_results(
        self,
        pred_result: Any,
        ref_result: Any,
        *,
        predicted_sql: str,
        reference_sql: str,
    ) -> Any:
        """Compare two SQL execution results using TEND normalization rules."""
        order_sensitive = self._is_order_sensitive(
            sql_query=predicted_sql,
            nosql_query=reference_sql,
        )
        pred_sig = self._sql_signature(pred_result, order_sensitive=order_sensitive)
        ref_sig = self._sql_signature(ref_result, order_sensitive=order_sensitive)
        match = pred_sig == ref_sig
        from src.evaluation.gold_output_comparison import build_sql_vs_sql_diff_summary

        return self._ComparisonResult(
            match=match,
            order_sensitive=order_sensitive,
            sql_signature=pred_sig,
            mongo_signature=ref_sig,
            diff_summary=None
            if match
            else build_sql_vs_sql_diff_summary(pred_sig, ref_sig),
        )


def compare_sql_execution(
    predicted_sql: str,
    reference_sql: str,
    *,
    db_id: str,
    dataset: str = "spider",
    session: _ExecutionSession | None = None,
) -> ExecutionComparison:
    """Compare predicted and reference SQL execution results on PostgreSQL."""
    if not predicted_sql.strip() or not reference_sql.strip() or not db_id.strip():
        return ExecutionComparison(match=False, error="missing sql or db_id")

    if session is not None:
        return session.compare_sql(
            dataset=dataset,
            db_id=db_id,
            predicted_sql=predicted_sql,
            reference_sql=reference_sql,
        )

    with _ExecutionSession() as owned:
        return owned.compare_sql(
            dataset=dataset,
            db_id=db_id,
            predicted_sql=predicted_sql,
            reference_sql=reference_sql,
        )


def compare_sql_to_mongo_execution(
    reference_sql: str,
    predicted_mongo: str,
    *,
    db_id: str,
    dataset: str = "spider",
    session: _ExecutionSession | None = None,
) -> ExecutionComparison:
    """Compare reference SQL (PostgreSQL) against predicted MongoDB query."""
    if not reference_sql.strip() or not predicted_mongo.strip() or not db_id.strip():
        return ExecutionComparison(match=False, error="missing query or db_id")

    if session is not None:
        return session.compare_sql_to_mongo(
            dataset=dataset,
            db_id=db_id,
            reference_sql=reference_sql,
            predicted_mongo=predicted_mongo,
        )

    with _ExecutionSession() as owned:
        return owned.compare_sql_to_mongo(
            dataset=dataset,
            db_id=db_id,
            reference_sql=reference_sql,
            predicted_mongo=predicted_mongo,
        )
