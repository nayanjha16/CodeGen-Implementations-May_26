"""Summarise saved RepoCoderStudio runs without ML dependencies.

The script is intentionally standard-library only so an interrupted Colab run
can be audited on any machine before another GPU session is requested.
"""

from __future__ import annotations

import argparse
import ast
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.code_extraction import extract_code, extract_natural_language


def _jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _mean(rows: Iterable[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    return statistics.fmean(values) if values else None


def _failure_category(row: dict[str, Any]) -> str:
    if row.get("prediction_empty"):
        return "empty_generation"
    raw = str(row.get("raw_prediction") or "")
    if "### Instruction" in raw or "### Task Contract" in raw:
        return "prompt_echo"
    target = row.get("target_modality")
    if target == "Python":
        if row.get("python_parse_success") in (False, 0, "False", "false"):
            return "python_syntax_error"
        return "low_similarity" if float(row.get("codebleu") or 0.0) < 0.10 else "ok"
    if target == "Java":
        if row.get("java_compile_success") in (False, 0, "False", "false"):
            return "java_compile_error"
        return "low_similarity" if float(row.get("codebleu") or 0.0) < 0.10 else "ok"
    if target == "Natural Language":
        weak = (
            float(row.get("rouge_l") or 0.0) < 0.05
            and float(row.get("sacrebleu") or 0.0) < 1.0
        )
        return "nl_low_overlap" if weak else "ok"
    return "unknown"


def _model_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("task_id", "unknown"))].append(row)
    summary = []
    for task_id in sorted(grouped):
        group = grouped[task_id]
        raw_lengths = [len(str(row.get("raw_prediction") or "")) for row in group]
        primary = [row.get("primary_success") for row in group]
        summary.append(
            {
                "task_id": task_id,
                "rows": len(group),
                "primary_success": (
                    sum(value is True for value in primary) / len(primary)
                    if any(value is not None for value in primary)
                    else None
                ),
                "codebleu": _mean(group, "codebleu"),
                "rouge_l": _mean(group, "rouge_l"),
                "semantic_similarity": _mean(group, "semantic_similarity"),
                "mean_raw_chars": statistics.fmean(raw_lengths),
                "max_raw_chars": max(raw_lengths),
                "raw_chars_ge_1000": sum(length >= 1000 for length in raw_lengths),
                "failures": dict(sorted(Counter(_failure_category(row) for row in group).items())),
            }
        )
    return summary


def _failure_examples(rows: list[dict[str, Any]], limit_per_task: int = 3) -> dict[str, list[dict[str, Any]]]:
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        category = _failure_category(row)
        if category in {"ok", "low_similarity", "nl_low_overlap"}:
            continue
        task_id = str(row.get("task_id", "unknown"))
        if len(examples[task_id]) >= limit_per_task:
            continue
        raw = str(row.get("raw_prediction") or "")
        reason = row.get("python_error") or row.get("compile_error") or ""
        examples[task_id].append(
            {
                "corpus_id": row.get("corpus_id"),
                "category": category,
                "raw_chars": len(raw),
                "reason": str(reason)[:600],
                "prediction_tail": raw[-500:],
            }
        )
    return dict(examples)


def _rouge_l(reference: str, prediction: str) -> float:
    reference_tokens = reference.lower().split()
    prediction_tokens = prediction.lower().split()
    if not reference_tokens or not prediction_tokens:
        return 0.0
    previous = [0] * (len(prediction_tokens) + 1)
    for ref_token in reference_tokens:
        current = [0]
        for index, pred_token in enumerate(prediction_tokens, start=1):
            if ref_token == pred_token:
                current.append(previous[index - 1] + 1)
            else:
                current.append(max(current[-1], previous[index]))
        previous = current
    lcs = previous[-1]
    precision = lcs / len(prediction_tokens)
    recall = lcs / len(reference_tokens)
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def _normalized_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("task_id", "unknown"))].append(row)
    result = []
    for task_id in sorted(grouped):
        group = grouped[task_id]
        target = group[0].get("target_modality")
        normalized = []
        success: list[bool] = []
        rouge_scores: list[float] = []
        for row in group:
            raw = str(row.get("raw_prediction") or "")
            if target == "Python":
                output = extract_code(raw, "python")
                if not output.strip():
                    success.append(False)
                else:
                    try:
                        ast.parse(output)
                        success.append(True)
                    except (SyntaxError, ValueError):
                        success.append(False)
            elif target == "Java":
                output = extract_code(raw, "java")
            else:
                output = extract_natural_language(raw)
                rouge_scores.append(_rouge_l(str(row.get("reference") or ""), output))
            normalized.append(output)
        result.append(
            {
                "task_id": task_id,
                "rows": len(group),
                "python_parse_success": (
                    sum(success) / len(success) if success else None
                ),
                "rouge_l_stdlib": (
                    statistics.fmean(rouge_scores) if rouge_scores else None
                ),
                "mean_normalized_chars": statistics.fmean(map(len, normalized)),
                "changed_outputs": sum(
                    output != str(row.get("raw_prediction") or "").strip()
                    for output, row in zip(normalized, group)
                ),
            }
        )
    return result


def audit(project_root: Path) -> dict[str, Any]:
    evaluation = project_root / "outputs" / "evaluation"
    notebook = project_root / "notebooks" / "RepoCoderStudio_till_Stage5_RAG_Improved.ipynb"
    report: dict[str, Any] = {
        "project_root": str(project_root),
        "models": {},
        "stage5_files": sorted(path.name for path in evaluation.glob("*rag*")),
    }
    for model_type in ("baseline", "finetuned"):
        rows = _jsonl(evaluation / f"{model_type}_prediction_logs.jsonl")
        report["models"][model_type] = {
            "summary": _model_summary(rows),
            "normalized_summary": _normalized_summary(rows),
            "failure_examples": _failure_examples(rows),
        }

    if notebook.exists():
        data = json.loads(notebook.read_text(encoding="utf-8"))
        cells = data.get("cells", [])
        errors = []
        for index, cell in enumerate(cells):
            for output in cell.get("outputs", []):
                if output.get("output_type") == "error":
                    errors.append(
                        {
                            "cell_index": index,
                            "error": f"{output.get('ename')}: {output.get('evalue')}",
                        }
                    )
        report["notebook"] = {
            "cell_count": len(cells),
            "executed_cell_count": sum(
                cell.get("execution_count") is not None for cell in cells
            ),
            "errors": errors,
        }
    return report


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "project_root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit(args.project_root.resolve())
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
