"""Tests for structural similarity metrics."""

from __future__ import annotations

from src.evaluation.structural_similarity import (
    mongo_structural_similarity,
    sql_structural_similarity,
)


def test_sql_structural_similarity_exact_match():
    sql = "SELECT name FROM singer WHERE age > 30 ORDER BY age DESC"
    assert sql_structural_similarity(sql, sql) == 1.0


def test_sql_structural_similarity_partial_match():
    predicted = "SELECT name FROM singer WHERE age > 30"
    reference = "SELECT count(*) FROM concert WHERE year = 2014"
    score = sql_structural_similarity(predicted, reference)
    assert 0.0 < score < 1.0


def test_mongo_structural_similarity_same_query():
    query = 'db.singer.find({}, {"name": 1}).sort({age: -1})'
    assert mongo_structural_similarity(query, query) == 1.0


def test_mongo_structural_similarity_different_collection():
    predicted = "db.singer.find({})"
    reference = "db.concert.find({})"
    assert mongo_structural_similarity(predicted, reference) < 1.0
