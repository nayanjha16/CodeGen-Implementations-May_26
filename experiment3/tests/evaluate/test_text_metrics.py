import pytest
from text2sql.evaluate.text_metrics import bleu_score, bertscore_f1

def test_bleu_identical_is_high():
    assert bleu_score("SELECT name FROM singer", "SELECT name FROM singer") > 90

def test_bleu_different_is_low():
    assert bleu_score("SELECT name FROM singer", "DELETE FROM concert") < 30

def test_bertscore_uses_injected_scorer():
    def fake_scorer(preds, golds):
        return [1.0 for _ in preds]
    assert bertscore_f1("a", "b", scorer=fake_scorer) == 1.0

@pytest.mark.needs_model
def test_bertscore_real_path_runs():
    val = bertscore_f1("SELECT 1", "SELECT 1")
    assert 0.0 <= val <= 1.0
