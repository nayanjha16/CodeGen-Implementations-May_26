"""Tests for SQL normalization guards."""

from __future__ import annotations

from agent.lib.sql_validation import (
    normalize_generated_sql,
    strip_invented_where_filters,
    strip_schema_artifact_filters,
)

DDL = (
    '-- Use exact quoted table/column names as shown (mixed-case names require double quotes).\n'
    'CREATE TABLE "Album" ("AlbumId" INT, "Title" TEXT, "ArtistId" INT);\n'
    'CREATE TABLE "Artist" ("ArtistId" INT, "Name" TEXT);'
)


def test_strip_pascalcase_artifact_filter() -> None:
    sql = (
        'SELECT t1."Title" FROM "Album" AS t1 JOIN "Artist" AS t2 '
        'ON t1."ArtistId" = t2."ArtistId" WHERE t2."Name" = \'PascalCase\''
    )
    cleaned = strip_schema_artifact_filters(sql)
    assert "WHERE" not in cleaned.upper()
    assert '"Title"' in cleaned


def test_strip_preserves_real_where_clause() -> None:
    sql = 'SELECT * FROM "Customer" WHERE "Country" = \'Brazil\''
    assert strip_schema_artifact_filters(sql) == sql


def test_strip_invented_where_for_open_listing() -> None:
    sql = (
        'SELECT t1."Title" FROM "Album" AS t1 JOIN "Artist" AS t2 '
        'ON t1."ArtistId" = t2."ArtistId" WHERE t2."Name" = \'PostgreSQL\''
    )
    cleaned = strip_invented_where_filters(sql, "List album titles with artist names.")
    assert "WHERE" not in cleaned.upper()


def test_normalize_generated_sql_applies_artifact_strip() -> None:
    sql = (
        'SELECT title FROM album AS t1 JOIN artist AS t2 '
        "ON t1.artistid = t2.artistid WHERE t2.name = 'PascalCase'"
    )
    cleaned = normalize_generated_sql(sql, DDL)
    assert "WHERE" not in cleaned.upper()
    assert '"Album"' in cleaned or "album" in cleaned.lower()
