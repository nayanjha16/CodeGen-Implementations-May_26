from text2sql.types import SchemaInfo
from text2sql.schema.linker import SchemaLinker

SCHEMA = SchemaInfo(
    db_id="db",
    tables={"singer": ["singer_id", "name", "age"], "concert": ["concert_id", "singer_id", "year"]},
    foreign_keys=[("concert.singer_id", "singer.singer_id")],
    primary_keys=["singer.singer_id", "concert.concert_id"],
)

def test_links_table_by_name():
    linked = SchemaLinker().link("How many singers are there?", SCHEMA)
    assert "singer" in linked

def test_links_column_match_and_fk_neighbor():
    linked = SchemaLinker().link("List the year of each concert", SCHEMA)
    assert "concert" in linked
    assert "singer" in linked

def test_falls_back_to_all_tables_when_no_match():
    linked = SchemaLinker().link("xyz qqq", SCHEMA)
    assert set(linked) == {"singer", "concert"}
