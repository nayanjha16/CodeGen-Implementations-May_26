"""
============================================================
RepoCoder Studio
metric_engine.py  —  v2.4
============================================================

Task-aware metric computation. Official CodeBLEU is attempted first and
CodeBLEU-lite remains a diagnostic fallback.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from src.config import CONFIG, AppConfig
from src.python_validator import PythonValidator
from src.java_validator import JavaValidator
from src.csr_builder import CSRBuilder
from src.generation_engine import GenerationEngine
from src.logger import LOG

_CODEBLEU_METRIC = None
_CODEBLEU_AVAILABLE = None


def _load_codebleu_metric():
    global _CODEBLEU_METRIC, _CODEBLEU_AVAILABLE
    if _CODEBLEU_AVAILABLE is not None:
        return _CODEBLEU_METRIC
    try:
        import evaluate
        _CODEBLEU_METRIC = evaluate.load("dvitel/codebleu")
        _CODEBLEU_AVAILABLE = True
        LOG.info("Official CodeBLEU metric available via evaluate/dvitel/codebleu.")
    except Exception as exc:
        _CODEBLEU_METRIC = None
        _CODEBLEU_AVAILABLE = False
        LOG.info(f"Official CodeBLEU unavailable; using CodeBLEU-lite diagnostic fallback. Reason: {exc}")
    return _CODEBLEU_METRIC


class MetricEngine:
    """Computes metrics for one prediction row."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.python_validator = PythonValidator()
        self.java_validator = JavaValidator(config)
        self.csr_builder = CSRBuilder()
        self.gen_engine = GenerationEngine(config)
        self._sem_model = None

    def codebleu_lite(self, reference: str, prediction: str) -> float:
        ref_tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|<=|>=|[{}()\[\];,+\-*/%<>=]", reference or "")
        pred_tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|<=|>=|[{}()\[\];,+\-*/%<>=]", prediction or "")
        if not ref_tokens or not pred_tokens:
            return 0.0
        ref_set, pred_set = set(ref_tokens), set(pred_tokens)
        precision = len(ref_set & pred_set) / max(1, len(pred_set))
        recall = len(ref_set & pred_set) / max(1, len(ref_set))
        return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)

    def official_codebleu(self, reference: str, prediction: str, lang: str) -> Optional[float]:
        metric = _load_codebleu_metric()
        if metric is None:
            return None
        try:
            result = metric.compute(references=[[reference or ""]], predictions=[prediction or ""], lang=lang)
            return float(result.get("codebleu", 0.0))
        except Exception as exc:
            LOG.warning(f"Official CodeBLEU failed for lang={lang}: {exc}")
            return None

    def codebleu(self, reference: str, prediction: str, lang: str) -> Dict[str, Any]:
        official = self.official_codebleu(reference, prediction, lang)
        lite = self.codebleu_lite(reference, prediction)
        return {
            "official_codebleu": official,
            "codebleu_lite": lite,
            "codebleu": official if official is not None else lite,
            "official_codebleu_used": official is not None,
        }

    def csr_similarity(self, reference: str, prediction: str, language: str) -> float:
        if language.lower() == "python":
            a = self.csr_builder.build_python(reference)
            b = self.csr_builder.build_python(prediction)
        else:
            a = self.csr_builder.build_java(reference)
            b = self.csr_builder.build_java(prediction)
        return self.csr_builder.similarity(a, b)

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
        }

        if target == "Python":
            prediction = self.gen_engine.extract_code(raw_prediction, "python")
            py = self.python_validator.validate(prediction)
            cb = self.codebleu(reference, prediction, "python")
            result.update(cb)
            result.update({
                "python_parse_success": py.get("status") == "PASS",
                "primary_success": py.get("status") == "PASS",
                "csr_score": self.csr_similarity(reference, prediction, "python"),
                "csr_similarity": self.csr_similarity(reference, prediction, "python"),
                "scored_prediction": prediction,
                "python_error": py.get("reason"),
            })
            return result

        if target == "Java":
            prediction = self.gen_engine.extract_code(raw_prediction, "java")
            java = self.java_validator.validate(prediction)
            cb = self.codebleu(reference, prediction, "java")
            result.update(cb)
            result.update({
                "java_compile_success": java.get("status") == "PASS",
                "primary_success": java.get("status") == "PASS",
                "csr_score": self.csr_similarity(reference, prediction, "java"),
                "csr_similarity": self.csr_similarity(reference, prediction, "java"),
                "scored_prediction": prediction,
                "compile_error": (java.get("stderr") or "")[:500],
            })
            return result

        prediction = (raw_prediction or "").strip()
        result.update({
            "sacrebleu": self.sacrebleu_score(reference, prediction),
            "rouge_l": self.rouge_l_score(reference, prediction),
            "semantic_similarity": self.semantic_similarity(reference, prediction),
            "primary_success": None,
            "scored_prediction": prediction,
        })
        return result
