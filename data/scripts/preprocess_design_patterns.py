#!/usr/bin/env python3
"""Preprocess design_patterns_solid manifests into HF datasets for Java→Python SFT."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from datasets import Dataset

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from prompt_templates import format_java2py

RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "design_patterns_solid"
OUT_ROOT = PROJECT_ROOT / "data" / "processed" / "java2py_patterns"


def load_manifest(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def records_from_manifest(raw_root: Path, manifest_path: Path) -> list[dict]:
    out: list[dict] = []
    for row in load_manifest(manifest_path):
        java = (raw_root / row["java_path"]).read_text(encoding="utf-8").strip()
        python = (raw_root / row["python_path"]).read_text(encoding="utf-8").strip()
        if not java or not python:
            continue
        out.append(
            {
                "text": format_java2py(java, python),
                "java_code": java,
                "python_code": python,
                "id": row["id"],
                "pattern_or_principle": row["pattern_or_principle"],
                "pattern_id": row.get("pattern_id", ""),
                "kind": row["kind"],
                "domain": row["domain"],
                "tier": row.get("tier", ""),
                "category": row.get("category", ""),
                "source": "design_patterns_solid",
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess design patterns + SOLID to HF datasets")
    parser.add_argument("--raw-root", type=str, default=str(RAW_ROOT))
    parser.add_argument("--output-dir", type=str, default=str(OUT_ROOT))
    args = parser.parse_args()

    raw_root = Path(args.raw_root)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    train_rows = records_from_manifest(raw_root, raw_root / "manifest_train.jsonl")
    test_rows = records_from_manifest(raw_root, raw_root / "manifest_test.jsonl")

    def to_ds(rows: list[dict]) -> Dataset:
        if not rows:
            raise SystemExit("No rows to write")
        keys = rows[0].keys()
        return Dataset.from_dict({k: [r[k] for r in rows] for k in keys})

    train_ds = to_ds(train_rows)
    test_ds = to_ds(test_rows)
    train_ds.save_to_disk(str(out_dir / "train"))
    test_ds.save_to_disk(str(out_dir / "test"))
    # Also expose as val alias for trainers that expect val/
    test_ds.save_to_disk(str(out_dir / "val"))

    print(f"Saved train={len(train_ds)} test/val={len(test_ds)} -> {out_dir}")
    print("--- sample text (first 400 chars) ---")
    print(train_ds[0]["text"][:400])


if __name__ == "__main__":
    main()
