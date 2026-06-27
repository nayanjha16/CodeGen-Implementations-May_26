from text2sql.types import Example
from text2sql.prompt.zero_shot import build_zero_shot_prompt
from text2sql.prompt.one_shot import build_one_shot_prompt

SCHEMA_STR = "CREATE TABLE singer (\n  singer_id INT PRIMARY KEY,\n  name TEXT\n);"

def test_zero_shot_contains_schema_and_question():
    p = build_zero_shot_prompt(SCHEMA_STR, "How many singers?", evidence="")
    assert "CREATE TABLE singer" in p
    assert "How many singers?" in p
    assert "SQL" in p

def test_zero_shot_includes_evidence_when_present():
    p = build_zero_shot_prompt(SCHEMA_STR, "q", evidence="Napa = county")
    assert "Napa = county" in p

def test_one_shot_includes_example_pair():
    shot = Example(db_id="db", question="How many rows?", gold_sql="SELECT count(*) FROM t")
    p = build_one_shot_prompt(SCHEMA_STR, "How many singers?", shot=shot, evidence="")
    assert "How many rows?" in p
    assert "SELECT count(*) FROM t" in p
    assert "How many singers?" in p
