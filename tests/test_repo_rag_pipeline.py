"""Tests for repository RAG retrieval helpers."""

import json
from unittest import mock

import numpy as np

from inference.repo_rag_pipeline import (
    RepoRAGPipeline,
    clear_repo_rag_cache,
    get_repo_rag_pipeline,
)


def _fake_pipeline(chunks: list[dict], scores: list[float]) -> RepoRAGPipeline:
    """Pipeline stub whose index returns fixed scores in chunk order."""
    pipeline = RepoRAGPipeline.__new__(RepoRAGPipeline)
    pipeline.chunks_meta = chunks

    class FakeIndex:
        def search(self, embedding, fetch_k):
            take = min(fetch_k, len(chunks))
            return (
                np.array([scores[:take]]),
                np.array([list(range(take))]),
            )

    pipeline.index = FakeIndex()
    pipeline._encode = lambda texts: [[0.0]]  # type: ignore[method-assign]
    return pipeline


def _chunk(file_path: str, chunk_type: str = "class", name: str = "X") -> dict:
    return {
        "content": f"content of {file_path}",
        "metadata": {"file_path": file_path, "type": chunk_type, "name": name},
    }


def test_retrieve_dedupes_by_file():
    pipeline = RepoRAGPipeline.__new__(RepoRAGPipeline)
    pipeline.chunks_meta = [
        {
            "content": "class A1",
            "metadata": {"file_path": "A.java", "type": "class", "name": "A1"},
        },
        {
            "content": "class A2",
            "metadata": {"file_path": "A.java", "type": "class", "name": "A2"},
        },
        {
            "content": "class B",
            "metadata": {"file_path": "B.java", "type": "class", "name": "B"},
        },
    ]

    scores = iter([0.9, 0.85, 0.8, 0.75])
    indices = iter([0, 1, 2, 0])

    class FakeIndex:
        def search(self, embedding, fetch_k):
            import numpy as np

            row_scores = [next(scores) for _ in range(fetch_k)]
            row_indices = [next(indices) for _ in range(fetch_k)]
            return np.array([row_scores]), np.array([row_indices])

    pipeline.index = FakeIndex()
    pipeline._encode = lambda texts: [[0.0]]  # type: ignore[method-assign]

    results = pipeline.retrieve("overview", top_k=2, min_score=0.5)
    files = [r["metadata"]["file_path"] for r in results]
    assert len(results) == 2
    assert len(set(files)) == 2
    assert "A.java" in files
    assert "B.java" in files


def test_retrieve_filters_low_scores():
    pipeline = RepoRAGPipeline.__new__(RepoRAGPipeline)
    pipeline.chunks_meta = [
        {
            "content": "class A",
            "metadata": {"file_path": "A.java", "type": "class", "name": "A"},
        },
    ]

    class FakeIndex:
        def search(self, embedding, fetch_k):
            import numpy as np

            return np.array([[0.1]]), np.array([[0]])

    pipeline.index = FakeIndex()
    pipeline._encode = lambda texts: [[0.0]]  # type: ignore[method-assign]

    results = pipeline.retrieve("unrelated", top_k=3, min_score=0.35)
    assert results == []


def test_retrieve_overview_injects_readme():
    pipeline = RepoRAGPipeline.__new__(RepoRAGPipeline)
    pipeline.chunks_meta = [
        {
            "content": "public class Main {}",
            "metadata": {"file_path": "Main.java", "type": "class", "name": "Main"},
        },
        {
            "content": "# MiniGit overview",
            "metadata": {"file_path": "README.md", "type": "doc", "name": "README.md"},
        },
    ]
    pipeline.index = object()
    pipeline.retrieve = lambda query, top_k=8, **kwargs: [  # type: ignore[method-assign]
        {
            "content": "public class Main {}",
            "metadata": {"file_path": "Main.java", "type": "class", "name": "Main"},
            "score": 0.62,
        }
    ]

    results = pipeline.retrieve_overview("repository overview", top_k=2)
    files = [result["metadata"]["file_path"] for result in results]
    assert "README.md" in files
    assert "Main.java" in files


def test_retrieve_overview_prefers_doc_and_summary_types():
    pipeline = RepoRAGPipeline.__new__(RepoRAGPipeline)
    ranked = RepoRAGPipeline._rank_by_preferred_types(
        [
            {
                "metadata": {"type": "class"},
                "score": 0.7,
            },
            {
                "metadata": {"type": "doc"},
                "score": 0.65,
            },
        ],
        frozenset({"doc", "summary"}),
    )
    assert ranked[0]["metadata"]["type"] == "doc"


def test_retrieve_filters_by_file_paths():
    pipeline = RepoRAGPipeline.__new__(RepoRAGPipeline)
    pipeline.chunks_meta = [
        {
            "content": "class A1",
            "metadata": {"file_path": "A.java", "type": "class", "name": "A1"},
        },
        {
            "content": "class A2",
            "metadata": {"file_path": "A.java", "type": "class", "name": "A2"},
        },
        {
            "content": "class B",
            "metadata": {"file_path": "B.java", "type": "class", "name": "B"},
        },
    ]

    scores = iter([0.9, 0.85, 0.8])
    indices = iter([0, 1, 2])

    class FakeIndex:
        def search(self, embedding, fetch_k):
            import numpy as np

            row_scores = [next(scores) for _ in range(min(fetch_k, 3))]
            row_indices = [next(indices) for _ in range(min(fetch_k, 3))]
            return np.array([row_scores]), np.array([row_indices])

    pipeline.index = FakeIndex()
    pipeline._encode = lambda texts: [[0.0]]  # type: ignore[method-assign]

    results = pipeline.retrieve(
        "methods in A",
        top_k=2,
        min_score=0.5,
        file_paths=["A.java"],
    )
    assert len(results) == 2
    assert all(r["metadata"]["file_path"] == "A.java" for r in results)


def test_score_margin_drops_trailing_weak_chunks():
    pipeline = _fake_pipeline(
        [_chunk("README.md", "doc"), _chunk("broken.py"), _chunk("calc.py")],
        [0.80, 0.60, 0.58],
    )
    results = pipeline.retrieve("overview of readme", top_k=5, score_margin=0.08)
    assert [r["metadata"]["file_path"] for r in results] == ["README.md"]


def test_score_margin_keeps_close_peers():
    pipeline = _fake_pipeline(
        [_chunk("Commit.java"), _chunk("CommitCommand.java"), _chunk("Unrelated.java")],
        [0.80, 0.75, 0.40],
    )
    results = pipeline.retrieve("how does commit work", top_k=5, score_margin=0.08)
    files = [r["metadata"]["file_path"] for r in results]
    assert files == ["Commit.java", "CommitCommand.java"]


def test_score_margin_defaults_to_no_gating():
    """Code Agent few-shot retrieval must keep its full candidate set."""
    pipeline = _fake_pipeline(
        [_chunk("A.java"), _chunk("B.java"), _chunk("C.java")],
        [0.80, 0.55, 0.50],
    )
    results = pipeline.retrieve("singleton pattern", top_k=3)
    assert len(results) == 3


def test_score_margin_uses_unboosted_scores():
    """A boost on the top hit must not raise the cutoff for its peers."""
    pipeline = _fake_pipeline(
        [_chunk("commit.java", name="Commit"), _chunk("CommitCommand.java")],
        [0.80, 0.75],
    )
    results = pipeline.retrieve(
        "how does commit work", top_k=5, score_margin=0.08, path_boost=True
    )
    files = [r["metadata"]["file_path"] for r in results]
    assert "CommitCommand.java" in files


def test_path_boost_promotes_matching_filename():
    boosted = RepoRAGPipeline._path_boost("overview of readme.md", "docs/README.md")
    unrelated = RepoRAGPipeline._path_boost("overview of readme.md", "src/calc.py")
    assert boosted > unrelated
    assert unrelated == 0.0


def test_resolve_index_paths_matches_basename():
    pipeline = RepoRAGPipeline.__new__(RepoRAGPipeline)
    pipeline.chunks_meta = [
        _chunk("mini-git/README.md", "doc"),
        _chunk("mini-git/src/Main.java"),
    ]
    assert pipeline.resolve_index_paths(["readme.md"]) == ["mini-git/README.md"]
    assert pipeline.resolve_index_paths(["@Main.java"]) == ["mini-git/src/Main.java"]
    assert pipeline.resolve_index_paths(["missing.md"]) == []


def test_retrieve_overview_skips_readme_injection_when_file_scoped():
    pipeline = RepoRAGPipeline.__new__(RepoRAGPipeline)
    pipeline.chunks_meta = [
        _chunk("README.md", "doc"),
        _chunk("ROADMAP.md", "doc"),
    ]
    pipeline.index = object()
    pipeline.retrieve = lambda query, top_k=8, **kwargs: [  # type: ignore[method-assign]
        {**_chunk("ROADMAP.md", "doc"), "score": 0.7}
    ]

    results = pipeline.retrieve_overview(
        "summarize roadmap", top_k=3, file_paths=["ROADMAP.md"]
    )
    assert [r["metadata"]["file_path"] for r in results] == ["ROADMAP.md"]


def test_load_index_rejects_dimension_mismatch(tmp_path, capsys):
    pipeline = RepoRAGPipeline.__new__(RepoRAGPipeline)
    pipeline.index_dir = tmp_path
    pipeline.model_id = "test-embedder"
    pipeline.embed_dim = 384
    pipeline.chunks_meta = []
    pipeline.index = None
    pipeline.stale_index = False

    meta_path = tmp_path / "metadata.json"
    meta_path.write_text(json.dumps([_chunk("A.java")]), encoding="utf-8")

    stale = mock.Mock()
    stale.d = 151936
    with mock.patch("faiss.read_index", return_value=stale):
        pipeline._load_index(tmp_path / "faiss.index", meta_path)

    assert pipeline.stale_index is True
    assert pipeline.index is None
    assert pipeline.retrieve("anything", top_k=3) == []
    assert "Rebuild it with" in capsys.readouterr().out


def test_get_repo_rag_pipeline_caches_until_index_changes(tmp_path):
    clear_repo_rag_cache()
    index_dir = tmp_path / "index"
    index_dir.mkdir()

    with mock.patch(
        "inference.repo_rag_pipeline._index_fingerprint",
        return_value=(str(index_dir), 100.0),
    ), mock.patch("inference.repo_rag_pipeline.RepoRAGPipeline") as factory:
        factory.side_effect = lambda repo_root: mock.Mock(name=repo_root)
        first = get_repo_rag_pipeline(str(tmp_path))
        second = get_repo_rag_pipeline(str(tmp_path))
        assert first is second
        assert factory.call_count == 1

    with mock.patch(
        "inference.repo_rag_pipeline._index_fingerprint",
        return_value=(str(index_dir), 200.0),
    ), mock.patch("inference.repo_rag_pipeline.RepoRAGPipeline") as factory:
        factory.side_effect = lambda repo_root: mock.Mock(name=repo_root)
        third = get_repo_rag_pipeline(str(tmp_path))
        assert third is not first

    clear_repo_rag_cache()
