"""Completion-only loss helpers for TRL SFT training."""

from __future__ import annotations

import logging
from typing import Any

from src.training.tasks import get_task_spec

logger = logging.getLogger("codegen.training")


def get_response_template(task: str) -> str:
    """Return the response-template suffix marking the start of the target."""
    return get_task_spec(task).response_template


def prepare_prompt_completion_dataset(dataset: Any, task: str) -> Any:
    """Map SFT examples to TRL prompt/completion columns for completion-only loss."""
    template = get_response_template(task)

    def _map(example: dict[str, Any]) -> dict[str, str]:
        prompt = str(example.get("prompt", ""))
        completion = str(example.get("completion") or example.get("target", ""))
        if template not in prompt:
            logger.warning(
                "Response template %r missing from prompt for task %s (id=%s)",
                template,
                task,
                example.get("id", ""),
            )
        return {"prompt": prompt, "completion": completion}

    column_names = list(dataset.column_names)
    remove_cols = [name for name in column_names if name not in {"prompt", "completion"}]
    return dataset.map(_map, remove_columns=remove_cols)


def build_data_collator(
    tokenizer: Any,
    *,
    max_length: int | None = None,
    completion_only_loss: bool = True,
) -> Any:
    """Build TRL's language-modeling collator for pre-tokenized SFT batches."""
    from trl.trainer.sft_trainer import DataCollatorForLanguageModeling

    pad_token = tokenizer.pad_token or tokenizer.eos_token
    if pad_token not in tokenizer.get_vocab():
        raise ValueError(
            f"Tokenizer pad token '{pad_token}' is not in the vocabulary."
        )
    tokenizer.pad_token = pad_token

    return DataCollatorForLanguageModeling(
        pad_token_id=tokenizer.pad_token_id,
        max_length=max_length,
        truncation_mode="keep_start",
        completion_only_loss=completion_only_loss,
    )
