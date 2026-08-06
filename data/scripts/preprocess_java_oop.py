#!/usr/bin/env python3
"""Build a combined Java→Python SFT set: AVATAR-TC + ClassEval-T + design_patterns_solid.

Output: data/processed/java2py_combined/{train,val}
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

from datasets import Dataset

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from preprocess_avatar_tc import load_split, subsample
from preprocess_java2py import load_codocbench
from prompt_templates import format_java2py

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SEED = 42


def _strip_leading_docstring_stub(python_src: str) -> str:
    """ClassEval Python files often start with a triple-quoted stub; keep the impl."""
    text = python_src.strip()
    if not (text.startswith('"""') or text.startswith("'''")):
        return text
    quote = text[:3]
    end = text.find(quote, 3)
    if end == -1:
        return text
    rest = text[end + 3 :].lstrip("\n")
    return rest if rest.strip() else text


def load_classeval_pairs(
    raw_dir: Path | None = None,
    holdout_ids: set[str] | None = None,
) -> tuple[list[dict], list[dict]]:
    """Load ClassEval-T Java/Python pairs. Returns (train, holdout)."""
    root = (raw_dir or RAW_DIR) / "classeval_t" / "ClassEval_T"
    java_dir = root / "java" / "solutuon"
    py_dir = root / "py" / "solution"
    if not java_dir.exists() or not py_dir.exists():
        print(f"  [ClassEval-T] not found under {root}")
        return [], []

    java_files = sorted(java_dir.glob("*.java"))
    holdout_ids = holdout_ids or set()
    # Default holdout: first 10 stems alphabetically for stable eval
    if not holdout_ids:
        stems = [p.stem for p in java_files]
        holdout_ids = set(stems[:10])

    train: list[dict] = []
    holdout: list[dict] = []
    for jf in java_files:
        pf = py_dir / f"{jf.stem}.py"
        if not pf.exists():
            continue
        java = jf.read_text(encoding="utf-8", errors="replace").strip()
        python = _strip_leading_docstring_stub(
            pf.read_text(encoding="utf-8", errors="replace")
        )
        if not java or not python:
            continue
        rec = {
            "java_code": java,
            "python_code": python,
            "source": "classeval_t",
            "id": jf.stem,
        }
        (holdout if jf.stem in holdout_ids else train).append(rec)

    print(f"  [ClassEval-T] train={len(train)} holdout={len(holdout)}")
    return train, holdout


def load_design_patterns_pairs(
    raw_dir: Path | None = None,
    split: str = "train",
) -> list[dict]:
    """Load design_patterns_solid from manifest_{split}.jsonl."""
    root = (raw_dir or RAW_DIR) / "design_patterns_solid"
    manifest = root / f"manifest_{split}.jsonl"
    if not manifest.exists():
        print(f"  [design_patterns_solid] missing {manifest}")
        return []

    records: list[dict] = []
    with manifest.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            java = (root / row["java_path"]).read_text(encoding="utf-8").strip()
            python = (root / row["python_path"]).read_text(encoding="utf-8").strip()
            if not java or not python:
                continue
            records.append(
                {
                    "java_code": java,
                    "python_code": python,
                    "source": "design_patterns_solid",
                    "id": row["id"],
                    "pattern_or_principle": row.get("pattern_or_principle", ""),
                    "kind": row.get("kind", ""),
                    "domain": row.get("domain", ""),
                }
            )
    print(f"  [design_patterns_solid/{split}] loaded {len(records)} samples")
    return records


def load_avatar_full(train_fraction: float = 1.0, max_samples: int | None = None) -> list[dict]:
    """AVATAR-TC train split (detokenized), optionally subsampled."""
    records = load_split("train")
    for r in records:
        r["source"] = "avatar_tc"
    if max_samples is not None or train_fraction < 1.0:
        records = subsample(records, train_fraction, max_samples)
    print(f"  [AVATAR-TC] loaded {len(records)} samples (fraction={train_fraction})")
    return records


def to_sft_records(pairs: list[dict], task: str = "java2py") -> list[dict]:
    out = []
    for r in pairs:
        out.append(
            {
                "text": format_java2py(r["java_code"], r["python_code"]),
                "task": task,
                "source": r.get("source", "unknown"),
                "java_code": r["java_code"],
                "python_code": r["python_code"],
            }
        )
    return out


def build_combined(
    *,
    avatar_fraction: float = 1.0,
    max_avatar: int | None = None,
    include_classeval: bool = True,
    include_design_patterns: bool = True,
    include_codocbench: bool = True,
    design_upsample: int = 1,
) -> tuple[list[dict], list[dict]]:
    """Return (train_pairs, val_pairs) with java_code/python_code/source."""
    train_pairs: list[dict] = []
    val_pairs: list[dict] = []

    train_pairs.extend(load_avatar_full(avatar_fraction, max_avatar))
    try:
        val_avatar = load_split("valid")
        for r in val_avatar:
            r["source"] = "avatar_tc"
        val_pairs.extend(val_avatar)
        print(f"  [AVATAR-TC valid] {len(val_avatar)} samples")
    except FileNotFoundError:
        pass

    if include_classeval:
        ce_train, ce_hold = load_classeval_pairs()
        train_pairs.extend(ce_train)
        val_pairs.extend(ce_hold)

    if include_design_patterns:
        dp_train = load_design_patterns_pairs(split="train")
        if design_upsample > 1:
            dp_train = dp_train * design_upsample
            print(f"  [design_patterns] upsampled x{design_upsample} -> {len(dp_train)}")
        train_pairs.extend(dp_train)
        val_pairs.extend(load_design_patterns_pairs(split="test"))

    if include_codocbench:
        codoc = load_codocbench(RAW_DIR)
        # 90/10 split for CoDocBench if present
        rng = random.Random(SEED)
        shuffled = codoc[:]
        rng.shuffle(shuffled)
        n = max(1, int(len(shuffled) * 0.9)) if shuffled else 0
        train_pairs.extend(shuffled[:n])
        val_pairs.extend(shuffled[n:])

    print(f"Combined Java2Py pairs: train={len(train_pairs)} val={len(val_pairs)}")
    return train_pairs, val_pairs


def save_combined(
    train_pairs: list[dict],
    val_pairs: list[dict],
    output_dir: Path | str | None = None,
) -> Path:
    out_dir = Path(output_dir or (PROCESSED_DIR / "java2py_combined"))
    out_dir.mkdir(parents=True, exist_ok=True)

    def to_ds(pairs: list[dict]) -> Dataset:
        return Dataset.from_dict(
            {
                "text": [format_java2py(r["java_code"], r["python_code"]) for r in pairs],
                "java_code": [r["java_code"] for r in pairs],
                "python_code": [r["python_code"] for r in pairs],
                "source": [r.get("source", "") for r in pairs],
            }
        )

    train_ds = to_ds(train_pairs)
    val_ds = to_ds(val_pairs if val_pairs else train_pairs[: max(1, len(train_pairs) // 20)])
    train_ds.save_to_disk(str(out_dir / "train"))
    val_ds.save_to_disk(str(out_dir / "val"))
    print(f"Saved train={len(train_ds)} val={len(val_ds)} -> {out_dir}")
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess combined Java2Py OOP datasets")
    parser.add_argument("--avatar-fraction", type=float, default=1.0)
    parser.add_argument("--max-avatar", type=int, default=None)
    parser.add_argument("--no-classeval", action="store_true")
    parser.add_argument("--no-design-patterns", action="store_true")
    parser.add_argument("--no-codocbench", action="store_true")
    parser.add_argument(
        "--design-upsample",
        type=int,
        default=1,
        help="Repeat design-pattern train rows to balance vs AVATAR (default 1).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(PROCESSED_DIR / "java2py_combined"),
    )
    args = parser.parse_args()

    train_pairs, val_pairs = build_combined(
        avatar_fraction=args.avatar_fraction,
        max_avatar=args.max_avatar,
        include_classeval=not args.no_classeval,
        include_design_patterns=not args.no_design_patterns,
        include_codocbench=not args.no_codocbench,
        design_upsample=args.design_upsample,
    )
    save_combined(train_pairs, val_pairs, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
