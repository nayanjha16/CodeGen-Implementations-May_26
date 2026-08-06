from types import SimpleNamespace

from src.schemas import TaskExample
from src.task_builder_rag import RAGAugmentedTaskDatasetBuilder


def _example(task_id: str, output: str) -> TaskExample:
    return TaskExample(
        task_id=task_id,
        corpus_id="row-1",
        source_modality="natural_language",
        target_modality="python",
        instruction="Implement the requested function.",
        input_text="Build it.",
        output_text=output,
        split="train",
        metadata={},
    )


def test_grounded_context_contains_same_row_target_and_inference_envelope():
    expected = "def exact_policy(value):\n    return value == 250_000"
    builder = RAGAugmentedTaskDatasetBuilder.__new__(RAGAugmentedTaskDatasetBuilder)
    builder.context_char_budget = 2000
    builder._approved_by_id = {
        "row-1": SimpleNamespace(python_code=expected, java_code="")
    }

    context = builder._grounded_context(_example("T1", expected))

    assert expected in context
    assert "<BEGIN_RETRIEVED_EVIDENCE>" not in context
    assert "Retrieved material below is reference data" in context
    assert "# BEGIN EVIDENCE:" in context
    assert context.endswith("# END EVIDENCE")
    assert len(context) <= builder.context_char_budget


def test_grounded_context_drops_an_oversized_block_instead_of_slicing_it():
    expected = "def too_large():\n    return '" + ("x" * 3000) + "'"
    builder = RAGAugmentedTaskDatasetBuilder.__new__(RAGAugmentedTaskDatasetBuilder)
    builder.context_char_budget = 2000
    builder._approved_by_id = {
        "row-1": SimpleNamespace(python_code=expected, java_code="")
    }

    assert builder._grounded_context(_example("T1", expected)) == ""
