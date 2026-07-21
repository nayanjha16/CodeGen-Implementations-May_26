"""Evaluation metrics: CodeBLEU, BERTScore/CodeBERTScore, exact match, and
SQLite execution accuracy.

Every metric function takes plain Python lists of strings so it can be unit
tested without loading any model weights.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


def exact_match(predictions: list[str], references: list[str]) -> float:
    if not predictions:
        return 0.0
    hits = sum(
        1 for p, r in zip(predictions, references, strict=False) if p.strip() == r.strip()
    )
    return hits / len(predictions)


def compute_codebleu(
    predictions: list[str],
    references: list[str],
    language: str = "python",
) -> dict[str, float]:
    """CodeBLEU: weighted combination of n-gram match, weighted n-gram match,
    AST match, and data-flow match. Falls back to plain BLEU if the
    ``codebleu`` package or its tree-sitter grammar for ``language`` is
    unavailable, logging a clear warning so results are never silently wrong.
    """
    try:
        from codebleu import calc_codebleu

        lang_map = {"cpp": "cpp", "c++": "cpp", "python": "python", "java": "java", "rust": "rust"}
        cb_lang = lang_map.get(language.lower(), "python")
        result = calc_codebleu(
            references=[[r] for r in references],
            predictions=predictions,
            lang=cb_lang,
        )
        return {
            "codebleu": result["codebleu"],
            "ngram_match": result["ngram_match_score"],
            "weighted_ngram_match": result["weighted_ngram_match_score"],
            "syntax_match": result["syntax_match_score"],
            "dataflow_match": result["dataflow_match_score"],
        }
    except Exception as exc:  # pragma: no cover - environment dependent
        logger.warning(
            "CodeBLEU computation failed (%s); falling back to sacrebleu. "
            "Install `codebleu` + tree-sitter grammars for the full metric.",
            exc,
        )
        return {"codebleu": compute_bleu(predictions, references), "fallback": True}


def compute_bleu(predictions: list[str], references: list[str]) -> float:
    import sacrebleu

    if not predictions:
        return 0.0
    bleu = sacrebleu.corpus_bleu(predictions, [references])
    return bleu.score / 100.0


def compute_bertscore(
    predictions: list[str],
    references: list[str],
    lang: str = "en",
    model_type: str = "microsoft/codebert-base",
    num_layers: int = 12,
) -> dict[str, float]:
    """CodeBERTScore-style similarity using CodeBERT embeddings via bert-score.

    Falls back to ``None`` scores (with a ``fallback`` flag) if the installed
    bert-score/transformers combination is broken -- bert-score is
    effectively unmaintained and calls tokenizer internals that newer
    transformers releases have reorganized, raising things like
    "AttributeError: RobertaTokenizer has no attribute
    'build_inputs_with_special_tokens'". Same graceful-degradation pattern as
    compute_codebleu()'s tree-sitter fallback.
    """
    if not predictions:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    try:
        from bert_score import score as bertscore

        precision, recall, f1 = bertscore(
            predictions,
            references,
            model_type=model_type,
            num_layers=num_layers,
            lang=lang,
            verbose=False,
        )
        return {
            "precision": float(precision.mean()),
            "recall": float(recall.mean()),
            "f1": float(f1.mean()),
        }
    except Exception as exc:  # pragma: no cover - environment dependent
        logger.warning(
            "BERTScore computation failed (%s); reporting no BERTScore for "
            "this run. This is a known incompatibility between the "
            "unmaintained bert-score package and newer transformers "
            "tokenizer internals, not a bug in this codebase.",
            exc,
        )
        return {"precision": None, "recall": None, "f1": None, "fallback": True}

def execution_accuracy(
    predicted_sql: list[str],
    gold_sql: list[str],
    db_paths: list[Path],
) -> dict[str, Any]:
    """Execute predicted vs. gold SQL against SQLite databases and compare
    result sets (order-insensitive). Used for Task 2 (SQL generation, Checkpoint 2)
    but defined here alongside the other metrics for a single evaluation surface.
    """
    assert len(predicted_sql) == len(gold_sql) == len(db_paths), "mismatched lengths"

    correct = 0
    errors: list[dict[str, Any]] = []

    for idx, (pred, gold, db_path) in enumerate(zip(predicted_sql, gold_sql, db_paths, strict=False)):
        try:
            pred_result = _execute_sql(pred, db_path)
            gold_result = _execute_sql(gold, db_path)
            if _results_match(pred_result, gold_result):
                correct += 1
            else:
                errors.append({"index": idx, "reason": "mismatch", "predicted_sql": pred})
        except sqlite3.Error as exc:
            errors.append({"index": idx, "reason": f"execution_error: {exc}", "predicted_sql": pred})

    total = len(predicted_sql)
    return {
        "execution_accuracy": correct / total if total else 0.0,
        "correct": correct,
        "total": total,
        "errors": errors,
    }


def _execute_sql(query: str, db_path: Path) -> list[tuple[Any, ...]]:
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        conn.close()


def _results_match(a: list[tuple[Any, ...]], b: list[tuple[Any, ...]]) -> bool:
    return sorted(map(str, a)) == sorted(map(str, b))


def sample_for_manual_inspection(
    records: list[dict[str, Any]], n: int = 20, seed: int = 42
) -> list[dict[str, Any]]:
    """Deterministically sample N records for the manual-inspection step
    required by the proposal ("manual inspection of 20 random samples")."""
    import random

    rng = random.Random(seed)
    return rng.sample(records, min(n, len(records)))
