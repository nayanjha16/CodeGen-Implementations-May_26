from text2sql.types import Example, SchemaInfo, GenResult

def test_example_roundtrip():
    ex = Example(db_id="concert", question="How many?", gold_sql="SELECT count(*) FROM t")
    assert ex.db_id == "concert"
    assert ex.question == "How many?"
    assert ex.gold_sql.startswith("SELECT")

def test_schemainfo_holds_tables():
    s = SchemaInfo(db_id="concert", tables={"singer": ["id", "name"]},
                   foreign_keys=[("concert.singer_id", "singer.id")], primary_keys=["singer.id"])
    assert s.tables["singer"] == ["id", "name"]

def test_genresult_defaults():
    g = GenResult(example=Example("db", "q", "SELECT 1"), raw_output="```sql\nSELECT 1\n```", sql="SELECT 1")
    assert g.sql == "SELECT 1"
