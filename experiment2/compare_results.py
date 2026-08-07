"""
Parse evaluation reports for all models on all three multi-task targets
and print a side-by-side comparison table matrix.

Usage:
    python compare_results.py
"""

import os
import re
from src.config import MODELS, COMPARISON_REPORT_PATH


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def _parse_spider_report(path):
    """
    Extract per-difficulty exact match scores from a Spider evaluation_report.txt.
    Returns dict with keys: easy, medium, hard, extra, overall (floats 0-1).
    Returns None if the file does not exist or cannot be parsed.
    """
    if not os.path.exists(path):
        return None

    with open(path, encoding="utf-8") as f:
        text = f.read()

    # Look for the exact match line: "exact match   0.448  0.195  0.109  0.030  0.215"
    match = re.search(
        r"exact match\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)",
        text,
    )
    if not match:
        return None

    vals = [float(v) for v in match.groups()]
    return dict(zip(["easy", "medium", "hard", "extra", "overall"], vals))


def _parse_docspider_report(path):
    """
    Extract per-difficulty execution accuracy from a DocSpider evaluation_report.txt.
    Returns dict with keys: easy, medium, hard, extra, overall (floats 0-100, as %).
    Returns None if the file does not exist or cannot be parsed.
    """
    if not os.path.exists(path):
        return None

    with open(path, encoding="utf-8") as f:
        text = f.read()

    results = {}
    for difficulty in ["easy", "medium", "hard", "extra"]:
        m = re.search(
            r"{}[\s\S]*?(\d+\.\d+)%".format(difficulty),
            text,
            re.IGNORECASE,
        )
        results[difficulty] = float(m.group(1)) if m else None

    m_total = re.search(r"TOTAL DATA EXECUTION ACCURACY[:\s]+([\d.]+)%", text, re.IGNORECASE)
    results["overall"] = float(m_total.group(1)) if m_total else None

    return results if any(v is not None for v in results.values()) else None


# ---------------------------------------------------------------------------
# Table renderer
# ---------------------------------------------------------------------------

def _pct(val, is_spider):
    """Format a score as a percentage string."""
    if val is None:
        return "  N/A  "
    pct = val * 100 if is_spider else val  # spider scores are 0-1; docspider are already %
    return f"{pct:5.1f}%"


def _print_table(rows, title):
    header = f"{'Task / Model':<26} {'Easy':>8} {'Medium':>8} {'Hard':>8} {'Extra':>8} {'Overall':>8}"
    sep    = "-" * len(header)
    lines  = [title, sep, header, sep]
    for row in rows:
        label, scores, is_spider = row
        if scores is None:
            line = f"  {label:<24} {'(no results yet)':>42}"
        else:
            line = (
                f"  {label:<24}"
                f" {_pct(scores.get('easy'),    is_spider):>8}"
                f" {_pct(scores.get('medium'),  is_spider):>8}"
                f" {_pct(scores.get('hard'),    is_spider):>8}"
                f" {_pct(scores.get('extra'),   is_spider):>8}"
                f" {_pct(scores.get('overall'), is_spider):>8}"
            )
        lines.append(line)
    lines.append(sep)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    text2sql_rows   = []
    sql2nosql_rows  = []
    text2nosql_rows = []

    for model_type, short in [("codegen", "CodeGen-350M"), ("codet5", "CodeT5+-220M")]:
        cfg = MODELS[model_type]

        # For CodeGen, use Pass 2 dirs — RAG inference only runs after teacher calibration.
        # CodeT5+ has no pass2 variant, so fall back to its single output dirs.
        if model_type == "codegen":
            t2s_dir = cfg.get("output_text2sql_p2", cfg.get("output_text2sql", os.path.join("outputs", f"{model_type}_text2sql")))
            s2n_dir = cfg.get("output_sql2nosql_p2", cfg.get("output_sql2nosql", os.path.join("outputs", f"{model_type}_sql2nosql")))
            t2n_dir = cfg.get("output_text2nosql_p2", cfg.get("output_text2nosql", os.path.join("outputs", f"{model_type}_text2nosql")))
        else:
            t2s_dir = cfg.get("output_text2sql", os.path.join("outputs", f"{model_type}_text2sql"))
            s2n_dir = cfg.get("output_sql2nosql", os.path.join("outputs", f"{model_type}_sql2nosql"))
            t2n_dir = cfg.get("output_text2nosql", os.path.join("outputs", f"{model_type}_text2nosql"))

        for mode_label, suffix in [("baseline", ""), ("+RAG    ", "_rag")]:
            spider_report    = os.path.join(t2s_dir, f"evaluation_report{suffix}.txt")
            docspider_report = os.path.join(s2n_dir, f"evaluation_report{suffix}.txt")
            direct_mql_report = os.path.join(t2n_dir, f"evaluation_report{suffix}.txt")

            # Label adjustments to show if it represents the newly fine-tuned multi-task model
            model_display = f"{short} (Unified)" if model_type == "codegen" else short

            text2sql_rows.append((
                f"{model_display} {mode_label}",
                _parse_spider_report(spider_report),
                True,
            ))
            sql2nosql_rows.append((
                f"{model_display} {mode_label}",
                _parse_docspider_report(docspider_report),
                False,
            ))
            text2nosql_rows.append((
                f"{model_display} {mode_label}",
                _parse_docspider_report(direct_mql_report),
                False,
            ))

    table_sql   = _print_table(text2sql_rows,   "NL -> SQL   (Spider exact match accuracy)")
    table_nosql = _print_table(sql2nosql_rows,  "SQL -> MQL  (DocSpider execution accuracy)")
    table_t2n   = _print_table(text2nosql_rows, "NL -> MQL   (DocSpider Direct text2nosql execution accuracy)")
    
    full_report = "\n\n".join([table_sql, table_nosql, table_t2n])

    print("\n" + full_report + "\n")

    os.makedirs(os.path.dirname(COMPARISON_REPORT_PATH), exist_ok=True)
    with open(COMPARISON_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(full_report + "\n")
    print(f"Comparison report saved securely: {COMPARISON_REPORT_PATH}")


if __name__ == "__main__":
    main()