"""Unit tests for executor using SQLite."""

import pandas as pd
from sqlalchemy import create_engine, text

from tool.core.activity_logger import ActivityLogger
from tool.core.executor import execute_readonly_sql


def test_execute_readonly_sql():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE items (id INTEGER, label TEXT)"))
        conn.execute(text("INSERT INTO items VALUES (1, 'a'), (2, 'b'), (3, 'c')"))
        conn.commit()

    logger = ActivityLogger()
    result = execute_readonly_sql(
        engine,
        "SELECT id, label FROM items ORDER BY id",
        max_rows=2,
        logger=logger,
    )

    assert isinstance(result.dataframe, pd.DataFrame)
    assert result.row_count == 2
    assert result.truncated is True
    assert any(e.event == "rows_retrieved" for e in logger.events)
