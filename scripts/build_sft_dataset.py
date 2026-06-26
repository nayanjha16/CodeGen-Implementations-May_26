#!/usr/bin/env python3
"""Smoke-check SFT dataset builder across spider + bird train splits."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.training.tasks import TRAINING_TASKS
from src.training.tend_dataset import build_sft_dataset, load_tend_training_rows


def main() -> int:
    rows = load_tend_training_rows()
    print(f"Combined train rows (spider + bird): {len(rows)}")

    for task in sorted(TRAINING_TASKS):
        result = build_sft_dataset(rows=rows, task=task, max_samples=50)
        print(
            f"  {task}: kept={result.row_count} "
            f"filter={result.filter_stats} "
            f"tokens={result.token_stats}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
