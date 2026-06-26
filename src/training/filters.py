"""Row filters for TEND SFT dataset construction."""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from src.training.tasks import TaskSpec, get_task_spec

logger = logging.getLogger("codegen.training")


@dataclass
class FilterStats:
    """Counts of rows kept or skipped while building an SFT dataset."""

    input_rows: int = 0
    kept_rows: int = 0
    skipped: Counter[str] = field(default_factory=Counter)

    def record_skip(self, reason: str) -> None:
        self.skipped[reason] += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_rows": self.input_rows,
            "kept_rows": self.kept_rows,
            "skipped_rows": sum(self.skipped.values()),
            "skip_reasons": dict(self.skipped),
        }


def _is_nonempty(value: Any) -> bool:
    return bool(str(value or "").strip())


def row_has_required_fields(row: dict[str, Any], spec: TaskSpec) -> bool:
    """Return True when all required columns for a task are present and non-empty."""
    return all(_is_nonempty(row.get(field_name)) for field_name in spec.required_fields)


def filter_tend_rows(
    rows: list[dict[str, Any]],
    task: str,
    *,
    stats: FilterStats | None = None,
) -> list[dict[str, Any]]:
    """Keep rows with complete supervision fields for the requested task."""
    spec = get_task_spec(task)
    filter_stats = stats or FilterStats()
    filter_stats.input_rows += len(rows)

    kept: list[dict[str, Any]] = []
    for row in rows:
        if not row_has_required_fields(row, spec):
            filter_stats.record_skip("missing_required_fields")
            continue
        kept.append(row)

    filter_stats.kept_rows += len(kept)
    return kept


def log_filter_stats(task: str, stats: FilterStats) -> None:
    """Log dataset filter summary."""
    summary = stats.to_dict()
    logger.info(
        "TEND filter task=%s input=%d kept=%d skipped=%d reasons=%s",
        task,
        summary["input_rows"],
        summary["kept_rows"],
        summary["skipped_rows"],
        summary["skip_reasons"],
    )
