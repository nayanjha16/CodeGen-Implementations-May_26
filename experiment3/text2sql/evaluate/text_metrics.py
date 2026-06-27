import sacrebleu

def bleu_score(pred_sql: str, gold_sql: str) -> float:
    """Sentence BLEU (0-100) over raw SQL strings."""
    return sacrebleu.sentence_bleu(pred_sql, [gold_sql]).score

def _default_bertscore(preds, golds):
    from bert_score import score as bs
    # bert_score has no built-in layer count for codebert-base, so pass num_layers
    # explicitly (it's a 12-layer RoBERTa) to avoid a KeyError in model2layers.
    P, R, F1 = bs(preds, golds, model_type="microsoft/codebert-base",
                  num_layers=12, verbose=False)
    return [float(x) for x in F1]

def bertscore_f1(pred_sql: str, gold_sql: str, scorer=None):
    """CodeBERT-based semantic similarity F1 (0-1). Inject `scorer` in tests.

    Returns None if the (fragile) bert_score/transformers stack errors, so a
    BERTScore failure never crashes a long evaluation run.
    """
    scorer = scorer or _default_bertscore
    try:
        return scorer([pred_sql], [gold_sql])[0]
    except Exception:
        return None
