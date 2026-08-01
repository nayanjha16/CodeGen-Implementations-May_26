from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from codegen_rag.rag.corpus_indexing import build_indexes_from_corpus, load_indexes, save_indexes
from codegen_rag.rag.topk_experiment import (
    run_four_tier_comparison,
    run_topk_experiment,
    select_best_configuration,
)


def _fake_embed_fn(dim: int):
    rng = np.random.default_rng(0)
    cache: dict[str, np.ndarray] = {}

    def _embed(texts):
        if isinstance(texts, str):
            texts = [texts]
        out = []
        for t in texts:
            if t not in cache:
                cache[t] = rng.normal(size=dim).astype("float32")
            out.append(cache[t])
        return np.stack(out) if len(out) > 1 else out[0]

    return _embed


@pytest.fixture
def small_corpus() -> list[dict]:
    return [
        {"code": f"def f{i}(a, b):\n    return a + b + {i}", "intent": f"add numbers variant {i}"}
        for i in range(12)
    ]


def test_build_indexes_from_corpus_produces_aligned_chunk_ids(small_corpus):
    dim = 16
    embed_fn = _fake_embed_fn(dim)
    dense_index, ast_index = build_indexes_from_corpus(
        small_corpus, embed_fn=lambda texts: np.stack([embed_fn(t) for t in texts]), embedding_dim=dim
    )
    assert len(dense_index) == len(small_corpus)
    assert len(ast_index) == len(small_corpus)


def test_save_and_load_indexes_roundtrip(tmp_path: Path, small_corpus):
    dim = 16
    embed_fn = _fake_embed_fn(dim)
    dense_index, ast_index = build_indexes_from_corpus(
        small_corpus, embed_fn=lambda texts: np.stack([embed_fn(t) for t in texts]), embedding_dim=dim
    )
    save_indexes(dense_index, ast_index, tmp_path / "rag_indexes")
    loaded_dense, loaded_ast = load_indexes(tmp_path / "rag_indexes")
    assert len(loaded_dense) == len(dense_index)
    assert len(loaded_ast) == len(ast_index)


def test_run_topk_experiment_returns_row_per_strategy_and_k(small_corpus):
    dim = 16
    embed_fn = _fake_embed_fn(dim)
    dense_index, ast_index = build_indexes_from_corpus(
        small_corpus, embed_fn=lambda texts: np.stack([embed_fn(t) for t in texts]), embedding_dim=dim
    )
    eval_records = small_corpus[:3]

    df = run_topk_experiment(
        eval_records,
        dense_index,
        ast_index,
        embed_fn=embed_fn,
        generate_fn=lambda prompt: "def f(a, b):\n    return a + b",
        k_values=[1, 3],
        strategies=["dense", "ast"],
        include_dynamic=True,
    )
    # 2 strategies * (2 K values + 1 dynamic row) = 6 rows
    assert len(df) == 6
    assert set(df["strategy"]) == {"dense", "ast"}
    assert "dynamic" in df["top_k"].values


def test_select_best_configuration_picks_max_codebleu():
    import pandas as pd

    df = pd.DataFrame(
        [
            {"strategy": "dense", "top_k": 1, "codebleu": 0.2},
            {"strategy": "hybrid", "top_k": 5, "codebleu": 0.8},
            {"strategy": "ast", "top_k": 3, "codebleu": 0.5},
        ]
    )
    best = select_best_configuration(df)
    assert best["strategy"] == "hybrid"
    assert best["codebleu"] == 0.8


def test_run_four_tier_comparison_produces_all_tiers(small_corpus):
    dim = 16
    embed_fn = _fake_embed_fn(dim)
    dense_index, ast_index = build_indexes_from_corpus(
        small_corpus, embed_fn=lambda texts: np.stack([embed_fn(t) for t in texts]), embedding_dim=dim
    )
    from codegen_rag.rag.pipeline import RAGPipeline

    rag_pipeline = RAGPipeline(dense_index=dense_index, ast_index=ast_index, embed_fn=embed_fn, strategy="hybrid", top_k=2)
    ft_rag_pipeline = RAGPipeline(dense_index=dense_index, ast_index=ast_index, embed_fn=embed_fn, strategy="dense", top_k=2)

    df = run_four_tier_comparison(
        small_corpus[:2],
        small_lm_generate_fn=lambda q: "def f(a,b): return a+b",
        llm_generate_fn=lambda q: "def f(a,b): return a+b # llm",
        rag_pipeline=rag_pipeline,
        fine_tuned_rag_pipeline=ft_rag_pipeline,
    )
    assert set(df["model_tier"]) == {"small_lm_baseline", "llm_no_rag", "llm_rag", "fine_tuned_rag"}


def test_fine_tuned_generate_fn_is_used_not_small_lm_generate_fn(small_corpus):
    """Regression test for the parameter-conflation bug: before this fix,
    the fine_tuned_rag tier silently reused small_lm_generate_fn, which
    means it was evaluating the base model wrapped in RAG, not the team's
    actual fine-tuned checkpoint. Passing a distinct fine_tuned_generate_fn
    must make the fine_tuned_rag tier's predictions come from it."""
    dim = 16
    embed_fn = _fake_embed_fn(dim)
    dense_index, ast_index = build_indexes_from_corpus(
        small_corpus, embed_fn=lambda texts: np.stack([embed_fn(t) for t in texts]), embedding_dim=dim
    )
    from codegen_rag.rag.pipeline import RAGPipeline

    rag_pipeline = RAGPipeline(dense_index=dense_index, ast_index=ast_index, embed_fn=embed_fn, strategy="hybrid", top_k=2)
    ft_rag_pipeline = RAGPipeline(dense_index=dense_index, ast_index=ast_index, embed_fn=embed_fn, strategy="dense", top_k=2)

    calls = {"small_lm": 0, "fine_tuned": 0}

    def small_lm_generate_fn(q):
        calls["small_lm"] += 1
        return "def f(a,b): return a+b  # base model"

    def fine_tuned_generate_fn(q):
        calls["fine_tuned"] += 1
        return "fn f(a: i32, b: i32) -> i32 { a + b }  // fine-tuned rust model"

    df = run_four_tier_comparison(
        small_corpus[:2],
        small_lm_generate_fn=small_lm_generate_fn,
        llm_generate_fn=lambda q: "def f(a,b): return a+b # llm",
        rag_pipeline=rag_pipeline,
        fine_tuned_rag_pipeline=ft_rag_pipeline,
        fine_tuned_generate_fn=fine_tuned_generate_fn,
    )

    assert "fine_tuned_rag" in set(df["model_tier"])
    # The fine-tuned generate_fn must actually have been invoked ...
    assert calls["fine_tuned"] == 2
    # ... and small_lm_generate_fn should only have been called for its own
    # baseline tier (2 records), not also inside the fine_tuned_rag branch.
    assert calls["small_lm"] == 2


def test_fine_tuned_generate_fn_falls_back_with_warning_when_omitted(small_corpus, caplog):
    """Backward-compat: omitting fine_tuned_generate_fn still works (falls
    back to small_lm_generate_fn) but now logs a warning explaining that
    the fine_tuned_rag tier won't actually reflect the fine-tuned model."""
    dim = 16
    embed_fn = _fake_embed_fn(dim)
    dense_index, ast_index = build_indexes_from_corpus(
        small_corpus, embed_fn=lambda texts: np.stack([embed_fn(t) for t in texts]), embedding_dim=dim
    )
    from codegen_rag.rag.pipeline import RAGPipeline

    rag_pipeline = RAGPipeline(dense_index=dense_index, ast_index=ast_index, embed_fn=embed_fn, strategy="hybrid", top_k=2)
    ft_rag_pipeline = RAGPipeline(dense_index=dense_index, ast_index=ast_index, embed_fn=embed_fn, strategy="dense", top_k=2)

    with caplog.at_level("WARNING"):
        df = run_four_tier_comparison(
            small_corpus[:2],
            small_lm_generate_fn=lambda q: "code",
            llm_generate_fn=lambda q: "code",
            rag_pipeline=rag_pipeline,
            fine_tuned_rag_pipeline=ft_rag_pipeline,
        )

    assert "fine_tuned_rag" in set(df["model_tier"])
    assert any("fine_tuned_generate_fn" in record.message for record in caplog.records)


def test_run_four_tier_comparison_without_fine_tuned_tier(small_corpus):
    dim = 16
    embed_fn = _fake_embed_fn(dim)
    dense_index, ast_index = build_indexes_from_corpus(
        small_corpus, embed_fn=lambda texts: np.stack([embed_fn(t) for t in texts]), embedding_dim=dim
    )
    from codegen_rag.rag.pipeline import RAGPipeline

    rag_pipeline = RAGPipeline(dense_index=dense_index, ast_index=ast_index, embed_fn=embed_fn, strategy="hybrid", top_k=2)

    df = run_four_tier_comparison(
        small_corpus[:2],
        small_lm_generate_fn=lambda q: "code",
        llm_generate_fn=lambda q: "code",
        rag_pipeline=rag_pipeline,
        fine_tuned_rag_pipeline=None,
    )
    assert "fine_tuned_rag" not in set(df["model_tier"])
