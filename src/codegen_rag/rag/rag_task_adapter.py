"""Adapter that wraps an existing task module with a RAGPipeline so any
model tier's generate function -- the untouched small LM, the fine-tuned
Rust checkpoint, or an upper-bound LLM client -- can be evaluated with
retrieval augmentation through the *same* scoring path as every other tier.

Why this exists: ``codegen_rag.rag.topk_experiment.run_four_tier_comparison``
scores its tiers with CodeBLEU only, into its own standalone DataFrame. The
project's main deliverable, ``results/comparison_table.csv``, is instead
built by ``Evaluator.build_comparison_table()`` from a list of
``Evaluator.evaluate_task()`` summaries -- and until now nothing fed a
RAG-augmented run through that path, so ``comparison_table.csv`` only ever
had rows for tiers that were run with a plain (non-RAG) task module, i.e.
``small_lm_baseline``. In particular, Checkpoint 4's explicit requirement
to "put their model into the RAG system and evaluate" had no route into the
project's actual results table.

``RAGAugmentedTask`` closes that gap: it duck-types the ``task_name`` /
``run_batch`` surface ``Evaluator.evaluate_task()`` expects (it does not
subclass ``BaseTask`` because ``BaseTask.__init__`` requires a
``CodeGenModel`` instance specifically, whereas here the "model" backing a
tier can just as easily be an upper-bound LLM client). Once wrapped, calling

    evaluator.evaluate_task(
        RAGAugmentedTask(program_synthesis_task, rag_pipeline, fine_tuned_generate_fn),
        records,
        model_tier="fine_tuned_rag",
    )

produces a full exact_match / CodeBLEU / BERTScore row for the
``fine_tuned_rag`` tier that merges into ``comparison_table.csv`` exactly
like every other tier -- no separate reporting path, no risk of the two
tables drifting apart.
"""

from __future__ import annotations

from typing import Any, Callable

from codegen_rag.rag.pipeline import RAGPipeline
from codegen_rag.tasks.base_task import BaseTask
from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


class RAGAugmentedTask:
    """Wraps ``base_task`` so every generation for it is retrieval-augmented
    via ``rag_pipeline`` and produced by ``generate_fn`` instead of
    ``base_task.model.generate``.

    ``generate_fn`` is deliberately a plain ``str -> str`` callable rather
    than a ``CodeGenModel`` so this works identically whether the tier being
    evaluated is the team's fine-tuned checkpoint
    (``lambda p: fine_tuned_model.generate(p, gen_config)[0]``) or an
    upper-bound LLM client (``lambda p: llm_client.generate(p).text``).
    """

    def __init__(
        self,
        base_task: BaseTask,
        rag_pipeline: RAGPipeline,
        generate_fn: Callable[[str], str],
        query_key: str = "intent",
    ):
        self.base_task = base_task
        self.rag_pipeline = rag_pipeline
        self.generate_fn = generate_fn
        self.query_key = query_key
        # Mirrors BaseTask.task_name so Evaluator._REFERENCE_KEYS lookups
        # (keyed on task_name) resolve exactly as they do for a plain task.
        self.task_name = base_task.task_name

    def run(self, record: dict[str, Any]) -> dict[str, Any]:
        task_prompt = self.base_task.build_prompt(record)
        if self.query_key in record and record[self.query_key]:
            # Retrieve on the short natural-language query (e.g. "intent"),
            # but still pass the task's own formatted prompt as
            # task_instruction so the model keeps its task-specific framing
            # (e.g. program synthesis's triple-quote docstring wrapper).
            query = str(record[self.query_key])
            task_instruction = task_prompt
        else:
            # Tasks without a separate query field (documentation
            # generation, commit-message generation, code translation) key
            # their prompt directly off the record, so the task prompt
            # *is* the query -- passing it again as task_instruction would
            # duplicate the same text back-to-back in the augmented prompt.
            query = task_prompt
            task_instruction = ""

        result = self.rag_pipeline.generate(query, self.generate_fn, task_instruction=task_instruction)
        prediction = self.base_task.postprocess(result.generation)
        return {
            **record,
            "prompt": result.augmented_prompt,
            "prediction": prediction,
            "task": self.task_name,
            "retrieved_k": len(result.retrieved_chunks),
            "retrieval_strategy": result.strategy,
        }

    def run_batch(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results = []
        for i, record in enumerate(records):
            results.append(self.run(record))
            if (i + 1) % 25 == 0:
                logger.info("[%s+RAG] processed %d/%d", self.task_name, i + 1, len(records))
        return results
