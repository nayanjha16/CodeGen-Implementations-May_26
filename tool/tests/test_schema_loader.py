"""Unit tests for schema_loader using SQLite."""

from sqlalchemy import create_engine, text

from tool.core.schema_loader import load_all_tables


def test_load_all_tables_sqlite():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"))
        conn.execute(text("CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER)"))
        conn.commit()

    tables = load_all_tables(engine, schema="main")
    names = {t.name for t in tables}
    assert "users" in names
    assert "orders" in names
    users = next(t for t in tables if t.name == "users")
    assert "id" in users.columns
    assert "CREATE TABLE users" in users.ddl
