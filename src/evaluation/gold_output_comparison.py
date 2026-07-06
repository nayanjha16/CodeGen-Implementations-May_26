"""Compare live query execution against gold sql_output / nosql_output payloads."""

from __future__ import annotations

import json
from typing import Any

from src.evaluation.database_execution import ExecutionComparison, _ExecutionSession, is_database_available


def build_sql_vs_sql_diff_summary(
    predicted_sig: list[Any],
    reference_sig: list[Any],
) -> str:
    """Build a diff summary for text-to-SQL (predicted SQL vs reference SQL)."""
    if len(predicted_sig) != len(reference_sig):
        return (
            f"row count mismatch: predicted={len(predicted_sig)} "
            f"reference={len(reference_sig)}"
        )
    for index, (predicted_row, reference_row) in enumerate(
        zip(predicted_sig, reference_sig)
    ):
        if predicted_row != reference_row:
            return (
                f"first mismatch at row {index}: "
                f"predicted={predicted_row!r} reference={reference_row!r}"
            )
    return "results differ"


def build_mongo_vs_gold_diff_summary(
    predicted_sig: list[Any],
    gold_sig: list[Any],
    *,
    gold_label: str,
) -> str:
    """Build a diff summary for predicted MongoDB output vs a gold output payload."""
    if len(predicted_sig) != len(gold_sig):
        return (
            f"row count mismatch: predicted={len(predicted_sig)} "
            f"{gold_label}={len(gold_sig)}"
        )
    for index, (predicted_row, gold_row) in enumerate(zip(predicted_sig, gold_sig)):
        if predicted_row != gold_row:
            return (
                f"first mismatch at row {index}: "
                f"predicted={predicted_row!r} {gold_label}={gold_row!r}"
            )
    return "results differ"


def _parse_gold_sql_output(raw: str) -> tuple[Any | None, str | None]:
    """Return a TEND SqlExecutionResult-compatible object or an error message."""
    from src.evaluation.database_execution import _load_tend_modules

    if not raw.strip():
        return None, "missing gold sql_output"

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, f"invalid gold sql_output json: {exc}"

    if isinstance(payload, dict) and "error" in payload:
        return None, f"gold sql_output error: {payload['error']}"
    if not isinstance(payload, list):
        return None, "invalid gold sql_output: expected row array"

    modules = _load_tend_modules()
    SqlExecutionResult = modules["SqlExecutionResult"]
    return SqlExecutionResult(rows=payload, row_count=len(payload), error=None), None


def _parse_gold_mongo_output(raw: str) -> tuple[Any | None, str | None]:
    """Return a TEND MongoExecutionResult-compatible object or an error message."""
    from src.evaluation.database_execution import _load_tend_modules

    if not raw.strip():
        return None, "missing gold nosql_output"

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, f"invalid gold nosql_output json: {exc}"

    if isinstance(payload, dict):
        if "error" in payload:
            return None, f"gold nosql_output error: {payload['error']}"
        if "value" in payload:
            modules = _load_tend_modules()
            MongoExecutionResult = modules["MongoExecutionResult"]
            scalar = payload["value"]
            return (
                MongoExecutionResult(
                    rows=[],
                    scalar=scalar,
                    row_count=1,
                    error=None,
                ),
                None,
            )
        return None, "invalid gold nosql_output: expected value or row array"

    if isinstance(payload, list):
        modules = _load_tend_modules()
        MongoExecutionResult = modules["MongoExecutionResult"]
        return (
            MongoExecutionResult(
                rows=payload,
                scalar=None,
                row_count=len(payload),
                error=None,
            ),
            None,
        )

    return None, "invalid gold nosql_output: unsupported payload type"


def _signature_from_gold_sql_output(
    raw: str,
    *,
    order_sensitive: bool,
) -> tuple[list[Any], str | None]:
    from src.evaluation.database_execution import _load_tend_modules

    result, error = _parse_gold_sql_output(raw)
    if error:
        return [], error
    modules = _load_tend_modules()
    return modules["_sql_signature"](result, order_sensitive=order_sensitive), None


def _signature_from_gold_mongo_output(
    raw: str,
    *,
    order_sensitive: bool,
) -> tuple[list[Any], str | None]:
    from src.evaluation.database_execution import _load_tend_modules

    result, error = _parse_gold_mongo_output(raw)
    if error:
        return [], error
    modules = _load_tend_modules()
    return modules["_mongo_signature"](result, order_sensitive=order_sensitive), None


def compare_predicted_sql_to_gold_output(
    predicted_sql: str,
    gold_sql_output: str,
    *,
    reference_sql: str = "",
    db_id: str,
    dataset: str = "spider",
    session: _ExecutionSession | None = None,
) -> ExecutionComparison:
    """Execute predicted SQL and compare against gold sql_output using TEND rules."""
    if not predicted_sql.strip() or not db_id.strip():
        return ExecutionComparison(match=False, error="missing sql or db_id")
    if not gold_sql_output.strip():
        return ExecutionComparison(match=False, error="missing gold sql_output")
    if not is_database_available():
        return ExecutionComparison(match=False, error="database execution unavailable")

    from src.evaluation.database_execution import _load_tend_modules

    modules = _load_tend_modules()
    order_sensitive = modules["is_order_sensitive"](
        sql_query=predicted_sql,
        nosql_query=reference_sql or predicted_sql,
    )
    gold_sig, gold_error = _signature_from_gold_sql_output(
        gold_sql_output,
        order_sensitive=order_sensitive,
    )
    if gold_error:
        return ExecutionComparison(match=False, error=gold_error)

    if session is None:
        with _ExecutionSession() as owned:
            return _compare_predicted_sql_signature_to_gold(
                owned,
                predicted_sql=predicted_sql,
                gold_sig=gold_sig,
                order_sensitive=order_sensitive,
                db_id=db_id,
                dataset=dataset,
            )
    return _compare_predicted_sql_signature_to_gold(
        session,
        predicted_sql=predicted_sql,
        gold_sig=gold_sig,
        order_sensitive=order_sensitive,
        db_id=db_id,
        dataset=dataset,
    )


def _compare_predicted_sql_signature_to_gold(
    session: _ExecutionSession,
    *,
    predicted_sql: str,
    gold_sig: list[Any],
    order_sensitive: bool,
    db_id: str,
    dataset: str,
) -> ExecutionComparison:
    conn = session._pg_conn(dataset)
    pred_result = session._execute_sql_query(
        session._config.postgres,
        dataset=dataset,
        db_id=db_id,
        sql_query=predicted_sql,
        conn=conn,
        statement_timeout_ms=10_000,
    )
    if not pred_result.ok:
        return ExecutionComparison(
            match=False,
            error=pred_result.error,
            diff_summary=f"predicted sql error: {pred_result.error}",
        )

    pred_sig = session._sql_signature(pred_result, order_sensitive=order_sensitive)
    match = pred_sig == gold_sig
    return ExecutionComparison(
        match=match,
        diff_summary=None
        if match
        else build_sql_vs_sql_diff_summary(pred_sig, gold_sig),
    )


def compare_predicted_mongo_to_gold_outputs(
    predicted_mongo: str,
    gold_nosql_output: str,
    *,
    gold_sql_output: str = "",
    reference_sql: str = "",
    reference_mongo_query: str = "",
    db_id: str,
    dataset: str = "spider",
    session: _ExecutionSession | None = None,
) -> tuple[ExecutionComparison, ExecutionComparison | None]:
    """Compare predicted MongoDB output against gold nosql_output and optional sql_output."""
    if not predicted_mongo.strip() or not db_id.strip():
        empty = ExecutionComparison(match=False, error="missing query or db_id")
        return empty, None
    if not gold_nosql_output.strip():
        empty = ExecutionComparison(match=False, error="missing gold nosql_output")
        return empty, None
    if not is_database_available():
        empty = ExecutionComparison(match=False, error="database execution unavailable")
        return empty, None

    from src.evaluation.database_execution import _load_tend_modules

    modules = _load_tend_modules()
    order_sensitive = modules["is_order_sensitive"](
        sql_query=reference_sql or "",
        nosql_query=reference_mongo_query or predicted_mongo,
    )
    gold_nosql_sig, gold_nosql_error = _signature_from_gold_mongo_output(
        gold_nosql_output,
        order_sensitive=order_sensitive,
    )
    if gold_nosql_error:
        empty = ExecutionComparison(match=False, error=gold_nosql_error)
        return empty, None

    gold_sql_comparison: ExecutionComparison | None = None
    gold_sql_sig: list[Any] | None = None
    if gold_sql_output.strip():
        gold_sql_sig, gold_sql_error = _signature_from_gold_sql_output(
            gold_sql_output,
            order_sensitive=order_sensitive,
        )
        if gold_sql_error:
            gold_sql_comparison = ExecutionComparison(match=False, error=gold_sql_error)
        else:
            gold_sql_sig = gold_sql_sig

    if session is None:
        with _ExecutionSession() as owned:
            nosql_comparison = _compare_predicted_mongo_signature_to_gold(
                owned,
                predicted_mongo=predicted_mongo,
                gold_sig=gold_nosql_sig,
                gold_label="gold_nosql",
                order_sensitive=order_sensitive,
                db_id=db_id,
                dataset=dataset,
            )
            if gold_sql_sig is not None and gold_sql_comparison is None:
                gold_sql_comparison = _compare_predicted_mongo_signature_to_gold(
                    owned,
                    predicted_mongo=predicted_mongo,
                    gold_sig=gold_sql_sig,
                    gold_label="gold_sql",
                    order_sensitive=order_sensitive,
                    db_id=db_id,
                    dataset=dataset,
                )
            return nosql_comparison, gold_sql_comparison

    nosql_comparison = _compare_predicted_mongo_signature_to_gold(
        session,
        predicted_mongo=predicted_mongo,
        gold_sig=gold_nosql_sig,
        gold_label="gold_nosql",
        order_sensitive=order_sensitive,
        db_id=db_id,
        dataset=dataset,
    )
    if gold_sql_sig is not None and gold_sql_comparison is None:
        gold_sql_comparison = _compare_predicted_mongo_signature_to_gold(
            session,
            predicted_mongo=predicted_mongo,
            gold_sig=gold_sql_sig,
            gold_label="gold_sql",
            order_sensitive=order_sensitive,
            db_id=db_id,
            dataset=dataset,
        )
    return nosql_comparison, gold_sql_comparison


def _compare_predicted_mongo_signature_to_gold(
    session: _ExecutionSession,
    *,
    predicted_mongo: str,
    gold_sig: list[Any],
    gold_label: str,
    order_sensitive: bool,
    db_id: str,
    dataset: str,
) -> ExecutionComparison:
    conn = session._pg_conn(dataset)
    mongo_result = session._execute_mongo_query(
        session._config.mongo,
        dataset=dataset,
        db_id=db_id,
        nosql_query=predicted_mongo,
        client=session._mongo,
        max_time_ms=10_000,
        string_columns=session._text_columns_for_schema(
            conn,
            session._sanitize_pg_schema_name(db_id),
        ),
    )
    if not mongo_result.ok:
        return ExecutionComparison(
            match=False,
            error=mongo_result.error,
            diff_summary=f"predicted mongo error: {mongo_result.error}",
        )

    pred_sig = session._mongo_signature(
        mongo_result,
        order_sensitive=order_sensitive,
    )
    match = pred_sig == gold_sig
    return ExecutionComparison(
        match=match,
        diff_summary=None
        if match
        else build_mongo_vs_gold_diff_summary(
            pred_sig,
            gold_sig,
            gold_label=gold_label,
        ),
    )
