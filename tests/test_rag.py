from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from codegen_rag.rag.ast_retrieval import ASTRetrievalIndex, ast_similarity, extract_ast_node_sequence
from codegen_rag.rag.context_packing import build_augmented_prompt, dynamic_top_k, pack_context
from codegen_rag.rag.faiss_index import CodeSearchIndex
from codegen_rag.rag.hybrid_retrieval import HybridRetriever, reciprocal_rank_fusion
from codegen_rag.rag.pipeline import RAGPipeline

# ---------------------------------------------------------------------------
# FAISS dense index
# ---------------------------------------------------------------------------


def _random_embeddings(n: int, dim: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(size=(n, dim)).astype("float32")


def test_faiss_index_build_and_search_returns_top_k():
    dim = 16
    embeddings = _random_embeddings(20, dim)
    metadata = [{"code": f"snippet_{i}"} for i in range(20)]

    index = CodeSearchIndex(dim=dim, use_ivf=True)
    index.build(embeddings, metadata)

    results = index.search(embeddings[0], top_k=5)
    assert len(results) == 5
    # The query vector itself should be its own nearest neighbor.
    assert results[0]["code"] == "snippet_0"


def test_faiss_index_falls_back_to_flat_for_small_corpus():
    dim = 8
    embeddings = _random_embeddings(10, dim)
    metadata = [{"code": f"s{i}"} for i in range(10)]
    index = CodeSearchIndex(dim=dim, use_ivf=True, nlist=100)
    index.build(embeddings, metadata)
    assert index.used_ivf is False  # too few points to train 100 clusters


def test_faiss_index_add_appends_without_rebuild():
    dim = 8
    index = CodeSearchIndex(dim=dim, use_ivf=False)
    index.build(_random_embeddings(5, dim), [{"code": f"a{i}"} for i in range(5)])
    index.add(_random_embeddings(3, dim, seed=1), [{"code": f"b{i}"} for i in range(3)])
    assert len(index) == 8


def test_faiss_index_save_and_load_roundtrip(tmp_path: Path):
    dim = 8
    embeddings = _random_embeddings(15, dim)
    metadata = [{"code": f"s{i}", "chunk_id": i} for i in range(15)]
    index = CodeSearchIndex(dim=dim, use_ivf=False)
    index.build(embeddings, metadata)
    index.save(tmp_path / "idx")

    loaded = CodeSearchIndex.load(tmp_path / "idx")
    results = loaded.search(embeddings[0], top_k=3)
    assert len(results) == 3
    assert results[0]["code"] == "s0"


def test_faiss_index_search_before_build_raises():
    index = CodeSearchIndex(dim=8)
    with pytest.raises(RuntimeError):
        index.search(_random_embeddings(1, 8)[0])


# ---------------------------------------------------------------------------
# AST retrieval
# ---------------------------------------------------------------------------


def test_extract_ast_node_sequence_python():
    seq = extract_ast_node_sequence("def f(x):\n    return x + 1", language="python")
    assert "FunctionDef" in seq
    assert "Return" in seq


def test_extract_ast_node_sequence_handles_syntax_error_gracefully():
    seq = extract_ast_node_sequence("def f(:\n  broken", language="python")
    assert isinstance(seq, list)  # falls back to structural tokenizer, never raises


def test_extract_ast_node_sequence_non_python_uses_fallback():
    seq = extract_ast_node_sequence("fn main() { if true { println!(1); } }", language="rust")
    assert "if" in seq


def test_ast_similarity_identical_sequences_is_one():
    seq = ["FunctionDef", "Return", "BinOp"]
    assert ast_similarity(seq, seq) == 1.0


def test_ast_similarity_disjoint_sequences_is_zero():
    assert ast_similarity(["FunctionDef"], ["ClassDef"]) == 0.0


def test_ast_similarity_empty_sequences():
    assert ast_similarity([], []) == 1.0
    assert ast_similarity(["X"], []) == 0.0


def test_ast_retrieval_index_ranks_structurally_similar_code_higher():
    codes = [
        "def add(a, b):\n    return a + b",
        "def sub(a, b):\n    return a - b",
        "class Foo:\n    pass",
    ]
    metadata = [{"code": c} for c in codes]
    index = ASTRetrievalIndex(language="python")
    index.build(codes, metadata)

    results = index.search("def mul(a, b):\n    return a * b", top_k=3)
    # The two similar function definitions should outrank the unrelated class.
    top_two_codes = {results[0]["code"], results[1]["code"]}
    assert codes[0] in top_two_codes
    assert codes[1] in top_two_codes


# ---------------------------------------------------------------------------
# Hybrid retrieval
# ---------------------------------------------------------------------------


def test_reciprocal_rank_fusion_boosts_items_ranked_high_in_both_lists():
    list_a = [{"chunk_id": 1}, {"chunk_id": 2}, {"chunk_id": 3}]
    list_b = [{"chunk_id": 2}, {"chunk_id": 1}, {"chunk_id": 4}]
    fused = reciprocal_rank_fusion([list_a, list_b], top_k=3)
    fused_ids = [f["chunk_id"] for f in fused]
    # chunk 1 and 2 both appear near the top of both lists -> should lead.
    assert set(fused_ids[:2]) == {1, 2}


def test_reciprocal_rank_fusion_respects_top_k():
    lists = [[{"chunk_id": i} for i in range(10)]]
    fused = reciprocal_rank_fusion(lists, top_k=3)
    assert len(fused) == 3


def test_hybrid_retriever_combines_dense_and_ast(monkeypatch):
    dim = 8
    embeddings = _random_embeddings(5, dim)
    codes = ["def add(a,b): return a+b"] * 5
    metadata = [{"code": codes[i], "chunk_id": i} for i in range(5)]

    dense = CodeSearchIndex(dim=dim, use_ivf=False)
    dense.build(embeddings, metadata)

    ast_index = ASTRetrievalIndex()
    ast_index.build(codes, [{"code": codes[i], "chunk_id": i} for i in range(5)])

    hybrid = HybridRetriever(dense, ast_index)
    results = hybrid.search("def add(a,b): return a+b", embeddings[0], top_k=3)
    assert len(results) == 3
    assert all("fusion_score" in r for r in results)


# ---------------------------------------------------------------------------
# Context packing / dynamic top-K
# ---------------------------------------------------------------------------


def test_pack_context_respects_max_chars():
    chunks = [{"code": "x" * 100, "score": 0.9} for _ in range(10)]
    packed = pack_context(chunks, max_chars=250)
    assert len(packed) <= 400  # header text adds some overhead, but bounded


def test_pack_context_always_includes_at_least_one_chunk():
    chunks = [{"code": "y" * 5000, "score": 0.9}]
    packed = pack_context(chunks, max_chars=10)
    assert "y" * 5000 in packed  # never drops the top chunk even if it overflows alone


def test_build_augmented_prompt_includes_all_parts():
    prompt = build_augmented_prompt("query text", "context text", "instruction text")
    assert "query text" in prompt
    assert "context text" in prompt
    assert "instruction text" in prompt


def test_dynamic_top_k_filters_by_threshold():
    results = [{"score": 0.9}, {"score": 0.7}, {"score": 0.3}, {"score": 0.1}]
    selected = dynamic_top_k(results, min_k=1, max_k=10, score_threshold=0.5)
    assert len(selected) == 2


def test_dynamic_top_k_falls_back_to_min_k_when_nothing_clears_threshold():
    results = [{"score": 0.1}, {"score": 0.05}]
    selected = dynamic_top_k(results, min_k=1, max_k=10, score_threshold=0.9)
    assert len(selected) == 1


def test_dynamic_top_k_respects_max_k():
    results = [{"score": 0.9 - i * 0.01} for i in range(20)]
    selected = dynamic_top_k(results, min_k=1, max_k=5, score_threshold=0.5)
    assert len(selected) == 5


# ---------------------------------------------------------------------------
# RAG pipeline (dependency-injected embed_fn / generate_fn — no real model needed)
# ---------------------------------------------------------------------------


def test_rag_pipeline_dense_strategy_end_to_end():
    dim = 8
    embeddings = _random_embeddings(6, dim)
    codes = [f"def f{i}(): return {i}" for i in range(6)]
    metadata = [{"code": codes[i], "chunk_id": i} for i in range(6)]

    dense = CodeSearchIndex(dim=dim, use_ivf=False)
    dense.build(embeddings, metadata)

    pipeline = RAGPipeline(dense_index=dense, embed_fn=lambda q: embeddings[0], strategy="dense", top_k=3)
    result = pipeline.generate("write a function", generate_fn=lambda p: "GENERATED")

    assert result.generation == "GENERATED"
    assert len(result.retrieved_chunks) == 3
    assert "write a function" in result.augmented_prompt


def test_rag_pipeline_ast_strategy_does_not_require_embed_fn():
    codes = ["def add(a,b): return a+b", "class Foo: pass"]
    ast_index = ASTRetrievalIndex()
    ast_index.build(codes, [{"code": c, "chunk_id": i} for i, c in enumerate(codes)])

    pipeline = RAGPipeline(ast_index=ast_index, strategy="ast", top_k=1)
    result = pipeline.generate("def mul(a,b): return a*b", generate_fn=lambda p: "OK")
    assert result.generation == "OK"
    assert len(result.retrieved_chunks) == 1


def test_rag_pipeline_missing_dependencies_raises_valueerror():
    with pytest.raises(ValueError):
        RAGPipeline(strategy="dense")  # no dense_index/embed_fn provided


def test_rag_pipeline_hybrid_with_dynamic_top_k():
    dim = 8
    embeddings = _random_embeddings(8, dim)
    codes = [f"def f{i}(a): return a+{i}" for i in range(8)]
    metadata = [{"code": codes[i], "chunk_id": i} for i in range(8)]

    dense = CodeSearchIndex(dim=dim, use_ivf=False)
    dense.build(embeddings, metadata)
    ast_index = ASTRetrievalIndex()
    ast_index.build(codes, [{"code": codes[i], "chunk_id": i} for i in range(8)])

    pipeline = RAGPipeline(
        dense_index=dense,
        ast_index=ast_index,
        embed_fn=lambda q: embeddings[0],
        strategy="hybrid",
        top_k=4,
        use_dynamic_top_k=True,
        dynamic_top_k_kwargs={"min_k": 1, "score_threshold": 0.0},
    )
    result = pipeline.generate("def new_fn(a): return a", generate_fn=lambda p: "GEN")
    assert result.generation == "GEN"
    assert len(result.retrieved_chunks) <= 4
