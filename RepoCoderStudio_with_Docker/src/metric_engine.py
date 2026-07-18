"""
============================================================
RepoCoder Studio
metric_engine.py  —  v2.9
============================================================

Task-aware metric computation with safe CodeBLEU handling.

Design decision
---------------
Official CodeBLEU is attempted once per runtime. If the installed
Python/evaluate/CodeBLEU stack fails, the engine disables official CodeBLEU
for the rest of the process and uses CodeBLEU-lite consistently.

This avoids repeated slow failures during baseline and fine-tuned evaluation
and keeps both evaluations comparable through the explicit fields:

- official_codebleu_used
- codebleu_backend
- official_codebleu_error

No global monkey-patching of fractions.Fraction is performed in this version.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

from src.config import CONFIG, AppConfig
from src.python_validator import PythonValidator
from src.java_validator import JavaValidator
from src.csr_builder import CSRBuilder
from src.generation_engine import GenerationEngine
from src.logger import LOG

_CODEBLEU_METRIC = None
_CODEBLEU_LOAD_ATTEMPTED = False
_CODEBLEU_LOAD_ERROR: Optional[str] = None
_CODEBLEU_DISABLED_AFTER_FAILURE = False
_CODEBLEU_DISABLE_REASON: Optional[str] = None


def _load_codebleu_metric():
    """Load Official CodeBLEU once. Never monkey-patch third-party internals."""
    global _CODEBLEU_METRIC, _CODEBLEU_LOAD_ATTEMPTED, _CODEBLEU_LOAD_ERROR

    if _CODEBLEU_LOAD_ATTEMPTED:
        return _CODEBLEU_METRIC

    _CODEBLEU_LOAD_ATTEMPTED = True

    try:
        import evaluate

        _CODEBLEU_METRIC = evaluate.load("dvitel/codebleu")
        LOG.info("Official CodeBLEU metric available via evaluate/dvitel/codebleu.")
    except Exception as exc:
        _CODEBLEU_METRIC = None
        _CODEBLEU_LOAD_ERROR = str(exc)
        LOG.info(
            "Official CodeBLEU unavailable; using CodeBLEU-lite diagnostic fallback. "
            f"Reason: {_CODEBLEU_LOAD_ERROR}"
        )

    return _CODEBLEU_METRIC


class MetricEngine:
    """Computes task-aware metrics for one prediction row."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.python_validator = PythonValidator()
        self.java_validator = JavaValidator(config)
        self.csr_builder = CSRBuilder()
        self.gen_engine = GenerationEngine(config)
        self._sem_model = None

    # ------------------------------------------------------------
    # CodeBLEU
    # ------------------------------------------------------------

    def codebleu_lite(self, reference: str, prediction: str) -> float:
        """Small diagnostic fallback based on token-set F1."""
        ref_tokens = re.findall(
            r"[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|<=|>=|[{}()\[\];,+\-*/%<>=]",
            reference or "",
        )
        pred_tokens = re.findall(
            r"[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|<=|>=|[{}()\[\];,+\-*/%<>=]",
            prediction or "",
        )
        if not ref_tokens or not pred_tokens:
            return 0.0
        ref_set, pred_set = set(ref_tokens), set(pred_tokens)
        precision = len(ref_set & pred_set) / max(1, len(pred_set))
        recall = len(ref_set & pred_set) / max(1, len(ref_set))
        return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)

    def official_codebleu(self, reference: str, prediction: str, lang: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Compute Official CodeBLEU when available.

        If official CodeBLEU fails once, it is disabled for the rest of the
        Python process so baseline and fine-tuned evaluation remain consistent
        and fast.
        """
        global _CODEBLEU_DISABLED_AFTER_FAILURE, _CODEBLEU_DISABLE_REASON

        if _CODEBLEU_DISABLED_AFTER_FAILURE:
            return None, _CODEBLEU_DISABLE_REASON or "official_codebleu_disabled_after_first_failure"

        metric = _load_codebleu_metric()
        if metric is None:
            return None, _CODEBLEU_LOAD_ERROR or "official_metric_unavailable"

        ref = reference or ""
        pred = prediction or ""
        language = (lang or "").lower()

        call_variants = [
            {"references": [ref], "predictions": [pred], "lang": language},
            {"references": [[ref]], "predictions": [pred], "lang": language},
        ]

        last_error: Optional[str] = None
        for kwargs in call_variants:
            try:
                result = metric.compute(**kwargs)
                for key in ("codebleu", "CodeBLEU", "code_bleu"):
                    if key in result:
                        return float(result.get(key, 0.0)), None
                last_error = f"official_result_missing_codebleu_key:{sorted(result.keys())}"
            except Exception as exc:
                last_error = str(exc)

        _CODEBLEU_DISABLED_AFTER_FAILURE = True
        _CODEBLEU_DISABLE_REASON = last_error or "official_codebleu_failed"
        LOG.warning(
            "Official CodeBLEU failed once and will be disabled for the rest of this run. "
            f"lang={language}; reason={_CODEBLEU_DISABLE_REASON}"
        )
        return None, _CODEBLEU_DISABLE_REASON

    def codebleu(self, reference: str, prediction: str, lang: str) -> Dict[str, Any]:
        official, official_error = self.official_codebleu(reference, prediction, lang)
        lite = self.codebleu_lite(reference, prediction)
        backend = "official" if official is not None else "lite_fallback"
        return {
            "official_codebleu": official,
            "codebleu_lite": lite,
            "codebleu": official if official is not None else lite,
            "official_codebleu_used": official is not None,
            "codebleu_backend": backend,
            "official_codebleu_error": official_error,
        }

    # ------------------------------------------------------------
    # Structural / NL metrics
    # ------------------------------------------------------------

    def csr_similarity(self, reference: str, prediction: str, language: str) -> float:
        try:
            if language.lower() == "python":
                a = self.csr_builder.build_python(reference)
                b = self.csr_builder.build_python(prediction)
            else:
                a = self.csr_builder.build_java(reference)
                b = self.csr_builder.build_java(prediction)
            return self.csr_builder.similarity(a, b)
        except Exception as exc:
            LOG.warning(f"CSR similarity failed for language={language}: {exc}")
            return 0.0

    def sacrebleu_score(self, reference: str, prediction: str) -> float:
        try:
            import sacrebleu

            return float(sacrebleu.corpus_bleu([prediction or ""], [[reference or ""]]).score)
        except Exception:
            return 0.0

    def rouge_l_score(self, reference: str, prediction: str) -> float:
        try:
            from rouge_score import rouge_scorer

            scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
            return float(scorer.score(reference or "", prediction or "")["rougeL"].fmeasure)
        except Exception:
            return 0.0

    def semantic_similarity(self, reference: str, prediction: str) -> Optional[float]:
        try:
            if self._sem_model is None:
                from sentence_transformers import SentenceTransformer

                self._sem_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            import numpy as np

            embs = self._sem_model.encode([reference or "", prediction or ""], convert_to_numpy=True)
            a, b = embs[0], embs[1]
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
        except Exception:
            return None

    # ------------------------------------------------------------
    # Main row evaluation
    # ------------------------------------------------------------

    def evaluate_prediction(self, row: Dict[str, Any], raw_prediction: str) -> Dict[str, Any]:
        task_id = row["task_id"]
        target = row["target_modality"]
        reference = row["output_text"]

        result: Dict[str, Any] = {
            "task_id": task_id,
            "corpus_id": row["corpus_id"],
            "source_modality": row["source_modality"],
            "target_modality": target,
            "prediction_empty": not bool((raw_prediction or "").strip()),
            "raw_prediction": raw_prediction,
            "prompt_version": row.get("prompt_version"),
            "prompt_hash": row.get("prompt_hash"),
            "response_header": row.get("response_header"),
        }

        if target == "Python":
            prediction = self.gen_engine.extract_code(raw_prediction, "python")
            py = self.python_validator.validate(prediction)
            cb = self.codebleu(reference, prediction, "python")
            csr = self.csr_similarity(reference, prediction, "python")
            result.update(cb)
            result.update(
                {
                    "python_parse_success": py.get("status") == "PASS",
                    "primary_success": py.get("status") == "PASS",
                    "csr_score": csr,
                    "csr_similarity": csr,
                    "scored_prediction": prediction,
                    "python_error": py.get("reason"),
                }
            )
            return result

        if target == "Java":
            prediction = self.gen_engine.extract_code(raw_prediction, "java")
            java = self.java_validator.validate(prediction)
            cb = self.codebleu(reference, prediction, "java")
            csr = self.csr_similarity(reference, prediction, "java")
            result.update(cb)
            result.update(
                {
                    "java_compile_success": java.get("status") == "PASS",
                    "primary_success": java.get("status") == "PASS",
                    "csr_score": csr,
                    "csr_similarity": csr,
                    "scored_prediction": prediction,
                    "compile_error": (java.get("stderr") or "")[:500],
                }
            )
            return result

        prediction = (raw_prediction or "").strip()
        result.update(
            {
                "sacrebleu": self.sacrebleu_score(reference, prediction),
                "rouge_l": self.rouge_l_score(reference, prediction),
                "semantic_similarity": self.semantic_similarity(reference, prediction),
                "primary_success": None,
                "scored_prediction": prediction,
            }
        )
        return result
