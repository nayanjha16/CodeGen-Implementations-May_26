"""Tests for RAGAugmentedTask -- the adapter that lets any model tier's
generate_fn (in particular, the team's own fine-tuned checkpoint) be
retrieval-augmented and scored through the exact same Evaluator.evaluate_task
path as every other tier, so it lands in comparison_table.csv with full
exact_match / CodeBLEU / BERTScore metrics rather than only the CodeBLEU-only
side comparison in topk_experiment.run_four_tier_comparison.

This is the regression coverage for Checkpoint 4's requirement to "put
their model into the RAG system and evaluate" -- see also
test_topk_experiment.py::test_fine_tuned_generate_fn_is_used_not_small_lm_generate_fn
for the companion fix in run_four_tier_comparison.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from codegen_rag.evaluation.evaluator import Evaluator
from codegen_rag.rag.corpus_indexing import build_indexes_from_corpus
from codegen_rag.rag.pipeline import RAGPipeline
from codegen_rag.rag.rag_task_adapter import RAGAugmentedTask
from codegen_rag.tasks.documentation_generation import DocumentationGenerationTask
from codegen_rag.tasks.program_synthesis import ProgramSynthesisTask


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


@pytest.fixture
def rag_pipeline(small_corpus):
    dim = 16
    embed_fn = _fake_embed_fn(dim)
    dense_index, ast_index = build_indexes_from_corpus(
        small_corpus, embed_fn=lambda texts: np.stack([embed_fn(t) for t in texts]), embedding_dim=dim
    )
    return RAGPipeline(dense_index=dense_index, ast_index=ast_index, embed_fn=embed_fn, strategy="hybrid", top_k=3)


class _FakeModel:
    """Minimal stand-in satisfying BaseTask's constructor (it only needs a
    `.generate` attribute in practice, but we keep the same shape as
    conftest's FakeCodeGenModel for consistency)."""

    def generate(self, prompt: str, gen_config=None):  # noqa: ANN001
        return ["def add(a, b):\n    return a + b"]


def test_rag_augmented_task_preserves_task_name_and_reference_fields(rag_pipeline):
    base_task = ProgramSynthesisTask(model=_FakeModel())
    wrapped = RAGAugmentedTask(
        base_task=base_task,
        rag_pipeline=rag_pipeline,
        generate_fn=lambda prompt: "def add(a, b):\n    return a + b",
    )
    records = [{"intent": "add two numbers", "code": "def add(a, b):\n    return a + b"}]

    outputs = wrapped.run_batch(records)

    assert wrapped.task_name == "program_synthesis"
    assert outputs[0]["task"] == "program_synthesis"
    assert outputs[0]["prediction"] == "def add(a, b):\n    return a + b"
    # Reference field the Evaluator needs for program_synthesis is preserved.
    assert outputs[0]["code"] == "def add(a, b):\n    return a + b"
    assert outputs[0]["retrieval_strategy"] == "hybrid"
    assert outputs[0]["retrieved_k"] > 0


def test_rag_augmented_task_uses_the_supplied_generate_fn_not_the_base_task_model(rag_pipeline):
    """The whole point of the adapter: the fine-tuned model's generate_fn
    drives generation, not base_task.model.generate (which would silently
    make the "fine_tuned_rag" tier just run the placeholder base model)."""
    base_task = ProgramSynthesisTask(model=_FakeModel())  # would return "def add(a, b): return a + b"
    distinctive_output = "def totally_different_fine_tuned_output(): pass"
    wrapped = RAGAugmentedTask(
        base_task=base_task,
        rag_pipeline=rag_pipeline,
        generate_fn=lambda prompt: distinctive_output,
    )
    records = [{"intent": "add two numbers", "code": "def add(a, b):\n    return a + b"}]

    outputs = wrapped.run_batch(records)

    assert outputs[0]["prediction"] == distinctive_output


def test_rag_augmented_task_falls_back_to_task_prompt_as_query_without_duplication(rag_pipeline):
    """documentation_generation records have no "intent" field -- the query
    should fall back to the task's own build_prompt(), and task_instruction
    should be empty so the augmented prompt doesn't contain that text twice.
    """
    base_task = DocumentationGenerationTask(model=_FakeModel())
    wrapped = RAGAugmentedTask(
        base_task=base_task,
        rag_pipeline=rag_pipeline,
        generate_fn=lambda prompt: "Adds two numbers.",
    )
    record = {"code": "def add(a, b):\n    return a + b", "docstring": "Add two numbers and return the sum."}

    outputs = wrapped.run_batch([record])

    task_prompt = base_task.build_prompt(record)
    augmented_prompt = outputs[0]["prompt"]
    # The task prompt should appear in the augmented prompt exactly once,
    # not twice (once as "query", once as "task_instruction").
    assert augmented_prompt.count(task_prompt) == 1


def test_rag_augmented_task_scores_correctly_through_evaluator(tmp_path: Path, rag_pipeline):
    """End-to-end: Evaluator.evaluate_task() treats a RAGAugmentedTask
    exactly like a plain task and produces real CodeBLEU/BERTScore/exact_match
    metrics that flow into build_comparison_table() -- closing the gap where
    RAG-augmented tiers never reached comparison_table.csv."""
    base_task = ProgramSynthesisTask(model=_FakeModel())
    wrapped = RAGAugmentedTask(
        base_task=base_task,
        rag_pipeline=rag_pipeline,
        generate_fn=lambda prompt: "def add(a, b):\n    return a + b",
    )
    records = [
        {"intent": "add two numbers", "code": "def add(a, b):\n    return a + b"},
        {"intent": "subtract two numbers", "code": "def sub(a, b):\n    return a - b"},
    ]

    evaluator = Evaluator(results_dir=tmp_path / "results")
    summary = evaluator.evaluate_task(wrapped, records, model_tier="fine_tuned_rag")

    assert summary["task"] == "program_synthesis"
    assert summary["model_tier"] == "fine_tuned_rag"
    assert summary["n_examples"] == 2
    assert "codebleu" in summary["metrics"]
    assert "bertscore" in summary["metrics"]

    comparison_df = evaluator.build_comparison_table([summary])
    assert set(comparison_df["model_tier"]) == {"fine_tuned_rag"}
    assert (comparison_df["task"] == "program_synthesis").all()
