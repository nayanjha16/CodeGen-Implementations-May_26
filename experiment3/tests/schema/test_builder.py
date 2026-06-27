from pathlib import Path
from text2sql.types import SchemaInfo
from text2sql.schema.builder import SchemaBuilder

FIX_DB = Path(__file__).parents[1] / "data" / "fixtures" / "spider_mini" / "database" / "concert_singer" / "concert_singer.sqlite"

SCHEMA = SchemaInfo(
    db_id="concert_singer",
    tables={"singer": ["singer_id", "name"]},
    primary_keys=["singer.singer_id"],
    column_types={"singer.singer_id": "INT", "singer.name": "TEXT"},
)

def test_includes_create_table_for_selected_tables():
    out = SchemaBuilder(sample_rows=2).build(SCHEMA, ["singer"], db_path=FIX_DB)
    assert "CREATE TABLE" in out
    assert "singer" in out
    assert "name" in out

def test_includes_sample_values():
    out = SchemaBuilder(sample_rows=2).build(SCHEMA, ["singer"], db_path=FIX_DB)
    assert "Joe" in out or "Ann" in out

def test_excludes_unselected_tables():
    schema = SchemaInfo(db_id="db", tables={"singer": ["singer_id"], "concert": ["concert_id"]})
    out = SchemaBuilder(sample_rows=0).build(schema, ["singer"], db_path=None)
    assert "singer" in out
    assert "concert" not in out
