"""Smoke test for Hugging Face TEND dataset integration."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.datasets.tend_loader import TENDLoader, load_gold_validation


def main() -> int:
    gold_rows = load_gold_validation()
    assert len(gold_rows) == 50, f"Expected 50 gold validation rows, got {len(gold_rows)}"
    print(f"OK gold validation: {len(gold_rows)} rows | id={gold_rows[0]['id']}")

    for config in ("spider", "bird"):
        loader = TENDLoader(config=config)
        for split in ("train", "test"):
            rows = loader.load_split(split)
            assert rows, f"Expected non-empty {config}/{split}"
            sample = rows[0]
            required = (
                "question",
                "schema",
                "sql",
                "nosql_schema",
                "nosql_query",
                "documentation",
            )
            missing = [field for field in required if not sample.get(field)]
            if missing:
                raise AssertionError(
                    f"{config}/{split} sample missing fields: {missing}"
                )
            print(
                f"OK {config}/{split}: {len(rows)} rows | "
                f"id={sample['id']} db_id={sample['db_id']}"
            )
    print("TEND Hugging Face integration test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
