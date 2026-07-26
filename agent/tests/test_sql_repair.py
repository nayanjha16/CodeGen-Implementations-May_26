"""Tests for listing SQL repair helpers."""

from __future__ import annotations

from agent.lib.sql_repair import repair_listing_select, sql_missing_requested_fields


def test_detect_missing_artist_in_select() -> None:
    sql = (
        'SELECT t1."Title" FROM "Album" AS t1 '
        'JOIN "Artist" AS t2 ON t1."ArtistId" = t2."ArtistId"'
    )
    missing = sql_missing_requested_fields("List album titles with artist names.", sql)
    assert "artist name" in missing


def test_repair_album_artist_listing() -> None:
    sql = (
        'SELECT t1."Title" FROM "Album" AS t1 INNER JOIN "Artist" AS t2 '
        'ON t1."ArtistId"::integer = t2."ArtistId"::integer ORDER BY t1."Title"'
    )
    repaired = repair_listing_select(sql, "List album titles with artist names.")
    assert 'album_title' in repaired
    assert 'artist_name' in repaired
    assert "WHERE" not in repaired.upper()
    assert "::integer" not in repaired


def test_repair_skips_unrelated_queries() -> None:
    sql = 'SELECT COUNT(*) FROM "Customer"'
    assert repair_listing_select(sql, "How many customers are there?") == sql
