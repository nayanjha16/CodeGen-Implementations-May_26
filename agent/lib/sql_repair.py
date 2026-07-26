"""Deterministic repairs for incomplete CodeGen SELECT lists on join queries."""

from __future__ import annotations

import re

from agent.lib.text2sql_hints import question_is_open_listing

_SELECT_FROM_RE = re.compile(r"\bSELECT\s+(?P<select>.+?)\s+FROM\b", re.IGNORECASE | re.DOTALL)


def _find_table_alias(sql: str, table: str) -> str | None:
    patterns = (
        rf'"{re.escape(table)}"\s+(?:AS\s+)?(?P<alias>[A-Za-z_][\w$]*)',
        rf"\b{re.escape(table)}\s+(?:AS\s+)?(?P<alias>[A-Za-z_][\w$]*)",
    )
    for pattern in patterns:
        match = re.search(pattern, sql, re.IGNORECASE)
        if match:
            return match.group("alias")
    return None


def _select_text(sql: str) -> str:
    match = _SELECT_FROM_RE.search(sql)
    return match.group("select") if match else ""


def sql_missing_requested_fields(question: str, sql: str) -> list[str]:
    """Detect requested entities missing from the SQL SELECT clause."""
    select = _select_text(sql).lower()
    sql_lower = sql.lower()
    lowered = question.lower()
    missing: list[str] = []

    def _select_has(*needles: str) -> bool:
        return any(needle in select for needle in needles)

    if re.search(r"\bartist", lowered) and "artist" in sql_lower and not _select_has("artist", '"name"', ".name"):
        missing.append("artist name")
    if re.search(r"\balbum", lowered) and "album" in sql_lower and not _select_has("album", "title"):
        missing.append("album title")
    if re.search(r"\bgenre", lowered) and "genre" in sql_lower and not _select_has("genre"):
        missing.append("genre")
    if re.search(r"\btrack", lowered) and "track" in sql_lower and not _select_has("track"):
        missing.append("track name")
    if re.search(r"\bcustomer", lowered) and "customer" in sql_lower and not _select_has(
        "customer", "firstname", "lastname"
    ):
        missing.append("customer name")

    return missing


def repair_listing_select(sql: str, question: str) -> str:
    """Patch common Chinook listing queries when CodeGen omits joined columns."""
    if not question_is_open_listing(question):
        return sql

    missing = sql_missing_requested_fields(question, sql)
    if not missing:
        return sql

    sql_lower = sql.lower()

    if "artist name" in missing and "album" in sql_lower and "artist" in sql_lower:
        album_alias = _find_table_alias(sql, "Album") or "t1"
        artist_alias = _find_table_alias(sql, "Artist") or "t2"
        select = (
            f'SELECT {album_alias}."Title" AS album_title, '
            f'{artist_alias}."Name" AS artist_name'
        )
        repaired = _SELECT_FROM_RE.sub(f"{select} FROM", sql, count=1)
        return re.sub(r"::\w+", "", repaired)

    if "track name" in missing and "track" in sql_lower and "album" in sql_lower:
        track_alias = _find_table_alias(sql, "Track") or "t1"
        album_alias = _find_table_alias(sql, "Album") or "t2"
        select = f'SELECT {track_alias}."Name" AS track_name, {album_alias}."Title" AS album_title'
        if "artist" in sql_lower:
            artist_alias = _find_table_alias(sql, "Artist") or "t3"
            select = (
                f'SELECT {track_alias}."Name" AS track_name, '
                f'{album_alias}."Title" AS album_title, '
                f'{artist_alias}."Name" AS artist_name'
            )
        repaired = _SELECT_FROM_RE.sub(f"{select} FROM", sql, count=1)
        return re.sub(r"::\w+", "", repaired)

    if "genre" in missing and "genre" in sql_lower and "track" in sql_lower:
        genre_alias = _find_table_alias(sql, "Genre") or "t1"
        repaired = _SELECT_FROM_RE.sub(
            f'SELECT {genre_alias}."Name" AS genre_name, COUNT(*) AS track_count FROM',
            sql,
            count=1,
        )
        if "GROUP BY" not in repaired.upper():
            repaired = re.sub(
                r"\s+ORDER\s+BY",
                f' GROUP BY {genre_alias}."Name" ORDER BY',
                repaired,
                count=1,
                flags=re.IGNORECASE,
            )
        return re.sub(r"::\w+", "", repaired)

    return sql
