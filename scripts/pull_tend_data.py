#!/usr/bin/env python3
"""Pull the latest TEND dataset splits from Hugging Face into the local cache."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.datasets.tend_loader import TEND_CONFIGS, TEND_SPLITS, TENDLoader
from src.utils.config import get_tend_dataset_id, load_config
from src.utils.logging import setup_logging


def pull_tend_data(
    *,
    configs: tuple[str, ...] = ("spider", "bird"),
    splits: tuple[str, ...] = ("train", "test"),
) -> dict[str, dict[str, int]]:
    """Force-refresh TEND splits from Hugging Face and return row counts."""
    dataset_id = get_tend_dataset_id()
    summary: dict[str, dict[str, int]] = {}

    for config in configs:
        loader = TENDLoader(dataset_id=dataset_id, config=config)
        summary[config] = {}
        for split in splits:
            rows = loader.refresh_split(split)
            summary[config][split] = len(rows)
            print(
                f"  {config}/{split}: {len(rows)} rows -> {loader._cache_path(split)}"
            )

    return summary


def main() -> int:
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Pull latest care2achieve/tend splits from Hugging Face"
    )
    parser.add_argument(
        "--config",
        action="append",
        choices=sorted(TEND_CONFIGS),
        help="TEND config to pull (default: spider and bird)",
    )
    parser.add_argument(
        "--split",
        action="append",
        choices=sorted(TEND_SPLITS),
        help="Split to pull (default: train and test)",
    )
    parser.add_argument(
        "--summary-out",
        default=None,
        help="Optional path to write a JSON summary of row counts",
    )
    args = parser.parse_args()

    configs = tuple(args.config) if args.config else tuple(sorted(TEND_CONFIGS))
    splits = tuple(args.split) if args.split else tuple(sorted(TEND_SPLITS))

    config = load_config()
    dataset_id = get_tend_dataset_id(config)
    cache_hint = TENDLoader(config=configs[0])._cache_dir().parent

    print(f"Dataset: {dataset_id}")
    print(f"Cache root: {cache_hint}")
    print(f"Pulling configs={configs} splits={splits} ...")

    summary = pull_tend_data(configs=configs, splits=splits)
    total = sum(count for split_counts in summary.values() for count in split_counts.values())
    print(f"Done. {total} rows cached across {len(configs)} config(s).")

    if args.summary_out:
        out_path = Path(args.summary_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "dataset_id": dataset_id,
            "configs": summary,
            "total_rows": total,
        }
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Summary written to {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
