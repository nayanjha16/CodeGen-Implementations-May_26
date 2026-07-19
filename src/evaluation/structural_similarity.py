"""Structural similarity metrics for SQL and MongoDB queries."""

from __future__ import annotations

import json
import re
from typing import Any

import sqlparse
from sqlparse.tokens import Keyword


_SQL_CLAUSES = (
    "select",
    "from",
    "where",
    "join",
    "group by",
    "order by",
    "having",
)


def _normalize_clause_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip().lower())
    return text.rstrip(";")


def _extract_sql_clause_map(sql: str) -> dict[str, str]:
    """Extract major SQL clauses for structural comparison."""
    parsed = sqlparse.parse(sql.strip().rstrip(";"))
    if not parsed:
        return {clause: "" for clause in _SQL_CLAUSES}

    statement = parsed[0]
    tokens = list(statement.flatten())
    clause_map = {clause: "" for clause in _SQL_CLAUSES}
    current_clause: str | None = None
    buffer: list[str] = []

    def _flush() -> None:
        nonlocal buffer, current_clause
        if current_clause is not None:
            clause_map[current_clause] = _normalize_clause_text(" ".join(buffer))
        buffer = []

    for token in tokens:
        if token.is_whitespace:
            continue
        value = token.value.lower()
        if token.ttype is Keyword and value in _SQL_CLAUSES:
            _flush()
            current_clause = value
            continue
        if current_clause is not None:
            buffer.append(token.value)

    _flush()
    return clause_map


def sql_structural_similarity(predicted: str, reference: str) -> float:
    """Return Jaccard-like similarity over normalized SQL clause text."""
    pred_map = _extract_sql_clause_map(predicted)
    ref_map = _extract_sql_clause_map(reference)
    scores: list[float] = []

    for clause in _SQL_CLAUSES:
        pred_text = pred_map.get(clause, "")
        ref_text = ref_map.get(clause, "")
        if not pred_text and not ref_text:
            scores.append(1.0)
            continue
        if not pred_text or not ref_text:
            scores.append(0.0)
            continue
        pred_tokens = set(re.findall(r"\w+", pred_text))
        ref_tokens = set(re.findall(r"\w+", ref_text))
        union = pred_tokens | ref_tokens
        if not union:
            scores.append(1.0 if pred_text == ref_text else 0.0)
            continue
        scores.append(len(pred_tokens & ref_tokens) / len(union))

    return sum(scores) / len(scores) if scores else 0.0


def sql_structural_similarity_batch(
    predictions: list[str],
    references: list[str],
) -> float:
    if not predictions:
        return 0.0
    scores = [
        sql_structural_similarity(pred, ref)
        for pred, ref in zip(predictions, references)
    ]
    return sum(scores) / len(scores)


_MONGO_STAGE_PATTERN = re.compile(
    r"\$(match|project|group|lookup|sort|limit|unwind)\b",
    re.IGNORECASE,
)


def _extract_mongo_structure(query: str) -> dict[str, Any]:
    text = query.strip()
    structure: dict[str, Any] = {
        "method": "",
        "collection": "",
        "stages": [],
        "normalized": _normalize_clause_text(text),
    }

    method_match = re.match(
        r"db\.(\w+)\.(find|aggregate|distinct|countdocuments)\s*\(",
        text,
        re.IGNORECASE,
    )
    if method_match:
        structure["collection"] = method_match.group(1).lower()
        structure["method"] = method_match.group(2).lower()

    if structure["method"] == "aggregate":
        pipeline_match = re.search(r"aggregate\s*\(\s*(\[.*\])\s*\)", text, re.IGNORECASE | re.DOTALL)
        if pipeline_match:
            try:
                pipeline = json.loads(pipeline_match.group(1))
                if isinstance(pipeline, list):
                    structure["stages"] = [
                        next(iter(stage.keys())).lower()
                        for stage in pipeline
                        if isinstance(stage, dict) and stage
                    ]
            except json.JSONDecodeError:
                structure["stages"] = [
                    match.group(1).lower()
                    for match in _MONGO_STAGE_PATTERN.finditer(pipeline_match.group(1))
                ]
    else:
        structure["stages"] = [
            stage.lower()
            for stage in ("match", "project", "sort", "limit")
            if stage in text.lower() or f".{stage}(" in text.lower()
        ]

    return structure


def mongo_structural_similarity(predicted: str, reference: str) -> float:
    """Compare MongoDB query structure (method, collection, pipeline stages)."""
    pred = _extract_mongo_structure(predicted)
    ref = _extract_mongo_structure(reference)

    parts: list[float] = []
    parts.append(1.0 if pred["method"] == ref["method"] else 0.0)
    parts.append(1.0 if pred["collection"] == ref["collection"] else 0.0)

    pred_stages = set(pred["stages"])
    ref_stages = set(ref["stages"])
    if not pred_stages and not ref_stages:
        stage_score = 1.0
    elif not pred_stages or not ref_stages:
        stage_score = 0.0
    else:
        stage_score = len(pred_stages & ref_stages) / len(pred_stages | ref_stages)
    parts.append(stage_score)

    pred_tokens = set(re.findall(r"\w+", pred["normalized"]))
    ref_tokens = set(re.findall(r"\w+", ref["normalized"]))
    union = pred_tokens | ref_tokens
    token_score = len(pred_tokens & ref_tokens) / len(union) if union else 1.0
    parts.append(token_score)

    return sum(parts) / len(parts)


def mongo_structural_similarity_batch(
    predictions: list[str],
    references: list[str],
) -> float:
    if not predictions:
        return 0.0
    scores = [
        mongo_structural_similarity(pred, ref)
        for pred, ref in zip(predictions, references)
    ]
    return sum(scores) / len(scores)
