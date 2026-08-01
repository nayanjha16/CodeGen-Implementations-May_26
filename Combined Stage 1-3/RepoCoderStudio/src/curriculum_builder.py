"""
============================================================
RepoCoder Studio
curriculum_builder.py  —  v2.5
============================================================

Deterministic curriculum and task balancing utilities.

The curriculum builder operates after TaskDatasetBuilder and before tokenizer
preparation. It does not change prompt text; it only orders and optionally caps
examples so the unified student does not see long task-specific runs that can
increase task interference.
"""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional

from src.config import CONFIG, AppConfig


class CurriculumBuilder:
    """Applies deterministic task-aware ordering and optional caps."""

    def __init__(self, config: AppConfig = CONFIG):
        self.config = config
        self.seed = getattr(config.runtime, "random_seed", 42)

    def cap_per_task(self, rows: List[Dict[str, Any]], cap_per_task: Optional[int] = None) -> List[Dict[str, Any]]:
        if cap_per_task is None:
            cap_per_task = getattr(self.config.training, "demo_task_cap_per_split", 10_000)
        if cap_per_task is None or cap_per_task <= 0:
            return rows
        grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[str(row.get("task_id", "unknown"))].append(row)
        capped: List[Dict[str, Any]] = []
        for task_id in sorted(grouped):
            capped.extend(grouped[task_id][:cap_per_task])
        return capped

    def round_robin_by_task(self, rows: List[Dict[str, Any]], shuffle_within_task: bool = True) -> List[Dict[str, Any]]:
        grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[str(row.get("task_id", "unknown"))].append(row)
        rng = random.Random(self.seed)
        task_ids = sorted(grouped)
        if shuffle_within_task:
            for task_id in task_ids:
                rng.shuffle(grouped[task_id])
        ordered: List[Dict[str, Any]] = []
        remaining = True
        idx = 0
        while remaining:
            remaining = False
            for task_id in task_ids:
                if idx < len(grouped[task_id]):
                    ordered.append(grouped[task_id][idx])
                    remaining = True
            idx += 1
        return ordered

    def apply(self, rows: List[Dict[str, Any]], split_name: str = "train") -> List[Dict[str, Any]]:
        selected = list(rows)
        if self.config.runtime.run_mode == "demo":
            selected = self.cap_per_task(selected)
        # Round-robin every split for predictable task distribution. This is most
        # important for train, but useful in evaluation/debugging too.
        return self.round_robin_by_task(selected, shuffle_within_task=(split_name == "train"))
