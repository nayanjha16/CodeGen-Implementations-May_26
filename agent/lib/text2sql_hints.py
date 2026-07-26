"""Heuristics for text2sql question hints and safe result summaries."""

from __future__ import annotations

import json
import re
from typing import Any

_AGGREGATE_QUESTION_RE = re.compile(
    r"\b("
    r"how many|how much|count|number of|total|sum|average|avg|"
    r"most|least|top\s+\d+|highest|lowest|maximum|minimum|max|min"
    r")\b",
    re.IGNORECASE,
)
_LIST_QUESTION_RE = re.compile(r"\b(list|show|display|give me|return|get)\b", re.IGNORECASE)


def question_needs_aggregate_in_select(question: str) -> bool:
    return bool(_AGGREGATE_QUESTION_RE.search(question))


def question_is_open_listing(question: str) -> bool:
    lowered = question.lower()
    if not _LIST_QUESTION_RE.search(question):
        return False
    # Specific filter cues — "customers from Brazil", "albums by AC/DC"
    if re.search(r"\b(from|where|named|called|for|in|by)\b", lowered):
        if not re.search(r"\b(with|and)\b", lowered):
            return False
    return True


def augment_codegen_question(question: str, allowed_tables: set[str] | None = None) -> str:
    """Add table and aggregate hints for CodeGen without changing src/ prompts."""
    parts = [question.strip()]
    if allowed_tables and len(allowed_tables) <= 5:
        table_list = ", ".join(f'"{name}"' for name in sorted(allowed_tables))
        parts.append(
            f"Use only these tables with exact quoted names: {table_list}."
        )
        if len(allowed_tables) > 1:
            parts.append("Join them using foreign keys from the schema.")
    if question_needs_aggregate_in_select(question):
        parts.append(
            "If the question asks for a count, total, or ranking, include the "
            "aggregate (COUNT, SUM, AVG, etc.) in the SELECT list — not only in "
            "ORDER BY or GROUP BY."
        )
    if question_is_open_listing(question):
        parts.append(
            "Return all matching rows. Do not add WHERE filters unless the question "
            "names a specific value to match. Never filter using schema keywords."
        )
        if re.search(r"\bwith\b", question, re.IGNORECASE):
            parts.append(
                "When the question joins entities (e.g. albums with artists), "
                "include columns from each mentioned table in the SELECT list."
            )
    return "\n\n".join(part for part in parts if part)


def _rows_include_numeric_values(rows: list[dict[str, Any]]) -> bool:
    for row in rows:
        for value in row.values():
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                return True
    return False


def _missing_requested_fields(question: str, rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return []
    columns = {str(key).lower() for key in rows[0].keys()}
    lowered = question.lower()
    missing: list[str] = []

    def _has_column(*needles: str) -> bool:
        return any(
            any(needle in column for needle in needles)
            for column in columns
        )

    if re.search(r"\bartist", lowered) and not _has_column("artist", "name"):
        missing.append("artist name")
    if re.search(r"\balbum", lowered) and not _has_column("album", "title"):
        missing.append("album title")
    if re.search(r"\bgenre", lowered) and not _has_column("genre"):
        missing.append("genre")
    if re.search(r"\bcustomer", lowered) and not _has_column("customer", "firstname", "lastname"):
        missing.append("customer name")
    if re.search(r"\btrack", lowered) and not _has_column("track"):
        missing.append("track name")

    return missing


def format_listing_summary(
    *,
    question: str,
    rows: list[dict[str, Any]] | None,
    error: str | None = None,
) -> str | None:
    """Factual summary for list/show queries — avoids claiming columns that aren't returned."""
    if error or not rows or not question_is_open_listing(question):
        return None

    columns = list(rows[0].keys())
    missing = _missing_requested_fields(question, rows)
    if missing:
        col_list = ", ".join(columns)
        return (
            f"The query returned {len(rows)} row(s) with column(s): {col_list}. "
            f"The question asked for {' and '.join(missing)}, but the SQL SELECT "
            f"does not include those fields — see the SQL and results table below."
        )

    if len(columns) >= 2 and len(rows) > 0:
        examples = []
        for row in rows[:3]:
            parts = [f"{key}: {row[key]}" for key in columns[:3] if key in row]
            examples.append("; ".join(parts))
        preview = " | ".join(examples)
        extra = f" (and {len(rows) - 3} more rows)" if len(rows) > 3 else ""
        return (
            f"The query returned {len(rows)} row(s) with columns: {', '.join(columns)}. "
            f"Examples: {preview}{extra}. See the results table below."
        )

    if len(columns) == 1 and len(rows) > 0:
        col = columns[0]
        examples = [str(row[col]) for row in rows[:3] if col in row]
        preview = ", ".join(examples)
        extra = f" (and {len(rows) - 3} more)" if len(rows) > 3 else ""
        return (
            f"The query returned {len(rows)} row(s) in column {col}. "
            f"Examples: {preview}{extra}. See the results table below."
        )

    return None


def format_deterministic_summary(
    *,
    question: str,
    rows: list[dict[str, Any]] | None,
    error: str | None = None,
) -> str | None:
    """Return a factual summary when LLM would likely hallucinate missing numbers."""
    if error or not rows:
        return None
    if not question_needs_aggregate_in_select(question):
        return None
    if _rows_include_numeric_values(rows):
        return None

    first = rows[0]
    if len(rows) == 1 and len(first) == 1:
        label, value = next(iter(first.items()))
        q = question.lower()
        if "most" in q or "highest" in q or "top" in q:
            return (
                f"Based on the query, {value} is the top-ranked result "
                f"(returned column: {label}). "
                f"The SQL orders by an aggregate but does not return the count "
                f"in the result columns — see the SQL below."
            )
        return (
            f"The query returned {label}: {value}. "
            "The SQL did not include a numeric count or total in the result columns. "
            "See the SQL below for the full query."
        )

    preview = json.dumps(rows[:3], default=str)
    if len(rows) > 3:
        preview = preview[:-1] + ", ...]"

    return (
        f"The query returned: {preview}. "
        "Numeric counts or totals are not in the result columns — "
        "see the SQL below for the full query."
    )
