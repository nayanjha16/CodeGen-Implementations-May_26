"""
Standalone evaluation script for Pass 1 and Pass 2 predictions.
Run on local PC where data/spider/database/ is available.

Usage:
    python evaluate_predictions.py --pass 1
    python evaluate_predictions.py --pass 2
    python evaluate_predictions.py --pass 2 --rag
    python evaluate_predictions.py --pass 1 --task text2sql
    python evaluate_predictions.py --pass 2 --task sql2nosql --rag
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
from contextlib import redirect_stdout

from src.config import DATA

# ---------------------------------------------------------------------------
# Output directory map — mirrors what run_multi_task_inference.py writes
# ---------------------------------------------------------------------------
PASS_DIRS = {
    1: {
        "text2sql":   "outputs/codegen/pass1/text2sql",
        "sql2nosql":  "outputs/codegen/pass1/sql2nosql",
        "text2nosql": "outputs/codegen/pass1/text2nosql",
    },
    2: {
        "text2sql":   "outputs/codegen/pass2/text2sql",
        "sql2nosql":  "outputs/codegen/pass2/sql2nosql",
        "text2nosql": "outputs/codegen/pass2/text2nosql",
    },
}

TASKS = ["text2sql", "sql2nosql", "text2nosql"]

# ---------------------------------------------------------------------------
# Normalisation — shared by SQL and MQL string-match fallback
# ---------------------------------------------------------------------------
def _norm(q: str) -> str:
    q = str(q).lower().strip()
    q = re.sub(r'\s+', ' ', q)
    q = re.sub(r'\s*,\s*', ', ', q)
    q = re.sub(r'\s*(=|!=|>=|<=|>|<)\s*', r' \1 ', q)
    q = re.sub(r"'([^']*)'", r'"\1"', q)
    q = re.sub(r'\{\s+', '{', q)
    q = re.sub(r'\s+\}', '}', q)
    q = re.sub(r'\[\s+', '[', q)
    q = re.sub(r'\s+\]', ']', q)
    return q


def _string_exact_match(predictions, gold_key, pred_key):
    if not predictions:
        return 0.0, 0, 0
    correct = sum(
        _norm(p.get(gold_key, "")) == _norm(p.get(pred_key, ""))
        for p in predictions
    )
    return correct / len(predictions), correct, len(predictions)


# ---------------------------------------------------------------------------
# Text-to-SQL evaluation (Spider harness + string-match fallback)
# ---------------------------------------------------------------------------
def _eval_text2sql(predictions, output_dir, label):
    db_dir = os.path.join("data", "spider", "database")
    report_path = os.path.join(output_dir, f"evaluation_report{label}.txt")

    lines = []

    if not os.path.exists(db_dir):
        msg = (
            f"[Spider eval] Skipped — database dir not found: {db_dir}\n"
            f"[Spider eval] Download spider.zip and extract so that "
            f"data/spider/database/ exists, then re-run.\n"
            f"[Spider eval] Showing normalised string exact match instead.\n"
        )
        print(msg)
        lines.append(msg)
    else:
        gold_txt = os.path.join(output_dir, "_eval_gold.txt")
        pred_txt = os.path.join(output_dir, "_eval_pred.txt")

        with open(gold_txt, "w", encoding="utf-8") as f:
            for item in predictions:
                f.write(f"{item['gold_sql']}\t{item['db_id']}\n")
        with open(pred_txt, "w", encoding="utf-8") as f:
            for item in predictions:
                f.write(f"{item['predicted_sql']}\n")

        cmd = [
            sys.executable, "evaluation.py",
            "--gold", gold_txt,
            "--pred", pred_txt,
            "--db",  db_dir,
            "--table", DATA["spider_tables"],
            "--etype", "match",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        spider_out = result.stdout or result.stderr
        print(spider_out)
        lines.append(spider_out)

        for tmp in (gold_txt, pred_txt):
            try:
                os.remove(tmp)
            except OSError:
                pass

    score, correct, total = _string_exact_match(predictions, "gold_sql", "predicted_sql")
    summary = f"String exact match (normalised): {correct}/{total} = {score:.1%}\n"
    print(summary)
    lines.append(summary)

    with open(report_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"  Report saved: {report_path}")

    return score


# ---------------------------------------------------------------------------
# NoSQL evaluation (execution eval if MongoDB available, + string match)
# ---------------------------------------------------------------------------
def _eval_nosql(predictions, pred_path, output_dir, label):
    report_path = os.path.join(output_dir, f"evaluation_report{label}.txt")
    lines = []

    # Try execution-based evaluation
    exec_ok = False
    try:
        from stage5_evaluate_by_execution import evaluate_pipeline
        buf = io.StringIO()
        with redirect_stdout(buf):
            evaluate_pipeline(pred_path)
        exec_out = buf.getvalue()
        print(exec_out)
        lines.append(exec_out)
        exec_ok = True
    except ImportError:
        msg = "[Execution eval] stage5_evaluate_by_execution.py not found — skipped.\n"
        print(msg)
        lines.append(msg)
    except Exception as e:
        msg = f"[Execution eval] Failed ({e}). MongoDB may not be running locally.\n"
        print(msg)
        lines.append(msg)

    if not exec_ok:
        lines.append("[Execution eval] Falling back to string exact match only.\n")

    score, correct, total = _string_exact_match(predictions, "gold_mql", "predicted_mql")
    summary = f"String exact match (normalised): {correct}/{total} = {score:.1%}\n"
    print(summary)
    lines.append(summary)

    with open(report_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"  Report saved: {report_path}")

    return score


# ---------------------------------------------------------------------------
# Per-task dispatcher
# ---------------------------------------------------------------------------
def evaluate_task(pass_num, task, output_dir, rag=False):
    suffix = "_rag" if rag else ""
    pred_file = os.path.join(output_dir, f"predictions{suffix}.json")
    variant = f"Pass {pass_num} | {task.upper()}" + (" (RAG)" if rag else "")

    print(f"\n{'=' * 64}")
    print(f"  {variant}")
    print(f"{'=' * 64}")

    if not os.path.exists(pred_file):
        print(f"  [skip] Prediction file not found: {pred_file}")
        return None

    with open(pred_file, encoding="utf-8") as f:
        predictions = json.load(f)
    print(f"  Examples: {len(predictions)}")

    if task == "text2sql":
        return _eval_text2sql(predictions, output_dir, suffix)
    else:
        return _eval_nosql(predictions, pred_file, output_dir, suffix)


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------
def _print_summary(results):
    print(f"\n{'=' * 64}")
    print("  SUMMARY")
    print(f"{'=' * 64}")
    print(f"  {'Variant':<38}  {'String EM':>10}")
    print(f"  {'-'*38}  {'-'*10}")
    for label, score in results:
        score_str = f"{score:.1%}" if score is not None else "n/a"
        print(f"  {label:<38}  {score_str:>10}")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Pass 1 or Pass 2 predictions locally."
    )
    parser.add_argument(
        "--pass", dest="pass_num", type=int, choices=[1, 2], default=1,
        help="Which pass to evaluate."
    )
    parser.add_argument(
        "--task", default="all",
        choices=["all"] + TASKS,
        help="Task to evaluate (default: all)."
    )
    parser.add_argument(
        "--rag", action="store_true",
        help="Evaluate the RAG variant (predictions_rag.json)."
    )
    parser.add_argument(
        "--dir", dest="output_dir", default=None,
        help="Override the predictions directory for a single task (skips PASS_DIRS lookup)."
    )
    args = parser.parse_args()

    if args.output_dir:
        # Single-directory mode: evaluate whatever is in --dir
        if args.task == "all":
            parser.error("--dir requires --task to be specified (not 'all')")
        task = args.task
        output_dir = args.output_dir
        os.makedirs(output_dir, exist_ok=True)
        results = []
        score = evaluate_task(args.pass_num, task, output_dir, rag=False)
        results.append((f"Pass {args.pass_num} {task}", score))
        if args.rag:
            score_rag = evaluate_task(args.pass_num, task, output_dir, rag=True)
            results.append((f"Pass {args.pass_num} {task} RAG", score_rag))
        _print_summary(results)
        return

    tasks = TASKS if args.task == "all" else [args.task]
    dirs  = PASS_DIRS[args.pass_num]
    results = []

    for task in tasks:
        output_dir = dirs[task]
        os.makedirs(output_dir, exist_ok=True)

        score = evaluate_task(args.pass_num, task, output_dir, rag=False)
        results.append((f"Pass {args.pass_num} {task}", score))

        if args.rag:
            score_rag = evaluate_task(args.pass_num, task, output_dir, rag=True)
            results.append((f"Pass {args.pass_num} {task} RAG", score_rag))

    _print_summary(results)


if __name__ == "__main__":
    main()
