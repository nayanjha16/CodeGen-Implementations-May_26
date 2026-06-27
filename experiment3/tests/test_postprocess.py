from text2sql.postprocess import extract_sql

def test_strips_markdown_fence():
    assert extract_sql("```sql\nSELECT 1\n```") == "SELECT 1"

def test_strips_plain_fence():
    assert extract_sql("```\nSELECT 2\n```") == "SELECT 2"

def test_takes_first_statement_and_trims():
    assert extract_sql("SELECT 3;\nSELECT 4;") == "SELECT 3"

def test_drops_leading_prose():
    raw = "Here is the query:\nSELECT name FROM singer WHERE id = 1"
    assert extract_sql(raw) == "SELECT name FROM singer WHERE id = 1"

def test_collapses_whitespace():
    assert extract_sql("SELECT   a,\n   b FROM t") == "SELECT a, b FROM t"
