"""Top-K (and dynamic Top-K) retrieval experiments, plus the 4-tier model
comparison (small LM baseline, LLM no-RAG, LLM+RAG, fine-tuned model+RAG)
required by Checkpoint 3, and specifically the Checkpoint 4 requirement of
putting the team's own fine-tuned model into the RAG system and evaluating
it (the ``fine_tuned_rag`` tier).

For the richer, per-task metric suite (exact_match / CodeBLEU / BERTScore,
not just CodeBLEU) that lands in the project's main comparison_table.csv,
see ``codegen_rag.rag.rag_task_adapter.RAGAugmentedTask``, which wraps any
task module + RAGPipeline + generate_fn so it can be scored through the
same ``Evaluator.evaluate_task()`` path as every other tier.
"""

from __future__ import annotations

from typing import Any, Callable

import pandas as pd

from codegen_rag.evaluation.metrics import compute_codebleu
from codegen_rag.rag.ast_retrieval import ASTRetrievalIndex
from codegen_rag.rag.faiss_index import CodeSearchIndex
from codegen_rag.rag.pipeline import RAGPipeline, RetrievalStrategy
from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


def run_topk_experiment(
    eval_records: list[dict[str, Any]],
    dense_index: CodeSearchIndex,
    ast_index: ASTRetrievalIndex,
    embed_fn: Callable[[str], Any],
    generate_fn: Callable[[str], str],
    k_values: list[int] | None = None,
    strategies: list[RetrievalStrategy] | None = None,
    language: str = "python",
    query_key: str = "intent",
    reference_key: str = "code",
    include_dynamic: bool = True,
) -> pd.DataFrame:
    """Sweep retrieval strategy x Top-K, generate for every eval record under
    each configuration, and score with CodeBLEU. Returns one row per
    (strategy, K) configuration — this is the artifact behind "evidence of the
    optimal top-K value for RAG retrieval" in the proposal's expected outcomes.
    """
    k_values = k_values or [1, 3, 5, 10]
    strategies = strategies or ["dense", "ast", "hybrid"]

    rows: list[dict[str, Any]] = []

    for strategy in strategies:
        for k in k_values:
            pipeline = RAGPipeline(
                dense_index=dense_index,
                ast_index=ast_index,
                embed_fn=embed_fn,
                strategy=strategy,
                top_k=k,
            )
            predictions, references = [], []
            for record in eval_records:
                result = pipeline.generate(record[query_key], generate_fn)
                predictions.append(result.generation)
                references.append(str(record.get(reference_key, "")))

            metric = compute_codebleu(predictions, references, language=language)
            rows.append(
                {
                    "strategy": strategy,
                    "top_k": k,
                    "dynamic": False,
                    "n_examples": len(eval_records),
                    "codebleu": metric["codebleu"],
                }
            )
            logger.info("strategy=%s K=%d codebleu=%.4f", strategy, k, metric["codebleu"])

        if include_dynamic:
            dynamic_pipeline = RAGPipeline(
                dense_index=dense_index,
                ast_index=ast_index,
                embed_fn=embed_fn,
                strategy=strategy,
                top_k=max(k_values),
                use_dynamic_top_k=True,
            )
            predictions, references = [], []
            for record in eval_records:
                result = dynamic_pipeline.generate(record[query_key], generate_fn)
                predictions.append(result.generation)
                references.append(str(record.get(reference_key, "")))
            metric = compute_codebleu(predictions, references, language=language)
            rows.append(
                {
                    "strategy": strategy,
                    "top_k": "dynamic",
                    "dynamic": True,
                    "n_examples": len(eval_records),
                    "codebleu": metric["codebleu"],
                }
            )
            logger.info("strategy=%s K=dynamic codebleu=%.4f", strategy, metric["codebleu"])

    return pd.DataFrame(rows)


def select_best_configuration(topk_results: pd.DataFrame) -> dict[str, Any]:
    """Pick the (strategy, K) row with the highest CodeBLEU — the "optimal
    top-K value" the proposal's expected outcomes ask for."""
    best_row = topk_results.loc[topk_results["codebleu"].idxmax()]
    return best_row.to_dict()


def run_four_tier_comparison(
    eval_records: list[dict[str, Any]],
    small_lm_generate_fn: Callable[[str], str],
    llm_generate_fn: Callable[[str], str],
    rag_pipeline: RAGPipeline,
    fine_tuned_rag_pipeline: RAGPipeline | None,
    fine_tuned_generate_fn: Callable[[str], str] | None = None,
    language: str = "python",
    query_key: str = "intent",
    reference_key: str = "code",
) -> pd.DataFrame:
    """Produce the core Checkpoint-3/4 deliverable: small LM vs. LLM (no RAG)
    vs. LLM+RAG vs. fine-tuned-model+RAG ("their model" put into the RAG
    system, per Checkpoint 4's requirement), scored with CodeBLEU.

    ``fine_tuned_generate_fn`` is the fine-tuned model's own generate
    callable and is what actually drives the ``fine_tuned_rag`` tier. It is
    kept separate from ``small_lm_generate_fn`` (which drives the untouched
    baseline tier) on purpose: reusing ``small_lm_generate_fn`` for both
    would silently make the "fine-tuned + RAG" tier just "base model + RAG"
    again, defeating the point of the comparison. For backward
    compatibility, if a ``fine_tuned_rag_pipeline`` is supplied without an
    explicit ``fine_tuned_generate_fn``, this falls back to
    ``small_lm_generate_fn`` and logs a warning, since that was the
    (incorrect) implicit behavior before this fix.
    """
    tiers: dict[str, list[str]] = {
        "small_lm_baseline": [],
        "llm_no_rag": [],
        "llm_rag": [],
    }
    if fine_tuned_rag_pipeline is not None:
        tiers["fine_tuned_rag"] = []
        if fine_tuned_generate_fn is None:
            logger.warning(
                "fine_tuned_rag_pipeline was provided without a distinct "
                "fine_tuned_generate_fn -- falling back to small_lm_generate_fn, "
                "which means the 'fine_tuned_rag' tier will actually be running "
                "the base model, not your fine-tuned checkpoint. Pass "
                "fine_tuned_generate_fn explicitly to evaluate your fine-tuned "
                "model inside the RAG system."
            )
            fine_tuned_generate_fn = small_lm_generate_fn

    references = [str(r.get(reference_key, "")) for r in eval_records]

    for record in eval_records:
        query = record[query_key]
        tiers["small_lm_baseline"].append(small_lm_generate_fn(query))
        tiers["llm_no_rag"].append(llm_generate_fn(query))
        tiers["llm_rag"].append(rag_pipeline.generate(query, llm_generate_fn).generation)
        if fine_tuned_rag_pipeline is not None:
            tiers["fine_tuned_rag"].append(
                fine_tuned_rag_pipeline.generate(query, fine_tuned_generate_fn).generation
            )

    rows = []
    for tier_name, predictions in tiers.items():
        metric = compute_codebleu(predictions, references, language=language)
        rows.append({"model_tier": tier_name, "n_examples": len(eval_records), "codebleu": metric["codebleu"]})
        logger.info("[four-tier] %s codebleu=%.4f", tier_name, metric["codebleu"])

    return pd.DataFrame(rows)
