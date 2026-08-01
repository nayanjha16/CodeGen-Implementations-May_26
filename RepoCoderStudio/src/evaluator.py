"""
============================================================
RepoCoder Studio
evaluator.py  —  v2.4
============================================================

Evaluation orchestrator with per-task reporting.

Stage 5 RAG comparison
-----------------------
evaluate() optionally accepts a `retrieval_engine` (duck-typed: anything
with `.is_eligible(task_id)` and `.build_context_block(query)`, i.e.
src.retrieval_engine.RetrievalEngine) and a `run_tag` to distinguish
output files. This lets a RAG-on run and a RAG-off run of the same
model go through the exact same evaluation code, the same way baseline
and fine-tuned already do -- so a RAG-on-vs-off comparison_engine.compare()
call is measuring one changed variable (retrieval context), not pipeline
drift. See notebook cell "Stage 5B" for the four-way (baseline/finetuned
x rag-off/rag-on) comparison this enables.
"""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional, Tuple
import random

import pandas as pd

from src.config import CONFIG, AppConfig
from src.storage import ProjectStorageManager
from src.generation_engine import GenerationEngine
from src.metric_engine import MetricEngine
from src.prediction_inspector import PredictionInspector
from src.failure_analyzer import FailureAnalyzer
from src.comparison_engine import ComparisonEngine
from src.logger import LOG, SectionPrinter, SummaryPrinter


EVALUATION_CONTRACT = "evaluation_v2.5_shared_extraction_incremental_resume"


class EvaluationEngine:
    """Runs baseline/fine-tuned evaluation and comparison."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.storage = ProjectStorageManager(config)
        self.gen_engine = GenerationEngine(config)
        self.metric_engine = MetricEngine(config)
        self.inspector = PredictionInspector()
        self.failure_analyzer = FailureAnalyzer()
        self.comparison_engine = ComparisonEngine()

    def load_model(self, model_type: str):
        return self.gen_engine.load_model(model_type)

    def _select_examples(self, rows: List[Dict[str, Any]], max_examples_per_task: int) -> List[Dict[str, Any]]:
        by_task: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            by_task.setdefault(row["task_id"], []).append(row)
        selected: List[Dict[str, Any]] = []
        rng = random.Random(self.config.runtime.random_seed)
        for task_id in sorted(by_task):
            candidates = list(by_task[task_id])
            rng.shuffle(candidates)
            selected.extend(candidates[:max_examples_per_task])
        return selected

    def evaluate(
        self,
        test_dataset,
        model_type: str,
        max_examples_per_task: int = 5,
        print_inspection: bool = True,
        print_failures: bool = True,
        retrieval_engine: Optional[Any] = None,
        run_tag: str = "",
        model: Optional[Any] = None,
        tokenizer: Optional[Any] = None,
        retrieval_policy: Optional[Dict[str, int]] = None,
    ) -> Tuple[List[Dict], List[Dict], pd.DataFrame]:
        assert model_type in {"baseline", "finetuned"}
        label = f"{model_type.upper()}{' + RAG' if retrieval_engine is not None else ''}"
        SectionPrinter.header(f"{label} Evaluation  [v2.4]")
        # Pass an already-loaded (model, tokenizer) pair (e.g. from a
        # notebook cell that loaded it once earlier in the session) to
        # skip a redundant full model load here -- defaults to the
        # original reload-per-call behavior when not given. This matters
        # on Colab: this project has already hit real CUDA OOM from GPU
        # memory pressure during evaluation once before (see trainer.py's
        # disabled step-eval), so avoiding needless extra model instances
        # resident in memory is a real, not cosmetic, concern.
        if model is None or tokenizer is None:
            model, tokenizer = self.gen_engine.load_model(model_type)
        selected = self._select_examples(list(test_dataset), max_examples_per_task)

        suffix = f"_{run_tag}" if run_tag else ""
        pred_path = f"{self.config.storage.evaluation_dir}/{model_type}{suffix}_prediction_logs.jsonl"
        metric_path = f"{self.config.storage.evaluation_dir}/{model_type}{suffix}_metric_rows.jsonl"
        partial_pred_path = f"{self.config.storage.evaluation_dir}/{model_type}{suffix}_prediction_logs.partial.jsonl"
        partial_metric_path = f"{self.config.storage.evaluation_dir}/{model_type}{suffix}_metric_rows.partial.jsonl"

        prediction_logs: List[Dict[str, Any]] = []
        metric_rows: List[Dict[str, Any]] = []
        # Tagged Stage 5 arms can take hours. Persist each completed row to a
        # dedicated partial file and resume only when the evaluation contract
        # and selected corpus ids match. Untagged baseline/fine-tuned outputs
        # retain their historical paths and behavior.
        if run_tag and self.storage.exists(partial_pred_path) and self.storage.exists(partial_metric_path):
            candidate_logs = self.storage.load_jsonl(partial_pred_path)
            candidate_metrics = self.storage.load_jsonl(partial_metric_path)
            selected_ids = {
                (str(row.get("task_id")), str(row.get("corpus_id")))
                for row in selected
            }
            resumable = (
                len(candidate_logs) == len(candidate_metrics)
                and all(row.get("evaluation_contract") == EVALUATION_CONTRACT for row in candidate_logs)
                and all(
                    (str(row.get("task_id")), str(row.get("corpus_id"))) in selected_ids
                    for row in candidate_logs
                )
            )
            if not resumable:
                raise RuntimeError(
                    f"Incompatible partial evaluation exists for run_tag={run_tag!r}. "
                    "Move the two *.partial.jsonl files aside before restarting; "
                    "they are never overwritten automatically."
                )
            prediction_logs = candidate_logs
            metric_rows = candidate_metrics
            LOG.info(f"Resuming {run_tag}: {len(prediction_logs)}/{len(selected)} rows already complete.")

        completed_ids = {
            (str(row.get("task_id")), str(row.get("corpus_id")))
            for row in prediction_logs
        }

        for idx, row in enumerate(selected):
            if (str(row.get("task_id")), str(row.get("corpus_id"))) in completed_ids:
                continue
            LOG.info(f"[{label}] {idx + 1}/{len(selected)} | {row['task_id']}")

            retrieved_context = ""
            row_task_id = row.get("task_id", "")
            retrieval_meta: Dict[str, Any] = {
                "retrieval_decision": "not_requested",
                "retrieval_top_score": None,
                "retrieval_score_margin": None,
                "retrieval_candidate_count": 0,
                "retrieval_context_chars": 0,
                "retrieval_context_sha256": None,
                "retrieval_sources": [],
                "retrieval_top_k": 0,
            }
            if retrieval_engine is not None and retrieval_engine.is_eligible(row_task_id):
                # corpus-only: this evaluation runs against the XLCoST-derived
                # T1/T3 test split, which has nothing to do with whatever demo
                # repository happens to be configured -- including repo-context
                # here would just dilute the one measurement meant to show
                # whether RAG actually helps the model (see retrieval_engine.py's
                # module docstring for the full reasoning).
                selected_top_k = self.config.retrieval.corpus_eval_top_k
                if retrieval_policy is not None:
                    selected_top_k = int(retrieval_policy.get(row_task_id, 0))

                if selected_top_k <= 0:
                    retrieval_meta["retrieval_decision"] = "disabled_by_validation_policy"
                else:
                    outcome = retrieval_engine.resolve(
                        row["input_text"],
                        task_id=row_task_id,
                        top_k=selected_top_k,
                        sources=("corpus",),
                    )
                    retrieved_context = outcome.context
                    decision = outcome.decision
                    retrieval_meta = {
                        "retrieval_decision": decision.reason,
                        "retrieval_top_score": decision.top_score,
                        "retrieval_score_margin": decision.score_margin,
                        "retrieval_candidate_count": decision.result_count,
                        "retrieval_context_chars": len(retrieved_context),
                        "retrieval_context_sha256": (
                            hashlib.sha256(retrieved_context.encode("utf-8")).hexdigest()
                            if retrieved_context
                            else None
                        ),
                        "retrieval_sources": outcome.sources,
                        "retrieval_top_k": selected_top_k,
                    }

            raw = self.gen_engine.generate(
                model=model,
                tokenizer=tokenizer,
                instruction=row["instruction"],
                input_text=row["input_text"],
                task_id=row.get("task_id", ""),
                retrieved_context=retrieved_context,
            )
            metrics = self.metric_engine.evaluate_prediction(row, raw)
            metric = {
                **metrics,
                "model_type": model_type,
                "evaluation_contract": EVALUATION_CONTRACT,
                "rag_used": bool(retrieved_context),
                **retrieval_meta,
            }
            log = {
                **row,
                **metric,
                "model_type": model_type,
                "evaluation_contract": EVALUATION_CONTRACT,
                "raw_prediction": raw,
                "scored_prediction": metrics.get("scored_prediction", raw),
                "reference": row["output_text"],
            }
            metric_rows.append(metric)
            prediction_logs.append(log)
            if run_tag:
                # A runtime/GPU interruption loses at most the currently
                # generating row. Final artifacts are still written only once
                # the complete selected arm has finished.
                category = self.failure_analyzer.analyze([metric]).iloc[0]["failure_category"]
                metric["failure_category"] = category
                log["failure_category"] = category
                self.storage.append_jsonl(log, partial_pred_path)
                self.storage.append_jsonl(metric, partial_metric_path)

        failure_df = self.failure_analyzer.analyze(metric_rows)
        if not failure_df.empty:
            # Copy failure category back to logs/metrics for inspection and persistence.
            for i, cat in enumerate(failure_df["failure_category"].tolist()):
                metric_rows[i]["failure_category"] = cat
                prediction_logs[i]["failure_category"] = cat

        # run_tag ("" by default) keeps every existing baseline/finetuned
        # (non-RAG) call's output paths byte-identical to before; a
        # non-empty tag (e.g. "rag", "no_rag") suffixes them so a RAG-on
        # and RAG-off run of the same model don't overwrite each other.
        self.storage.save_jsonl(prediction_logs, pred_path)
        self.storage.save_jsonl(metric_rows, metric_path)
        if run_tag:
            for partial in (partial_pred_path, partial_metric_path):
                partial_file = self.storage.path(partial)
                if partial_file.exists():
                    partial_file.unlink()

        summary_df = self.inspector.aggregate_metrics(metric_rows)
        summary_path = (
            self.config.storage.project_root()
            / self.config.storage.evaluation_dir
            / f"{model_type}{suffix}_summary.csv"
        )
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_df.to_csv(summary_path, index=False)

        if print_inspection:
            self.inspector.print_inspection(prediction_logs, max_per_task=2, model_type=model_type)
        if print_failures:
            self.failure_analyzer.print_failure_report(metric_rows, model_type=model_type)

        rag_eligible_count = sum(1 for m in metric_rows if m.get("rag_used"))
        SummaryPrinter.print_summary(
            f"{label} Evaluation Summary  [v2.4]",
            {
                "Evaluated Examples": len(selected),
                "RAG Context Used": f"{rag_eligible_count}/{len(selected)}" if retrieval_engine is not None else "n/a",
                "Prediction Logs": pred_path,
                "Metric Rows": metric_path,
                "Summary CSV": str(summary_path),
            },
        )
        return prediction_logs, metric_rows, summary_df

    def compare(self, baseline_summary: pd.DataFrame, finetuned_summary: pd.DataFrame) -> pd.DataFrame:
        comparison = self.comparison_engine.print_comparison(baseline_summary, finetuned_summary)
        comparison_path = self.config.storage.project_root() / self.config.storage.evaluation_dir / "baseline_vs_finetuned_comparison.csv"
        comparison_path.parent.mkdir(parents=True, exist_ok=True)
        comparison.to_csv(comparison_path, index=False)
        return comparison
