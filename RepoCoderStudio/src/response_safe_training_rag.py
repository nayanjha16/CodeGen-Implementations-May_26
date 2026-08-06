"""
============================================================
RepoCoder Studio
response_safe_training_rag.py  —  v1.1
============================================================

Response-safe token budgeting for a RAG-augmented training dataset.

New module. Does not modify anything under src/.

Why this exists
----------------
The original corrected full run notebook applies a response-safe
budgeting pass to the training dataset before calling SFTTrainer: since
SFTTrainer truncates every row to models.max_seq_length (1024 tokens),
and MultiHeaderCompletionCollator (completion_collator.py) raises a hard
ValueError if truncation cuts into the row's response header, that
notebook rebuilds any row that would overflow by shortening only the
input text -- never the response -- and excludes a row outright if even
a minimal input can't fit alongside the complete response.

RAG-augmented rows (prompt_builder_rag.py's build_rag_training_text) are
meaningfully longer than plain rows -- they add an "### Evidence Policy"
paragraph and a "### Retrieved Context" block on top of the same task
contract every row already carries. task_builder_rag.py already keeps
retrieved context to a smaller training-time budget
(context_char_budget=2000 chars, vs. inference's 7000) to reduce the odds
of overflow, but 1024 tokens is tight enough that this safety net is
still needed, not optional: without it, a single overlong RAG row can
crash the entire training run when the collator can't find the response
header.

apply_response_safe_budgeting() below is the original notebook's
algorithm (preserve the complete response, truncate only the input,
exclude a row if it still doesn't fit), extended to rebuild a row with
RAGPromptBuilder.build_rag_training_text() instead of
PromptBuilder.build_training_text() when that row is RAG-augmented. Rows
are matched to their (rag_augmented, retrieved_context) origin by
prompt_hash, the one field in the tokenized dataset that is unique per
rendered example -- corpus_id/task_id alone are not, since one approved
row now produces both a plain and a RAG-augmented TaskExample sharing
the same corpus_id and task_id.
"""

from __future__ import annotations

import gc
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.completion_collator import last_subsequence_end
from src.config import CONFIG, AppConfig
from src.prompt_builder import PromptBuilder, TASK_PROMPT_PROFILES
from src.prompt_builder_rag import RAGPromptBuilder
from src.schemas import TaskExample

RESPONSE_SAFE_BUDGETING_RAG_VERSION = "response_safe_training_rag_v1.1"

TOKEN_SAFETY_MARGIN = 4
MINIMUM_INPUT_TOKENS = 16


def _context_lookup(task_examples: List[TaskExample]) -> Dict[str, Tuple[bool, str]]:
    lookup: Dict[str, Tuple[bool, str]] = {}
    for ex in task_examples:
        metadata = ex.metadata or {}
        prompt_hash = metadata.get("prompt_hash")
        if not prompt_hash:
            continue
        lookup[prompt_hash] = (
            bool(metadata.get("rag_augmented")),
            str(metadata.get("retrieved_context", "")),
        )
    return lookup


def apply_response_safe_budgeting(
    train_dataset,
    task_examples: List[TaskExample],
    config: AppConfig = CONFIG,
    report_path: str = "outputs/reports/training_sequence_budget_report_rag_augmented.json",
):
    """Rebuilds any training row that would overflow max_seq_length by
    truncating only its input text, choosing the RAG or plain prompt
    template per row, and excludes rows whose complete response still
    doesn't fit. Returns (budgeted_train_dataset, budget_report).

    Mirrors the original corrected full run notebook's budgeting cell,
    extended for RAG-augmented rows. Applies to the train split only,
    matching the original (validation/test are never used for
    completion-masked loss).
    """

    import torch
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        config.models.student_model_name, trust_remote_code=True
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    plain_prompt_builder = PromptBuilder()
    rag_prompt_builder = RAGPromptBuilder()
    context_lookup = _context_lookup(task_examples)

    max_sequence_length = int(config.models.max_seq_length)

    configured_headers = {
        profile["response_header"] for profile in TASK_PROMPT_PROFILES.values()
    }
    marker_token_ids: List[List[int]] = []
    for header in configured_headers:
        for marker_text in (f"{header}\n", f"\n{header}\n"):
            token_ids = tokenizer.encode(marker_text, add_special_tokens=False)
            if token_ids and token_ids not in marker_token_ids:
                marker_token_ids.append(token_ids)
    assert marker_token_ids, "No response-header token patterns were created."

    def token_ids_for_text(text: str) -> List[int]:
        return tokenizer(str(text), add_special_tokens=True, truncation=False)["input_ids"]

    def response_marker_end(input_ids: List[int]):
        found_end = None
        for marker in marker_token_ids:
            candidate = last_subsequence_end(input_ids, marker)
            if candidate is not None:
                found_end = max(found_end or 0, candidate)
        return found_end

    def decode_prefix(token_ids: List[int], number_to_keep: int) -> str:
        return tokenizer.decode(
            token_ids[:number_to_keep], skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

    def render(task_id: str, instruction: str, input_text: str, output_text: str,
               rag_augmented: bool, retrieved_context: str) -> str:
        if rag_augmented and retrieved_context.strip():
            return rag_prompt_builder.build_rag_training_text(
                instruction, input_text, retrieved_context, output_text, task_id=task_id,
            )
        return plain_prompt_builder.build_training_text(
            instruction, input_text, output_text, task_id=task_id,
        )

    def build_response_safe_row(row: Dict[str, Any]) -> Dict[str, Any]:
        task_id = str(row.get("task_id", "")).strip()
        instruction = str(row.get("instruction", "") or "")
        original_input = str(row.get("input_text", "") or "")
        output_text = str(row.get("output_text", "") or "")
        rag_augmented, retrieved_context = context_lookup.get(
            row.get("prompt_hash"), (False, "")
        )

        # Hugging Face Dataset.map() requires every newly-created column to
        # exist for every returned row, including early-exit rows.  Keep the
        # schema stable and capture the RAG/plain origin before prompt_hash is
        # replaced on the successful (possibly input-truncated) path.
        result: Dict[str, Any] = {
            "training_budget_keep": False,
            "training_budget_status": "unknown",
            "training_sequence_tokens": 0,
            "training_rag_augmented": bool(rag_augmented),
        }

        if task_id not in TASK_PROMPT_PROFILES:
            result["training_budget_status"] = "unknown_task"
            return result
        if not original_input.strip():
            result["training_budget_status"] = "empty_input"
            return result
        if not output_text.strip():
            result["training_budget_status"] = "empty_output"
            return result

        original_input_ids = tokenizer.encode(original_input, add_special_tokens=False)

        fixed_text = render(task_id, instruction, "", output_text, rag_augmented, retrieved_context)
        fixed_length = len(token_ids_for_text(fixed_text))
        available_input_tokens = max_sequence_length - fixed_length - TOKEN_SAFETY_MARGIN
        minimum_required = min(MINIMUM_INPUT_TOKENS, len(original_input_ids))

        if available_input_tokens < minimum_required:
            result["training_budget_status"] = "excluded_complete_response_too_long"
            return result

        retained_count = min(len(original_input_ids), available_input_tokens)
        retained_input = decode_prefix(original_input_ids, retained_count)
        candidate_text = render(task_id, instruction, retained_input, output_text, rag_augmented, retrieved_context)
        candidate_ids = token_ids_for_text(candidate_text)

        while len(candidate_ids) > max_sequence_length and retained_count > minimum_required:
            overflow = len(candidate_ids) - max_sequence_length
            retained_count = max(minimum_required, retained_count - overflow - 2)
            retained_input = decode_prefix(original_input_ids, retained_count)
            candidate_text = render(task_id, instruction, retained_input, output_text, rag_augmented, retrieved_context)
            candidate_ids = token_ids_for_text(candidate_text)

        if len(candidate_ids) > max_sequence_length:
            result["training_budget_status"] = "excluded_could_not_fit_sequence"
            return result

        marker_end = response_marker_end(candidate_ids)
        if marker_end is None:
            result["training_budget_status"] = "excluded_response_header_not_tokenized"
            return result
        if marker_end >= len(candidate_ids):
            result["training_budget_status"] = "excluded_no_completion_tokens"
            return result

        result.update({
            "text": candidate_text,
            "prompt_hash": hashlib.sha256(candidate_text.encode("utf-8")).hexdigest(),
            "training_budget_keep": True,
            "training_budget_status": (
                "input_truncated" if retained_count < len(original_input_ids) else "unchanged"
            ),
            "training_sequence_tokens": len(candidate_ids),
        })
        return result

    original_rows = len(train_dataset)
    original_task_counts = Counter(train_dataset["task_id"])
    original_rag_counts = Counter(
        "rag_augmented" if context_lookup.get(h, (False, ""))[0] else "plain"
        for h in train_dataset["prompt_hash"]
    )

    budgeted = train_dataset.map(build_response_safe_row, desc="Applying response-safe token budgeting (RAG-aware)")
    status_counts = Counter(budgeted["training_budget_status"])
    train_dataset = budgeted.filter(
        lambda row: bool(row["training_budget_keep"]), desc="Keeping completion-safe training rows"
    )

    retained_rows = len(train_dataset)
    excluded_rows = original_rows - retained_rows
    assert retained_rows > 0, "Response-safe preprocessing excluded every training row."

    missing_tasks = sorted(set(original_task_counts) - set(Counter(train_dataset["task_id"])))
    assert not missing_tasks, f"Response-safe preprocessing removed all rows for tasks: {missing_tasks}"

    maximum_retained_length = max(train_dataset["training_sequence_tokens"])
    assert maximum_retained_length <= max_sequence_length

    marker_failures = []
    for row_index, text in enumerate(train_dataset["text"]):
        input_ids = tokenizer(text, add_special_tokens=True, truncation=True, max_length=max_sequence_length)["input_ids"]
        marker_end = response_marker_end(input_ids)
        if marker_end is None or marker_end >= len(input_ids):
            marker_failures.append(row_index)
    assert not marker_failures, f"Completion-header preflight failed for retained rows: {marker_failures[:20]}"

    retained_rag_counts = Counter(
        "rag_augmented" if flag else "plain"
        for flag in train_dataset["training_rag_augmented"]
    )

    budget_report = {
        "response_safe_budgeting_rag_version": RESPONSE_SAFE_BUDGETING_RAG_VERSION,
        "policy": "preserve_complete_response_truncate_input_only",
        "max_sequence_length": max_sequence_length,
        "original_rows": original_rows,
        "retained_rows": retained_rows,
        "excluded_rows": excluded_rows,
        "retention_rate": retained_rows / original_rows if original_rows else 0.0,
        "status_counts": dict(sorted(status_counts.items())),
        "original_task_counts": dict(sorted(original_task_counts.items())),
        "retained_task_counts": dict(sorted(Counter(train_dataset["task_id"]).items())),
        "original_rag_vs_plain_counts": dict(sorted(original_rag_counts.items())),
        "retained_rag_vs_plain_counts": dict(sorted(retained_rag_counts.items())),
        "maximum_retained_sequence_tokens": maximum_retained_length,
        "response_header_preflight_failures": len(marker_failures),
    }

    reports_dir = config.storage.project_root() / config.storage.reports_dir
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / Path(report_path).name).write_text(
        json.dumps(budget_report, indent=2), encoding="utf-8"
    )

    del tokenizer
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return train_dataset, budget_report
