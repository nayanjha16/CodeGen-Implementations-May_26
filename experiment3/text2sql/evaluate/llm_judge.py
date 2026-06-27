import re
from text2sql.models.base import ModelRunner

_PROMPT = (
    "You are grading a text-to-SQL answer. Rate the predicted SQL from 1 (wrong) to "
    "5 (perfect) for whether it correctly answers the question, compared to the gold SQL.\n"
    "Question: {q}\nGold SQL: {gold}\nPredicted SQL: {pred}\n"
    "Respond with a line 'Rating: N' where N is 1-5."
)

def judge_score(question: str, pred_sql: str, gold_sql: str, runner: ModelRunner) -> int:
    out = runner.generate(_PROMPT.format(q=question, gold=gold_sql, pred=pred_sql), max_tokens=64)
    # Extract the rating integer (any number), preferring one labelled "Rating:".
    # Out-of-range values are clamped to [1, 5] rather than discarded.
    m = re.search(r"rating\s*[:=]?\s*(\d+)", out, re.IGNORECASE)
    if not m:
        m = re.search(r"\b(\d+)\b", out)
    if not m:
        return 1
    return max(1, min(5, int(m.group(1))))


def judge_cell(per_example: list[dict], runner: ModelRunner, limit: int = 75):
    """Average judge_score over up to `limit` per-example rows (1-5). None if empty.

    Sample-limited (a 1-5 rating doesn't need the full 200) and corroborating only —
    callers must never let this override Execution Accuracy.
    """
    rows = per_example[:limit]
    if not rows:
        return None
    scores = [judge_score(r["question"], r["pred"], r["gold"], runner) for r in rows]
    return sum(scores) / len(scores)
