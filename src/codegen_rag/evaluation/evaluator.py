"""High-level Evaluator: runs a task over a dataset split and produces both
per-example results and aggregate comparison-table rows.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from codegen_rag.evaluation.metrics import (
    compute_bertscore,
    compute_codebleu,
    exact_match,
    execution_accuracy,
    sample_for_manual_inspection,
)
from codegen_rag.tasks.base_task import BaseTask
from codegen_rag.utils.io_utils import write_json, write_jsonl
from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)

_REFERENCE_KEYS = {
    "program_synthesis": "code",
    "documentation_generation": "docstring",
    "commit_message_generation": "commit_message",
    "code_translation": "target_code",
}


class Evaluator:
    """Runs a task, scores it against references, and persists artifacts."""

    def __init__(self, results_dir: Path):
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def evaluate_task(
        self,
        task: BaseTask,
        records: list[dict[str, Any]],
        model_tier: str,
        language: str = "python",
    ) -> dict[str, Any]:
        """Run ``task`` over ``records``, compute metrics, and write artifacts.

        ``model_tier`` labels which model produced these predictions
        (e.g. "small_lm_baseline", "fine_tuned_rust", "llm_no_rag", "llm_rag")
        so results from multiple runs can be concatenated into the final
        4-model comparison table.
        """
        outputs = task.run_batch(records)
        reference_key = _REFERENCE_KEYS.get(task.task_name)
        predictions = [o["prediction"] for o in outputs]
        references = [str(o.get(reference_key, "")) for o in outputs] if reference_key else []

        metrics: dict[str, Any] = {}
        if references and any(references):
            metrics["exact_match"] = exact_match(predictions, references)
            metrics["codebleu"] = compute_codebleu(predictions, references, language=language)
            metrics["bertscore"] = compute_bertscore(predictions, references)

        manual_sample = sample_for_manual_inspection(outputs, n=20)

        run_name = f"{task.task_name}__{model_tier}"
        write_jsonl(outputs, self.results_dir / f"{run_name}__predictions.jsonl")
        write_jsonl(manual_sample, self.results_dir / f"{run_name}__manual_review_sample.jsonl")
        write_json(metrics, self.results_dir / f"{run_name}__metrics.json")

        logger.info("[%s / %s] metrics: %s", task.task_name, model_tier, metrics)
        return {
            "task": task.task_name,
            "model_tier": model_tier,
            "n_examples": len(outputs),
            "metrics": metrics,
        }

    def evaluate_sql_task(
        self,
        task: BaseTask,
        records: list[dict[str, Any]],
        model_tier: str,
        dataset_name: str = "spider",
    ) -> dict[str, Any]:
        """SQL-specific evaluation: runs the task, then computes execution
        accuracy by actually running predicted vs. gold SQL against each
        record's SQLite database (Task 2's primary metric per the proposal).

        ``records`` must each contain ``question``, ``schema`` (a
        ``DatabaseSchema``), ``gold_sql``, and ``db_path``.
        """
        outputs = task.run_batch(records)
        predictions = [o["prediction"] for o in outputs]
        gold = [o.get("gold_sql", "") for o in outputs]
        db_paths = [o["db_path"] for o in outputs]

        exec_result = execution_accuracy(predictions, gold, db_paths)
        metrics = {"execution_accuracy": exec_result}

        manual_sample = sample_for_manual_inspection(outputs, n=20)

        run_name = f"sql_generation__{dataset_name}__{model_tier}"
        # `schema`/`db_path` objects aren't JSON-serializable as-is; drop them
        # from the persisted predictions and keep only primitive fields.
        serializable_outputs = [
            {k: v for k, v in o.items() if k not in ("schema", "db_path")} for o in outputs
        ]
        write_jsonl(serializable_outputs, self.results_dir / f"{run_name}__predictions.jsonl")
        write_jsonl(
            [{k: v for k, v in s.items() if k not in ("schema", "db_path")} for s in manual_sample],
            self.results_dir / f"{run_name}__manual_review_sample.jsonl",
        )
        write_json(metrics, self.results_dir / f"{run_name}__metrics.json")

        logger.info(
            "[sql_generation / %s / %s] execution_accuracy=%.3f (%d/%d)",
            dataset_name,
            model_tier,
            exec_result["execution_accuracy"],
            exec_result["correct"],
            exec_result["total"],
        )
        return {
            "task": f"sql_generation_{dataset_name}",
            "model_tier": model_tier,
            "n_examples": len(outputs),
            "metrics": metrics,
        }

    def build_comparison_table(self, evaluation_summaries: list[dict[str, Any]]) -> pd.DataFrame:
        """Flatten a list of evaluate_task()/evaluate_sql_task() summaries into
        the CSV comparison table required by the project deliverables
        (`results/comparison_table.csv`).

        Each checkpoint notebook runs as an independent Colab session and
        calls this with only its own summaries. This merges with whatever
        the file already has on disk (from earlier checkpoints) rather than
        overwriting it -- otherwise Checkpoint 2's call would silently wipe
        out Checkpoint 1's rows, leaving Checkpoint 4's "final
        cross-checkpoint comparison table" showing only the last checkpoint
        that happened to run. Rows are deduplicated on (task, model_tier),
        keeping the newest entry so re-running a checkpoint updates its own
        rows in place instead of duplicating them.
        """
        rows = []
        for summary in evaluation_summaries:
            metrics = summary["metrics"]
            row = {
                "task": summary["task"],
                "model_tier": summary["model_tier"],
                "n_examples": summary["n_examples"],
                "exact_match": metrics.get("exact_match"),
                "codebleu": (metrics.get("codebleu") or {}).get("codebleu"),
                "bertscore_f1": (metrics.get("bertscore") or {}).get("f1"),
                "execution_accuracy": (metrics.get("execution_accuracy") or {}).get("execution_accuracy"),
            }
            rows.append(row)

        new_df = pd.DataFrame(rows)
        out_path = self.results_dir / "comparison_table.csv"

        if out_path.exists():
            existing_df = pd.read_csv(out_path)
            combined = pd.concat([existing_df, new_df], ignore_index=True)
            combined = combined.drop_duplicates(subset=["task", "model_tier"], keep="last")
        else:
            combined = new_df

        combined.to_csv(out_path, index=False)
        logger.info(
            "Wrote comparison table (%d total rows, %d from this run) to %s",
            len(combined),
            len(new_df),
            out_path,
        )
        return combined
