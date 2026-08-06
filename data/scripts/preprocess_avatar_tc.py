#!/usr/bin/env python3
"""Preprocess AVATAR-TC Java->Python pairs into a HuggingFace Dataset for SFT.

The raw AVATAR-TC files are in CodeXGLUE delexicalized format (space-separated
tokens, NEW_LINE/INDENT/DEDENT structure tokens, in-string space markers). Both
sides are detokenized so the training `text` field matches exactly what the
baseline evaluation feeds the model at inference time (see
``evaluation/run_baseline_qwen.py`` and ``data/scripts/prompt_templates.py``).

By default only 1/4 of the train split is used (seeded shuffle for a
representative sample) to keep MPS training time manageable.
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from datasets import Dataset

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from detokenize import detokenize_java, detokenize_python
from prompt_templates import format_java2py

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "avatar_tc"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SEED = 42


def load_split(split: str) -> list[dict]:
    """Load and detokenize one AVATAR-TC split into Java/Python records."""
    java_path = RAW_DIR / f"{split}.java-python.java"
    py_path = RAW_DIR / f"{split}.java-python.python"

    with open(java_path) as fj, open(py_path) as fp:
        pairs = list(zip(fj, fp))

    records = []
    for j, p in pairs:
        java = detokenize_java(j.rstrip("\n")).strip()
        python = detokenize_python(p.rstrip("\n")).strip()
        if java and python:
            records.append({"java_code": java, "python_code": python})
    return records


def subsample(records: list[dict], fraction: float, max_samples: int | None) -> list[dict]:
    """Return a seeded random subset of records.

    ``max_samples`` (if given) takes precedence over ``fraction``.
    """
    rng = random.Random(SEED)
    shuffled = records[:]
    rng.shuffle(shuffled)

    if max_samples is not None:
        n = min(max_samples, len(shuffled))
    else:
        n = max(1, int(len(shuffled) * fraction))
    return shuffled[:n]


def to_dataset(records: list[dict]) -> Dataset:
    return Dataset.from_dict(
        {
            "text": [format_java2py(r["java_code"], r["python_code"]) for r in records],
            "java_code": [r["java_code"] for r in records],
            "python_code": [r["python_code"] for r in records],
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess AVATAR-TC for Java2Py SFT")
    parser.add_argument(
        "--train-fraction",
        type=float,
        default=0.25,
        help="Fraction of the train split to keep (default 0.25 = 1/4).",
    )
    parser.add_argument(
        "--max-train-samples",
        type=int,
        default=None,
        help="Exact cap on train samples (overrides --train-fraction).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(PROCESSED_DIR / "java2py_avatar"),
        help="Where to save the train/val HF datasets.",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Loading AVATAR-TC splits...")
    train_records = load_split("train")
    val_records = load_split("valid")
    print(f"  train (full): {len(train_records)} pairs")
    print(f"  valid:        {len(val_records)} pairs")

    train_records = subsample(train_records, args.train_fraction, args.max_train_samples)
    print(f"  train (used): {len(train_records)} pairs")

    train_ds = to_dataset(train_records)
    val_ds = to_dataset(val_records)

    train_ds.save_to_disk(str(out_dir / "train"))
    val_ds.save_to_disk(str(out_dir / "val"))
    print(f"\nSaved train ({len(train_ds)}) and val ({len(val_ds)}) to {out_dir}")
    print("\n--- Sample training text ---")
    print(train_ds[0]["text"][:500])


if __name__ == "__main__":
    main()
