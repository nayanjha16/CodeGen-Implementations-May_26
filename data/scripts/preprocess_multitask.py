#!/usr/bin/env python3
"""Build a combined multi-task SFT dataset for Qwen fine-tuning.

Java2Py: full AVATAR-TC + ClassEval-T + design_patterns_solid + CoDocBench
NL2Py:   MBPP only (Spider / BirdBench SQL proxies are excluded)
Code2Doc: DocuMint
Optional: code comments

Output: data/processed/qwen_multitask/{train,val}
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

from prompt_templates import (
    format_code2doc,
    format_comment,
    format_java2py,
    format_nl2py,
)
from preprocess_java_oop import build_combined, to_sft_records
from preprocess_nl2py import load_mbpp

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SEED = 42


def _strip_comments_and_docstrings(code: str) -> str:
    """Remove # line comments and triple-quoted docstrings."""
    lines: list[str] = []
    in_docstring = False
    doc_quote = ""

    for line in code.split("\n"):
        stripped = line.strip()
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                doc_quote = stripped[:3]
                rest = stripped[3:]
                if rest.endswith(doc_quote) and len(rest) > 3:
                    continue
                in_docstring = True
                continue
            if "#" in line:
                line = line[: line.index("#")].rstrip()
            if line.strip():
                lines.append(line)
        else:
            if doc_quote in stripped:
                in_docstring = False
            continue

    return "\n".join(lines).strip()


def _has_comments_or_docstring(code: str) -> bool:
    stripped = _strip_comments_and_docstrings(code)
    return stripped != code.strip() and len(stripped) >= 20


def load_java2py_all(
    *,
    avatar_fraction: float = 1.0,
    max_avatar: int | None = None,
    include_classeval: bool = True,
    include_design_patterns: bool = True,
    include_codocbench: bool = True,
    design_upsample: int = 1,
    include_val_in_train_pool: bool = False,
) -> list[dict]:
    """All Java→Python SFT rows for the multitask mix (train pool only by default)."""
    train_pairs, val_pairs = build_combined(
        avatar_fraction=avatar_fraction,
        max_avatar=max_avatar,
        include_classeval=include_classeval,
        include_design_patterns=include_design_patterns,
        include_codocbench=include_codocbench,
        design_upsample=design_upsample,
    )
    pairs = train_pairs
    if include_val_in_train_pool:
        # Not recommended; kept for ablation only
        pairs = train_pairs + val_pairs
    records = to_sft_records(pairs, task="java2py")
    print(f"  [Java2Py total] {len(records)} samples")
    return records


def load_nl2py_records(
    raw_dir: Path | None = None,
    max_mbpp: int | None = None,
    skip_hf: bool = False,
) -> list[dict]:
    """MBPP-only NL2Py (no Spider/Bird SQL proxies)."""
    del raw_dir  # unused; kept for call-site compatibility
    records: list[dict] = []
    if skip_hf:
        print("  [NL2Py] skipped (--skip-hf); MBPP requires Hugging Face")
        return records

    for r in load_mbpp(max_samples=max_mbpp):
        records.append({
            "text": format_nl2py(r["nl_query"], r["python_code"]),
            "task": "nl2py",
            "source": r["source"],
        })

    print(f"  [NL2Py total] {len(records)} samples (MBPP only)")
    return records


def load_code2doc_records(max_documint: int = 5000, skip_hf: bool = False) -> list[dict]:
    """DocuMint with fallback to kaanrkaraman/code2doc (Python only)."""
    records: list[dict] = []
    if skip_hf:
        print("  [Code2Doc] skipped (--skip-hf)")
        return records

    try:
        from datasets import load_dataset

        ds = load_dataset("documint/DocuMint", split="train", streaming=True)
        count = 0
        for item in ds:
            if count >= max_documint:
                break
            code = (item.get("instruction") or item.get("function_code") or "").strip()
            doc = (item.get("response") or item.get("documentation") or "").strip()
            if code and doc and len(code) >= 20:
                records.append({
                    "text": format_code2doc(code, doc),
                    "task": "code2doc",
                    "source": "documint",
                })
                count += 1
        print(f"  [DocuMint] loaded {len(records)} samples")
    except Exception as e:
        print(f"  [DocuMint] failed ({e}), trying code2doc fallback")

    if records:
        return records

    try:
        from datasets import load_dataset

        ds = load_dataset("kaanrkaraman/code2doc", split="train")
        for item in ds:
            if item.get("language") != "python":
                continue
            code = (item.get("function_code") or "").strip()
            doc = (item.get("documentation") or "").strip()
            if code and doc:
                records.append({
                    "text": format_code2doc(code, doc),
                    "task": "code2doc",
                    "source": "code2doc",
                })
        print(f"  [code2doc fallback] loaded {len(records)} samples")
    except Exception as e:
        print(f"  [code2doc fallback] skipped ({e})")

    return records


def load_comment_records(max_samples: int = 3000, skip_hf: bool = False) -> list[dict]:
    """Synthetic comment pairs from CodeParrot Python (strip comments -> original)."""
    records: list[dict] = []
    if skip_hf or max_samples <= 0:
        print("  [Code comments] skipped")
        return records

    try:
        from datasets import load_dataset

        ds = load_dataset(
            "codeparrot/github-code",
            languages=["Python"],
            split="train",
            streaming=True,
            trust_remote_code=True,
        )
        count = 0
        for item in ds:
            if count >= max_samples:
                break
            code = item.get("code", "").strip()
            if not code or len(code) < 50 or not _has_comments_or_docstring(code):
                continue
            stripped = _strip_comments_and_docstrings(code)
            if not stripped or stripped == code or len(stripped) < 30:
                continue
            records.append({
                "text": format_comment(stripped, code),
                "task": "comments",
                "source": "codeparrot",
            })
            count += 1
    except Exception as e:
        print(f"  [Code comments] skipped ({e})")

    print(f"  [Code comments] loaded {len(records)} samples")
    return records


def _synthetic_fallback() -> list[dict]:
    """Minimal dataset when nothing else loads (tests / offline smoke)."""
    return [
        {
            "text": format_java2py("int x = 1;", "x = 1"),
            "task": "java2py",
            "source": "synthetic",
        },
        {
            "text": format_nl2py("add two numbers", "def add(a, b):\n    return a + b"),
            "task": "nl2py",
            "source": "synthetic",
        },
        {
            "text": format_code2doc(
                "def add(a, b):\n    return a + b",
                "Return the sum of a and b.",
            ),
            "task": "code2doc",
            "source": "synthetic",
        },
        {
            "text": format_comment(
                "def add(a, b):\n    return a + b",
                "def add(a, b):\n    # Return sum\n    return a + b",
            ),
            "task": "comments",
            "source": "synthetic",
        },
    ]


def build_dataset(
    records: list[dict],
    val_ratio: float = 0.1,
) -> tuple[Dataset, Dataset]:
    rng = random.Random(SEED)
    shuffled = records[:]
    rng.shuffle(shuffled)

    split_idx = max(1, int(len(shuffled) * (1 - val_ratio)))
    train_records = shuffled[:split_idx]
    val_records = shuffled[split_idx:] or shuffled[: max(1, len(shuffled) // 10)]

    def to_rows(recs: list[dict]) -> dict:
        return {
            "text": [r["text"] for r in recs],
            "task": [r["task"] for r in recs],
            "source": [r["source"] for r in recs],
        }

    return Dataset.from_dict(to_rows(train_records)), Dataset.from_dict(to_rows(val_records))


def collect_all_records(
    *,
    avatar_fraction: float = 1.0,
    max_avatar: int | None = None,
    include_classeval: bool = True,
    include_design_patterns: bool = True,
    include_codocbench: bool = True,
    design_upsample: int = 1,
    max_mbpp: int | None = None,
    max_documint: int = 5000,
    max_comments: int = 0,
    skip_hf: bool = False,
    # Backward-compat aliases used by older notebook/tests
    max_java2py_replay: int | None = None,
    train_fraction: float | None = None,
) -> list[dict]:
    """Load and merge all multi-task records."""
    if train_fraction is not None:
        avatar_fraction = train_fraction
    if max_java2py_replay is not None and max_avatar is None:
        # Legacy: "replay" cap → max_avatar
        max_avatar = max_java2py_replay
        if train_fraction is None and avatar_fraction == 1.0:
            # Old default was 0.25 when using replay API
            pass

    print("Loading multi-task datasets...")
    all_records: list[dict] = []
    all_records.extend(
        load_java2py_all(
            avatar_fraction=avatar_fraction,
            max_avatar=max_avatar,
            include_classeval=include_classeval,
            include_design_patterns=include_design_patterns,
            include_codocbench=include_codocbench,
            design_upsample=design_upsample,
        )
    )
    all_records.extend(load_nl2py_records(RAW_DIR, max_mbpp, skip_hf))
    all_records.extend(load_code2doc_records(max_documint, skip_hf))
    all_records.extend(load_comment_records(max_comments, skip_hf))

    if not all_records:
        print("WARNING: No records loaded. Using minimal synthetic dataset.")
        all_records = _synthetic_fallback()

    task_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}
    for r in all_records:
        task_counts[r["task"]] = task_counts.get(r["task"], 0) + 1
        source_counts[r["source"]] = source_counts.get(r["source"], 0) + 1
    print(f"Total records: {len(all_records)}")
    for task, n in sorted(task_counts.items()):
        print(f"  task/{task}: {n}")
    for src, n in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"  source/{src}: {n}")

    return all_records


def save_multitask_dataset(
    records: list[dict],
    output_dir: Path | str | None = None,
    val_ratio: float = 0.1,
) -> Path:
    """Split records into train/val and save to disk."""
    out_dir = Path(output_dir or (PROCESSED_DIR / "qwen_multitask"))
    out_dir.mkdir(parents=True, exist_ok=True)

    train_ds, val_ds = build_dataset(records, val_ratio=val_ratio)
    train_ds.save_to_disk(str(out_dir / "train"))
    val_ds.save_to_disk(str(out_dir / "val"))
    print(f"\nSaved train ({len(train_ds)}) and val ({len(val_ds)}) to {out_dir}")
    print("\n--- Sample training text ---")
    print(train_ds[0]["text"][:500])
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Preprocess multi-task Qwen SFT dataset")
    parser.add_argument(
        "--avatar-fraction",
        type=float,
        default=1.0,
        help="Fraction of AVATAR-TC train to keep (1.0 = full).",
    )
    parser.add_argument(
        "--max-avatar",
        type=int,
        default=None,
        help="Optional hard cap on AVATAR-TC train pairs.",
    )
    parser.add_argument(
        "--max-java2py-replay",
        type=int,
        default=None,
        help="Deprecated alias for --max-avatar.",
    )
    parser.add_argument(
        "--train-fraction",
        type=float,
        default=None,
        help="Deprecated alias for --avatar-fraction.",
    )
    parser.add_argument("--no-classeval", action="store_true")
    parser.add_argument("--no-design-patterns", action="store_true")
    parser.add_argument("--no-codocbench", action="store_true")
    parser.add_argument(
        "--design-upsample",
        type=int,
        default=2,
        help="Repeat design-pattern rows to keep them visible vs full AVATAR (default 2).",
    )
    parser.add_argument(
        "--max-mbpp",
        type=int,
        default=0,
        help="Max MBPP NL2Py samples (0 = all train+validation)",
    )
    parser.add_argument("--max-documint", type=int, default=5000)
    parser.add_argument(
        "--max-comments",
        type=int,
        default=0,
        help="Max comment pairs from CodeParrot (0 = disabled)",
    )
    parser.add_argument("--skip-hf", action="store_true", help="Skip HuggingFace datasets")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(PROCESSED_DIR / "qwen_multitask"),
    )
    args = parser.parse_args()

    max_mbpp = None if args.max_mbpp <= 0 else args.max_mbpp
    max_avatar = args.max_avatar if args.max_avatar is not None else args.max_java2py_replay
    avatar_fraction = (
        args.avatar_fraction if args.train_fraction is None else args.train_fraction
    )

    records = collect_all_records(
        avatar_fraction=avatar_fraction,
        max_avatar=max_avatar,
        include_classeval=not args.no_classeval,
        include_design_patterns=not args.no_design_patterns,
        include_codocbench=not args.no_codocbench,
        design_upsample=args.design_upsample,
        max_mbpp=max_mbpp,
        max_documint=args.max_documint,
        max_comments=args.max_comments,
        skip_hf=args.skip_hf,
    )
    save_multitask_dataset(records, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
