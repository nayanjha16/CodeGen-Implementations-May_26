"""Evaluation metrics: BLEU, BERTScore, CodeBLEU, CodeBERTScore.

Bugs fixed vs original:
  1. compute_bert_score now uses 'roberta-large' (general NLP model),
     not codebert-base — previously both bert + code_bert were identical.
  2. calc_codebleu references now passed as list-of-lists (required format).
  3. num_layers removed from _bert_score_means — let bert_score pick
     the optimal layer per model automatically.
  4. normalize_code is now applied before all metric computations.
  5. Empty/None prediction guard added.
"""

from __future__ import annotations

import re
from typing import Sequence, cast

import torch
from bert_score import score as bert_score_fn


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def normalize_code(code: str) -> str:
    """Normalize code for fair comparison.

    Removes comments and collapses whitespace so that formatting
    differences don't artificially penalise scores.
    """
    code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)   # strip comments
    code = re.sub(r"\s+", " ", code).strip()               # collapse whitespace
    return code


def _safe_normalize(texts: Sequence[str]) -> list[str]:
    """Normalize a list of code strings; replace None/empty with placeholder."""
    result = []
    for t in texts:
        if not t or not t.strip():
            result.append("<empty>")
        else:
            result.append(normalize_code(t))
    return result


def _bert_score_means(
    predictions: Sequence[str],
    references: Sequence[str],
    model_type: str,
    num_layers: int | None = None,
) -> tuple[float, float, float]:
    """Return corpus-mean P/R/F1 from BERTScore.

    bert_score auto-selects an optimal layer only for models listed in its
    ``model2layers`` table (e.g. roberta-large → 17). Models NOT in that
    table — notably microsoft/codebert-base — raise a KeyError when
    num_layers is omitted, so callers must pass it explicitly for those.
    """
    P, R, F1 = bert_score_fn(
        list(predictions),
        list(references),
        model_type=model_type,
        num_layers=num_layers,   # required for models absent from model2layers
        verbose=False,
    )
    precision = cast(torch.Tensor, P).mean().item()
    recall    = cast(torch.Tensor, R).mean().item()
    f1        = cast(torch.Tensor, F1).mean().item()
    return precision, recall, f1


# ---------------------------------------------------------------------------
# Public metric functions
# ---------------------------------------------------------------------------

def compute_bleu(predictions: Sequence[str], references: Sequence[str]) -> dict:
    """Compute corpus BLEU using sacrebleu (with code normalization)."""
    try:
        import sacrebleu
        norm_preds = _safe_normalize(predictions)
        norm_refs  = _safe_normalize(references)
        bleu = sacrebleu.corpus_bleu(norm_preds, [norm_refs])
        return {"bleu": bleu.score, "bleu_details": bleu.format()}
    except Exception as e:
        return {"bleu": 0.0, "error": str(e)}


def compute_bert_score(
    predictions: Sequence[str],
    references: Sequence[str],
    model_type: str = "roberta-large",          # FIX: was "microsoft/codebert-base"
) -> dict:
    """Compute BERTScore with a general NLP model (roberta-large).

    FIX: original used codebert-base here AND in compute_code_bert_score,
    making both metrics return identical values. BERTScore should use a
    general language model; CodeBERTScore uses the code-specific one.
    """
    try:
        norm_preds = _safe_normalize(predictions)
        norm_refs  = _safe_normalize(references)
        precision, recall, f1 = _bert_score_means(norm_preds, norm_refs, model_type)
        return {
            "bertscore_precision": precision,
            "bertscore_recall":    recall,
            "bertscore_f1":        f1,
        }
    except Exception as e:
        return {"bertscore_f1": 0.0, "error": str(e)}


def compute_codebleu(
    predictions: Sequence[str],
    references: Sequence[str],
    lang: str = "python",
) -> dict:
    """Compute CodeBLEU metric.

    FIX: references must be List[List[str]] (list-of-lists), not List[str].
    Passing a flat list caused the library to iterate over individual
    characters, producing near-zero n-gram scores (~0.026).
    """
    try:
        from codebleu import calc_codebleu

        # NOTE: do NOT normalize here — CodeBLEU's AST parser needs
        # valid Python syntax with proper indentation/newlines.
        norm_preds = [p if p and p.strip() else "pass" for p in predictions]
        norm_refs  = [r if r and r.strip() else "pass" for r in references]

        # CodeBLEU's default n-gram tokenizer is ``str.split()`` (whitespace
        # only), so idiomatic predictions (``fibo[i-1]``) score near-zero
        # n-gram against detokenized references (``fibo [ i - 1 ]``) purely
        # due to spacing. A code-aware tokenizer that splits identifiers from
        # punctuation makes the n-gram match spacing-invariant.
        def code_tokenizer(s: str) -> list[str]:
            return re.findall(r"\w+|[^\s\w]", s)

        result = calc_codebleu(
            references=[[r] for r in norm_refs],   # FIX: list-of-lists
            predictions=norm_preds,
            lang=lang,
            weights=(0.25, 0.25, 0.25, 0.25),
            tokenizer=code_tokenizer,
        )
        return {
            "codebleu":                 result.get("codebleu", 0.0),
            "codebleu_ngram":           result.get("ngram_match_score", 0.0),
            "codebleu_weighted_ngram":  result.get("weighted_ngram_match_score", 0.0),
            "codebleu_syntax":          result.get("syntax_match_score", 0.0),
            "codebleu_dataflow":        result.get("dataflow_match_score", 0.0),
        }
    except Exception as e:
        hint = (
            f"{e} (tree-sitter/codebleu version mismatch — "
            "install tree-sitter>=0.23.2,<0.24.0 and tree-sitter-python>=0.23.6; "
            "see requirements.txt)"
        )
        return {"codebleu": 0.0, "error": hint}


def compute_code_bert_score(
    predictions: Sequence[str],
    references: Sequence[str],
    model_type: str = "microsoft/codebert-base",  # correct: code-specific model
    num_layers: int = 12,                          # codebert-base is absent from
                                                   # bert_score's auto layer table
) -> dict:
    """Compute CodeBERTScore (BERTScore with CodeBERT embeddings).

    Uses microsoft/codebert-base which was pretrained on code, giving
    semantically meaningful similarity scores for code pairs. Because this
    model is not in bert_score's model2layers table, num_layers must be
    supplied explicitly (12 hidden layers) or scoring raises a KeyError.
    """
    try:
        norm_preds = _safe_normalize(predictions)
        norm_refs  = _safe_normalize(references)
        precision, recall, f1 = _bert_score_means(
            norm_preds, norm_refs, model_type, num_layers=num_layers
        )
        return {
            "code_bertscore_precision": precision,
            "code_bertscore_recall":    recall,
            "code_bertscore_f1":        f1,
        }
    except Exception as e:
        return {"code_bertscore_f1": 0.0, "error": str(e)}


def compute_execution_accuracy(results: Sequence[dict]) -> dict:
    """Compute pass rate from sandbox execution results."""
    if not results:
        return {"execution_accuracy": 0.0, "passed": 0, "total": 0}
    passed = sum(1 for r in results if r.get("passed", False))
    total  = len(results)
    return {
        "execution_accuracy": passed / total,
        "passed":             passed,
        "total":              total,
    }


def _normalize_stdout(stdout: str) -> str:
    """Normalize stdout for comparison across platforms."""
    return stdout.strip().replace("\r\n", "\n")


def compute_output_match_accuracy(
    pred_results: Sequence[dict],
    ref_results: Sequence[dict],
) -> dict:
    """Compare prediction stdout against reference stdout.

    A sample counts as matched only when both pred and ref executed
    successfully (``passed=True``) and normalized stdout is equal.
    """
    if not pred_results or not ref_results:
        return {
            "output_match_accuracy": 0.0,
            "output_matched":        0,
            "output_comparable":     0,
            "total":                 0,
        }

    total = min(len(pred_results), len(ref_results))
    matched = 0
    comparable = 0

    for pred, ref in zip(pred_results[:total], ref_results[:total]):
        pred_passed = pred.get("passed", False)
        ref_passed = ref.get("passed", False)
        if pred_passed and ref_passed:
            comparable += 1
            if _normalize_stdout(pred.get("stdout", "")) == _normalize_stdout(ref.get("stdout", "")):
                matched += 1

    return {
        "output_match_accuracy": matched / total if total else 0.0,
        "output_matched":        matched,
        "output_comparable":     comparable,
        "total":                 total,
    }


def compute_all_metrics(
    predictions: Sequence[str],
    references: Sequence[str],
    execution_results: Sequence[dict] | None = None,
    skip_bert: bool = False,
) -> dict:
    """Run all evaluation metrics and return combined report."""
    report: dict = {}
    report.update(compute_bleu(predictions, references))
    report.update(compute_codebleu(predictions, references))

    if not skip_bert:
        report.update(compute_bert_score(predictions, references))
        report.update(compute_code_bert_score(predictions, references))

    if execution_results is not None:
        report.update(compute_execution_accuracy(execution_results))

    return report