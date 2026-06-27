from text2sql.types import GenResult
from text2sql.evaluate.execution import ex_match, ves_score
from text2sql.evaluate.component import component_f1
from text2sql.evaluate.text_metrics import bleu_score, bertscore_f1
from text2sql.evaluate.llm_judge import judge_score

def evaluate_results(results: list[GenResult], db_path_fn, metrics: list[str],
                     judge_runner=None, benchmark: str = "spider") -> dict[str, float]:
    """Aggregate metrics over generation results.

    `benchmark` ("spider" | "bird") selects the dataset-aware Execution Accuracy
    semantics (Spider=multiset, BIRD=set) and is threaded into ex_match/ves_score
    so BIRD is scored with its official set-of-rows semantics.
    """
    acc = {m: [] for m in metrics}
    for r in results:
        db = db_path_fn(r.example.db_id)
        gold, pred, q = r.example.gold_sql, r.sql, r.example.question
        if "ex" in metrics:
            acc["ex"].append(1.0 if ex_match(pred, gold, db, benchmark=benchmark) else 0.0)
        if "ves" in metrics:
            acc["ves"].append(ves_score(pred, gold, db, benchmark=benchmark))
        if "component_f1" in metrics:
            acc["component_f1"].append(component_f1(pred, gold))
        if "bleu" in metrics:
            acc["bleu"].append(bleu_score(pred, gold))
        if "bertscore" in metrics:
            bs = bertscore_f1(pred, gold)   # None if the bert_score stack errors
            if bs is not None:
                acc["bertscore"].append(bs)
        if "ts" in metrics:
            acc["ts"].append(1.0 if ex_match(pred, gold, db, benchmark=benchmark) else 0.0)  # single-db fallback
        if "llm_judge" in metrics and judge_runner is not None:
            acc["llm_judge"].append(float(judge_score(q, pred, gold, judge_runner)))
    # empty bertscore -> None (metric unavailable), other empty metrics -> 0.0
    return {m: (sum(v) / len(v) if v else (None if m == "bertscore" else 0.0))
            for m, v in acc.items()}
