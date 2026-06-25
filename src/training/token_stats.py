"""Token statistics for SFT dataset construction."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("codegen.training")


@dataclass
class TokenStats:
    """Aggregate token counts for one dataset build."""

    rows: int = 0
    prompt_tokens: list[int] = field(default_factory=list)
    target_tokens: list[int] = field(default_factory=list)
    total_tokens: list[int] = field(default_factory=list)
    skipped_too_long_target: int = 0
    skipped_too_long_prompt: int = 0

    def record(
        self,
        *,
        prompt_tokens: int,
        target_tokens: int,
        total_tokens: int,
    ) -> None:
        self.rows += 1
        self.prompt_tokens.append(prompt_tokens)
        self.target_tokens.append(target_tokens)
        self.total_tokens.append(total_tokens)

    @staticmethod
    def _mean(values: list[int]) -> float:
        return sum(values) / len(values) if values else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows": self.rows,
            "avg_prompt_tokens": round(self._mean(self.prompt_tokens), 2),
            "avg_target_tokens": round(self._mean(self.target_tokens), 2),
            "avg_total_tokens": round(self._mean(self.total_tokens), 2),
            "max_total_tokens": max(self.total_tokens) if self.total_tokens else 0,
            "skipped_too_long_target": self.skipped_too_long_target,
            "skipped_too_long_prompt": self.skipped_too_long_prompt,
        }


def log_token_stats(task: str, stats: TokenStats) -> None:
    """Log token distribution summary for a built dataset."""
    summary = stats.to_dict()
    logger.info(
        "TEND token stats task=%s rows=%d avg_prompt=%.1f avg_target=%.1f "
        "avg_total=%.1f max_total=%d skipped_target=%d skipped_prompt=%d",
        task,
        summary["rows"],
        summary["avg_prompt_tokens"],
        summary["avg_target_tokens"],
        summary["avg_total_tokens"],
        summary["max_total_tokens"],
        summary["skipped_too_long_target"],
        summary["skipped_too_long_prompt"],
    )
