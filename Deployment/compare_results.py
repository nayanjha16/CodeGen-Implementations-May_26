"""3-arm comparison report (plan §8/§12, SPEC §6.4, SPEC-REVIEW #3).

Reads the dev-eval predictions for the three arms and reports execution accuracy
per task and per difficulty. The **only** headline is **C − B**
(treatment − control): both are two-stage, so their difference isolates the one
thing that varies — the teacher's diagnoses.

Arm A (Pass 1) is **draft-only** and structurally not comparable to the two-stage
arms (it never learned to revise). It is shown for context, explicitly labelled,
and the report **never** computes or headlines C − A or B − A — doing so would
conflate "teacher signal" with "got a second inference pass at all".

The metric is value-set-per-row execution accuracy (DocSpider's own semantics):
lossy by design — it measures "right values in the right number of rows", not
"right query" — so arm-to-arm gaps carry that caveat, printed alongside the headline.

Run:  python compare_results.py [--rag]
"""

from __future__ import annotations

import argparse
import json
import logging

from src import config
from src.logger import setup_logging

log = logging.getLogger(__name__)

# Arm labels. A = baseline (draft-only), B = control, C = teacher.
ARM_ORDER = [("A", "baseline"), ("B", "control"), ("C", "teacher")]
DIFFICULTIES = ["easy", "medium", "hard", "extra"]
METRIC_CAVEAT = (
    "Metric = value-set-per-row execution accuracy (DocSpider semantics): lossy by design "
    "(measures right values in the right #rows, not the exact query). Arm gaps carry this caveat."
)


def _pred_path(arm_dir: str, task: str, rag: bool):
    fname = "predictions_rag.json" if rag else "predictions.json"
    return config.OUTPUTS_DIR / "codegen" / "eval" / arm_dir / task / fname


def load_arm_task(arm_dir: str, task: str, rag: bool) -> list[dict] | None:
    p = _pred_path(arm_dir, task, rag)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _acc(records: list[dict]) -> tuple[float, int, int]:
    n = len(records)
    c = sum(1 for r in records if r.get("correct"))
    return (c / n if n else float("nan")), c, n


def _bucket(records: list[dict], difficulty: str | None) -> list[dict]:
    if difficulty is None:
        return records
    return [r for r in records if (r.get("difficulty") or "").lower() == difficulty]


def build_report(rag: bool) -> str:
    lines: list[str] = []
    lines.append("=" * 78)
    lines.append(f"3-ARM COMPARISON REPORT  (rag={rag})")
    lines.append("Arms: A=baseline(Pass1, DRAFT-ONLY)  B=control  C=teacher")
    lines.append("HEADLINE = C - B (treatment - control).  A is draft-only — NOT directly comparable.")
    lines.append("=" * 78)
    lines.append(METRIC_CAVEAT)
    lines.append("")

    # Cache loaded predictions per (arm, task).
    data: dict[tuple[str, str], list[dict] | None] = {}
    for _tag, arm_dir in ARM_ORDER:
        for task in config.TASKS:
            data[(arm_dir, task)] = load_arm_task(arm_dir, task, rag)

    headline_rows = []  # (task, difficulty, accB, accC, delta)

    for task in config.TASKS:
        lines.append(f"### TASK: {task}")
        # Difficulty rows only where difficulty exists (NoSQL); text2sql -> 'overall' only.
        recsA = data[("baseline", task)]
        has_difficulty = bool(recsA) and any(r.get("difficulty") for r in recsA)
        buckets = (DIFFICULTIES + [None]) if has_difficulty else [None]

        header = f"  {'bucket':<10} {'A(draft)':>10} {'B(control)':>12} {'C(teacher)':>12} {'C - B':>10}"
        lines.append(header)
        lines.append("  " + "-" * (len(header) - 2))
        for diff in buckets:
            label = diff if diff else "overall"
            cells = {}
            for _tag, arm_dir in ARM_ORDER:
                recs = data[(arm_dir, task)]
                if recs is None:
                    cells[arm_dir] = None
                    continue
                acc, c, n = _acc(_bucket(recs, diff))
                cells[arm_dir] = (acc, c, n)

            def fmt(cell):
                if cell is None:
                    return "  n/a"
                acc, c, n = cell
                return f"{acc:.3f}({c}/{n})" if n else "  -"

            a, b, cc = cells["baseline"], cells["control"], cells["teacher"]
            # A is labelled draft-only; it is shown but the delta is B/C only.
            a_str = fmt(a) + ("*" if a is not None else "")
            delta = ""
            if b is not None and cc is not None and b[2] and cc[2]:
                d = cc[0] - b[0]
                delta = f"{d:+.3f}"
                headline_rows.append((task, label, b[0], cc[0], d))
            lines.append(f"  {label:<10} {a_str:>10} {fmt(b):>12} {fmt(cc):>12} {delta:>10}")
        lines.append("")

    lines.append("* A (baseline) is DRAFT-ONLY — shown for context, NOT comparable to two-stage B/C.")
    lines.append("  (C - A and B - A are intentionally NOT computed — they are confounded, SPEC-REVIEW #3.)")
    lines.append("")
    lines.append("HEADLINE  C - B  (treatment - control), the isolated teacher effect:")
    if headline_rows:
        for task, label, accB, accC, d in headline_rows:
            if label == "overall":
                lines.append(f"  {task:<12} {label:<8}  C-B = {d:+.3f}   (B={accB:.3f}  C={accC:.3f})")
    else:
        lines.append("  (no arm pair had both B and C predictions on disk)")
    lines.append("")
    lines.append(METRIC_CAVEAT)
    lines.append("=" * 78)
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="3-arm comparison report (headline C - B).")
    ap.add_argument("--rag", action="store_true", help="read the RAG-variant predictions")
    args = ap.parse_args()

    setup_logging("compare_results")
    report = build_report(args.rag)
    config.ensure_dirs()
    out = config.OUTPUTS_DIR / "comparison_report.txt"
    out.write_text(report + "\n", encoding="utf-8")
    print(report)
    log.info("wrote %s", out)


if __name__ == "__main__":
    main()
