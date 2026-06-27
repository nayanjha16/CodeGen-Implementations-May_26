from text2sql.evaluate.component import component_f1

def test_identical_queries_score_one():
    f1 = component_f1("SELECT name FROM singer WHERE age > 30",
                      "SELECT name FROM singer WHERE age > 30")
    assert f1 == 1.0

def test_partial_overlap_between_zero_and_one():
    f1 = component_f1("SELECT name FROM singer WHERE age > 30",
                      "SELECT name FROM singer")
    assert 0.0 < f1 < 1.0

def test_disjoint_queries_score_low():
    f1 = component_f1("SELECT name FROM singer",
                      "SELECT count(*) FROM concert GROUP BY year")
    assert f1 < 0.5

def test_invalid_sql_returns_zero():
    assert component_f1("not sql", "SELECT 1") == 0.0
