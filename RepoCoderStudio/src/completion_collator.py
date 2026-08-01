"""Completion-only supervision for RepoCoderStudio's multi-task headers.

The six tasks intentionally use different response headers (for example
``### Python`` and ``### Java Translation``). TRL's standard completion-only
collator accepts one marker, so this small adapter supports all configured
headers while preserving normal causal-LM padding.
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Sequence


def last_subsequence_end(
    values: Sequence[int],
    pattern: Sequence[int],
) -> Optional[int]:
    """Return the exclusive end of the last exact pattern occurrence."""

    if not pattern or len(pattern) > len(values):
        return None
    last = None
    width = len(pattern)
    for start in range(len(values) - width + 1):
        if list(values[start : start + width]) == list(pattern):
            last = start + width
    return last


class MultiHeaderCompletionCollator:
    """Mask prompt tokens and compute loss only on the reference response."""

    def __init__(self, tokenizer, response_headers: Iterable[str]):
        from transformers import DataCollatorForLanguageModeling

        self.delegate = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
        )
        self.eos_token_id = tokenizer.eos_token_id
        self.marker_token_ids: List[List[int]] = []

        # Include a leading newline variant because tokenizers can merge line
        # breaks differently depending on the preceding prompt text.
        marker_texts = {
            variant
            for header in response_headers
            for variant in (
                f"{header}\n",
                f"\n{header}\n",
            )
        }
        for marker in sorted(marker_texts):
            token_ids = tokenizer.encode(marker, add_special_tokens=False)
            if token_ids and token_ids not in self.marker_token_ids:
                self.marker_token_ids.append(token_ids)

        if not self.marker_token_ids:
            raise ValueError("At least one tokenizable response header is required.")

    def __call__(self, features):
        original_lengths = [len(feature["input_ids"]) for feature in features]
        batch = self.delegate(features)
        labels = batch["labels"]

        for row_index in range(labels.shape[0]):
            row = labels[row_index].tolist()
            marker_end = None
            for marker in self.marker_token_ids:
                candidate_end = last_subsequence_end(row, marker)
                if candidate_end is not None:
                    marker_end = max(marker_end or 0, candidate_end)

            if marker_end is None:
                raise ValueError(
                    "No configured response header was found in a training "
                    "example; refusing to train on prompt tokens."
                )

            labels[row_index, :marker_end] = -100

            # pad_token is intentionally aliased to eos_token for Qwen. TRL's
            # delegate therefore masks every EOS id as padding, including the
            # real final completion terminator. Restore only the final token
            # from the unpadded feature; right-padding tokens remain masked.
            final_index = original_lengths[row_index] - 1
            if (
                self.eos_token_id is not None
                and final_index >= marker_end
                and int(batch["input_ids"][row_index, final_index])
                == int(self.eos_token_id)
            ):
                labels[row_index, final_index] = int(self.eos_token_id)

        return batch
