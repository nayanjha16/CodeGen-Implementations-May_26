"""Unit tests for schema_selector (mocked embeddings)."""

import numpy as np

from tool.core.activity_logger import ActivityLogger
from tool.core.schema_loader import TableSchema
from tool.core.schema_selector import build_schema_ddl, select_tables_for_prompt


def _table(name: str, cols: list[str], fk: list[dict] | None = None) -> TableSchema:
    return TableSchema(
        name=name,
        ddl=f"CREATE TABLE {name} ({', '.join(cols)});",
        columns=cols,
        foreign_keys=fk or [],
    )


def test_full_schema_when_few_tables():
    tables = [_table("a", ["id"]), _table("b", ["id"])]
    result = select_tables_for_prompt("show customers", tables, top_k=8)
    assert result.method == "full_schema"
    assert len(result.selected) == 2


def test_embedding_selection(monkeypatch):
    tables = [
        _table("Customers", ["id", "name"]),
        _table(
            "Orders",
            ["id", "customer_id"],
            fk=[{"column": "customer_id", "referred_table": "Customers", "referred_column": "id"}],
        ),
        _table("Products", ["id", "sku"]),
    ]

    embeddings = np.array(
        [
            [1.0, 0.0],
            [0.9, 0.1],
            [0.0, 1.0],
        ]
    )
    query_emb = np.array([1.0, 0.0])

    def fake_embed(model_name, texts):
        if len(texts) == 1:
            return np.array([query_emb])
        return embeddings[: len(texts)]

    monkeypatch.setattr("tool.core.schema_selector._embed_texts", fake_embed)
    logger = ActivityLogger()
    result = select_tables_for_prompt(
        "list top customers",
        tables,
        top_k=2,
        min_score=0.0,
        logger=logger,
    )
    names = {t.name for t in result.selected}
    assert result.method == "embedding"
    assert "Customers" in names
    assert any(e.event == "tables_selected" for e in logger.events)


def test_single_table_count_skips_fk_expansion(monkeypatch):
    tables = [
        _table(
            "film_actor",
            ["actor_id", "film_id"],
            fk=[
                {"column": "actor_id", "referred_table": "actor", "referred_column": "actor_id"},
                {"column": "film_id", "referred_table": "film", "referred_column": "film_id"},
            ],
        ),
        _table(
            "film",
            ["film_id", "title", "language_id"],
            fk=[{"column": "language_id", "referred_table": "language", "referred_column": "language_id"}],
        ),
        _table("actor", ["actor_id", "first_name", "last_name"]),
        _table("language", ["language_id", "name"]),
    ]

    embeddings = np.array(
        [
            [0.2, 0.8],
            [1.0, 0.0],
            [0.1, 0.9],
            [0.0, 1.0],
        ]
    )
    query_emb = np.array([1.0, 0.0])

    def fake_embed(model_name, texts):
        if len(texts) == 1:
            return np.array([query_emb])
        return embeddings[: len(texts)]

    monkeypatch.setattr("tool.core.schema_selector._embed_texts", fake_embed)
    result = select_tables_for_prompt(
        "count number of films",
        tables,
        top_k=1,
        min_score=0.0,
    )

    assert [t.name for t in result.selected] == ["film"]
    assert result.fk_expanded == []


def test_fk_expansion_adds_join_partners_with_top_k_one(monkeypatch):
    tables = [
        _table(
            "film_actor",
            ["actor_id", "film_id"],
            fk=[
                {"column": "actor_id", "referred_table": "actor", "referred_column": "actor_id"},
                {"column": "film_id", "referred_table": "film", "referred_column": "film_id"},
            ],
        ),
        _table("actor", ["actor_id", "first_name", "last_name"]),
        _table("film", ["film_id", "title"]),
        _table("Products", ["id", "sku"]),
    ]

    embeddings = np.array(
        [
            [1.0, 0.0],
            [0.2, 0.8],
            [0.1, 0.9],
            [0.0, 1.0],
        ]
    )
    query_emb = np.array([1.0, 0.0])

    def fake_embed(model_name, texts):
        if len(texts) == 1:
            return np.array([query_emb])
        return embeddings[: len(texts)]

    monkeypatch.setattr("tool.core.schema_selector._embed_texts", fake_embed)
    result = select_tables_for_prompt(
        "find the films acted by first_name = Penelope",
        tables,
        top_k=1,
        min_score=0.0,
    )

    names = {t.name for t in result.selected}
    assert names == {"film_actor", "actor", "film"}
    assert set(result.fk_expanded) == {"actor", "film"}


def test_build_schema_ddl():
    tables = [_table("t1", ["a"]), _table("t2", ["b"])]
    ddl = build_schema_ddl(tables)
    assert "CREATE TABLE t1" in ddl
    assert "CREATE TABLE t2" in ddl
    assert "Relationships:" not in ddl


def test_build_schema_ddl_includes_relationships():
    tables = [
        _table(
            "film_actor",
            ["actor_id", "film_id"],
            fk=[
                {"column": "actor_id", "referred_table": "actor", "referred_column": "actor_id"},
                {"column": "film_id", "referred_table": "film", "referred_column": "film_id"},
            ],
        ),
        _table("actor", ["actor_id", "first_name"]),
        _table("film", ["film_id", "title"]),
    ]
    ddl = build_schema_ddl(tables)
    assert "Relationships:" in ddl
    assert "film_actor.actor_id -> actor.actor_id" in ddl
    assert "film_actor.film_id -> film.film_id" in ddl


def test_column_boost_prefers_actor_for_first_name_question(monkeypatch):
    tables = [
        _table(
            "film_actor",
            ["actor_id", "film_id"],
            fk=[
                {"column": "actor_id", "referred_table": "actor", "referred_column": "actor_id"},
                {"column": "film_id", "referred_table": "film", "referred_column": "film_id"},
            ],
        ),
        _table("actor", ["actor_id", "first_name", "last_name"]),
        _table("film", ["film_id", "title"]),
    ]

    embeddings = np.array(
        [
            [0.95, 0.05],
            [0.94, 0.06],
            [0.93, 0.07],
        ]
    )
    query_emb = np.array([0.96, 0.04])

    def fake_embed(model_name, texts):
        if len(texts) == 1:
            return np.array([query_emb])
        return embeddings[: len(texts)]

    monkeypatch.setattr("tool.core.schema_selector._embed_texts", fake_embed)
    result = select_tables_for_prompt(
        "find rows where first_name = Penelope",
        tables,
        top_k=1,
        min_score=0.0,
    )

    assert result.selected[0].name == "actor"


def test_fallback_selection_expands_join_partners(monkeypatch):
    tables = [
        _table(
            "film_actor",
            ["actor_id", "film_id"],
            fk=[
                {"column": "actor_id", "referred_table": "actor", "referred_column": "actor_id"},
                {"column": "film_id", "referred_table": "film", "referred_column": "film_id"},
            ],
        ),
        _table("actor", ["actor_id", "first_name", "last_name"]),
        _table("film", ["film_id", "title"]),
    ]

    def fail_embed(model_name, texts):
        raise RuntimeError("embedding unavailable")

    monkeypatch.setattr("tool.core.schema_selector._embed_texts", fail_embed)
    result = select_tables_for_prompt(
        "find the films acted by first_name = Penelope",
        tables,
        top_k=1,
        min_score=0.0,
    )

    assert result.method == "fallback"
    assert {t.name for t in result.selected} == {"actor", "film_actor", "film"}
