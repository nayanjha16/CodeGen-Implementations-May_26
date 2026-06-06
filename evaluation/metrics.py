"""Evaluation metrics for SQL generation and NoSQL translation."""

from __future__ import annotations

import re
from typing import Any

import sqlparse


class EvaluationMetrics:
    """Compute NLP, code, and execution metrics for text-to-SQL."""

    def normalize_sql(self, sql: str) -> str:
        """Normalize SQL for exact match comparison."""
        sql = sql.strip().rstrip(";")
        try:
            return sqlparse.format(sql, reindent=True, keyword_case="upper")
        except Exception:
            return sql.upper().strip()

    def exact_match(self, predicted: str, reference: str) -> bool:
        """Exact match accuracy after normalization."""
        return self.normalize_sql(predicted) == self.normalize_sql(reference)

    def exact_match_batch(
        self, predictions: list[str], references: list[str]
    ) -> float:
        """Batch exact match accuracy."""
        if not predictions:
            return 0.0
        matches = sum(
            1 for p, r in zip(predictions, references) if self.exact_match(p, r)
        )
        return matches / len(predictions)

    def syntax_validity_rate(self, predictions: list[str]) -> float:
        """Fraction of syntactically valid SQL predictions."""
        from src.text2sql.sql_validator import SQLValidator

        validator = SQLValidator()
        if not predictions:
            return 0.0
        valid = sum(1 for p in predictions if validator.validate_syntax(p)["valid"])
        return valid / len(predictions)

    def execution_accuracy(
        self,
        predictions: list[str],
        references: list[str],
        db_paths: list[str | None],
    ) -> float:
        """Execution accuracy comparing result sets."""
        from src.text2sql.sql_executor import SQLExecutor

        executor = SQLExecutor()
        correct = 0
        total = 0

        for pred, ref, db_path in zip(predictions, references, db_paths):
            if not db_path:
                continue
            total += 1
            result = executor.compare_results(pred, ref, db_path)
            if result.get("execution_match"):
                correct += 1

        return correct / total if total > 0 else 0.0

    def compute_bleu(self, predictions: list[str], references: list[str]) -> float:
        """Compute corpus BLEU score."""
        try:
            from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu

            refs = [[r.split()] for r in references]
            preds = [p.split() for p in predictions]
            smoothing = SmoothingFunction().method1
            return float(corpus_bleu(refs, preds, smoothing_function=smoothing))
        except Exception:
            return self._simple_token_overlap(predictions, references)

    def compute_rouge_l(self, predictions: list[str], references: list[str]) -> float:
        """Compute average ROUGE-L F1."""
        try:
            from rouge_score import rouge_scorer

            scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
            scores = [
                scorer.score(ref, pred)["rougeL"].fmeasure
                for pred, ref in zip(predictions, references)
            ]
            return sum(scores) / len(scores) if scores else 0.0
        except Exception:
            return self._simple_token_overlap(predictions, references)

    def compute_bertscore(
        self, predictions: list[str], references: list[str]
    ) -> float:
        """Compute average BERTScore F1."""
        try:
            from bert_score import score as bert_score

            _, _, f1 = bert_score(
                predictions,
                references,
                lang="en",
                verbose=False,
                model_type="distilbert-base-uncased",
            )
            return float(f1.mean())
        except Exception:
            return self._simple_token_overlap(predictions, references)

    def compute_codebleu(
        self, predictions: list[str], references: list[str]
    ) -> dict[str, float]:
        """Compute CodeBLEU with n-gram, syntax, and semantic components."""
        try:
            from codebleu import calc_codebleu

            result = calc_codebleu(
                references,
                predictions,
                lang="sql",
                weights=(0.25, 0.25, 0.25, 0.25),
            )
            return {
                "codebleu": float(result["codebleu"]),
                "ngram_match": float(result.get("ngram_match_score", 0)),
                "syntax_match": float(result.get("syntax_match_score", 0)),
                "semantic_match": float(result.get("dataflow_match_score", 0)),
            }
        except Exception:
            overlap = self._simple_token_overlap(predictions, references)
            return {
                "codebleu": overlap,
                "ngram_match": overlap,
                "syntax_match": overlap,
                "semantic_match": overlap,
            }

    def evaluate_all(
        self,
        predictions: list[str],
        references: list[str],
        db_paths: list[str | None] | None = None,
    ) -> dict[str, Any]:
        """Run full evaluation suite."""
        codebleu = self.compute_codebleu(predictions, references)
        metrics = {
            "exact_match": self.exact_match_batch(predictions, references),
            "syntax_validity": self.syntax_validity_rate(predictions),
            "bleu": self.compute_bleu(predictions, references),
            "rouge_l": self.compute_rouge_l(predictions, references),
            "bertscore": self.compute_bertscore(predictions, references),
            **codebleu,
            "count": len(predictions),
        }

        if db_paths:
            metrics["execution_accuracy"] = self.execution_accuracy(
                predictions, references, db_paths
            )

        return metrics

    @staticmethod
    def _simple_token_overlap(
        predictions: list[str], references: list[str]
    ) -> float:
        """Fallback token overlap when metric libraries unavailable."""
        scores = []
        for pred, ref in zip(predictions, references):
            pred_tokens = set(re.findall(r"\w+", pred.lower()))
            ref_tokens = set(re.findall(r"\w+", ref.lower()))
            if not ref_tokens:
                scores.append(0.0)
                continue
            scores.append(len(pred_tokens & ref_tokens) / len(ref_tokens))
        return sum(scores) / len(scores) if scores else 0.0
