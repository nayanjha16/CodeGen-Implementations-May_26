"""Shared base class for all task modules.

Every task follows the same shape: build a prompt from a record, generate
with the underlying `CodeGenModel`, and post-process the raw completion into
a clean output string. Subclasses only need to implement ``build_prompt`` and
``postprocess``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from codegen_rag.models.generation_config import GenerationConfig
from codegen_rag.utils.logging_config import get_logger

if TYPE_CHECKING:
    # Only needed for type checkers (mypy). Importing `codegen_wrapper` at
    # runtime would pull in torch, which task modules should not require
    # just to be imported and unit-tested.
    from codegen_rag.models.codegen_wrapper import CodeGenModel

logger = get_logger(__name__)


class BaseTask(ABC):
    task_name: str = "base_task"

    def __init__(self, model: "CodeGenModel", gen_config: GenerationConfig | None = None):
        self.model = model
        self.gen_config = gen_config or GenerationConfig()

    @abstractmethod
    def build_prompt(self, record: dict[str, Any]) -> str:
        """Turn a raw record (e.g. {'code': ..., 'intent': ...}) into a prompt string."""

    def postprocess(self, raw_completion: str) -> str:
        """Default postprocessing: strip trailing whitespace/incomplete lines."""
        return raw_completion.strip()

    def run(self, record: dict[str, Any]) -> dict[str, Any]:
        """Generate a single output for one record, returning record + prediction."""
        prompt = self.build_prompt(record)
        completions = self.model.generate(prompt, self.gen_config)
        prediction = self.postprocess(completions[0]) if completions else ""
        return {**record, "prompt": prompt, "prediction": prediction, "task": self.task_name}

    def run_batch(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generate for a list of records, logging progress every 25 items."""
        results = []
        for i, record in enumerate(records):
            results.append(self.run(record))
            if (i + 1) % 25 == 0:
                logger.info("[%s] processed %d/%d", self.task_name, i + 1, len(records))
        return results
