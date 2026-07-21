"""Top-K (and dynamic Top-K) retrieval experiments, plus the 4-tier model
comparison (small LM baseline, LLM no-RAG, LLM+RAG, fine-tuned model+RAG)
required by Checkpoint 3.
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
    language: str = "python",
    query_key: str = "intent",
    reference_key: str = "code",
) -> pd.DataFrame:
    """Produce the core Checkpoint-3 deliverable: small LM vs. LLM (no RAG)
    vs. LLM+RAG vs. fine-tuned-model+RAG, scored with CodeBLEU."""
    tiers: dict[str, list[str]] = {
        "small_lm_baseline": [],
        "llm_no_rag": [],
        "llm_rag": [],
    }
    if fine_tuned_rag_pipeline is not None:
        tiers["fine_tuned_rag"] = []

    references = [str(r.get(reference_key, "")) for r in eval_records]

    for record in eval_records:
        query = record[query_key]
        tiers["small_lm_baseline"].append(small_lm_generate_fn(query))
        tiers["llm_no_rag"].append(llm_generate_fn(query))
        tiers["llm_rag"].append(rag_pipeline.generate(query, llm_generate_fn).generation)
        if fine_tuned_rag_pipeline is not None:
            tiers["fine_tuned_rag"].append(
                fine_tuned_rag_pipeline.generate(query, small_lm_generate_fn).generation
            )

    rows = []
    for tier_name, predictions in tiers.items():
        metric = compute_codebleu(predictions, references, language=language)
        rows.append({"model_tier": tier_name, "n_examples": len(eval_records), "codebleu": metric["codebleu"]})
        logger.info("[four-tier] %s codebleu=%.4f", tier_name, metric["codebleu"])

    return pd.DataFrame(rows)
