from pathlib import Path
from text2sql.types import Example, SchemaInfo
from text2sql.models.base import StubRunner
from text2sql.pipeline import generate_for_examples

DB = Path(__file__).parent / "data" / "fixtures" / "spider_mini" / "database" / "concert_singer" / "concert_singer.sqlite"

def test_zero_shot_pipeline_produces_clean_sql():
    ex = Example("concert_singer", "How many singers?", "SELECT count(*) FROM singer")
    schema = SchemaInfo(db_id="concert_singer", tables={"singer": ["singer_id", "name"]})
    runner = StubRunner(responses=["```sql\nSELECT count(*) FROM singer\n```"])
    results = generate_for_examples(
        [ex], schemas={"concert_singer": schema}, db_paths={"concert_singer": DB},
        runner=runner, scenario="zero_shot", retriever=None)
    assert results[0].sql == "SELECT count(*) FROM singer"

def test_one_shot_pipeline_uses_retriever():
    ex = Example("concert_singer", "How many singers?", "SELECT count(*) FROM singer")
    schema = SchemaInfo(db_id="concert_singer", tables={"singer": ["singer_id", "name"]})
    class FakeRetriever:
        def retrieve(self, q): return Example("concert_singer", "count rows", "SELECT count(*) FROM t")
    runner = StubRunner(responses=["SELECT count(*) FROM singer"])
    results = generate_for_examples(
        [ex], schemas={"concert_singer": schema}, db_paths={"concert_singer": DB},
        runner=runner, scenario="one_shot", retriever=FakeRetriever())
    assert results[0].sql == "SELECT count(*) FROM singer"
