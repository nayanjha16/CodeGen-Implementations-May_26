#!/usr/bin/env python3
"""Preprocess NL-to-Python datasets into HuggingFace Dataset format."""

import argparse
import json
import os
import sys
from pathlib import Path

from datasets import Dataset, concatenate_datasets

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from prompt_templates import format_nl2py

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def load_spider(raw_dir: Path) -> list[dict]:
    """Load Spider NL+SQL pairs; use SQL as proxy Python target for NL2Py training."""
    records = []
    train_file = raw_dir / "spider" / "train_spider.json"
    if not train_file.exists():
        for candidate in raw_dir.glob("spider/**/train_spider.json"):
            train_file = candidate
            break
    if not train_file.exists():
        print(f"  [Spider] train file not found at {raw_dir / 'spider'}")
        return records

    with open(train_file) as f:
        data = json.load(f)

    for item in data:
        question = item.get("question", "").strip()
        query = item.get("query", "").strip()
        if question and query:
            python_proxy = f"# SQL equivalent\n{query}"
            records.append({
                "nl_query": question,
                "python_code": python_proxy,
                "source": "spider",
            })
    print(f"  [Spider] loaded {len(records)} samples")
    return records


def load_bird(raw_dir: Path) -> list[dict]:
    """Load BirdBench dev set NL+SQL pairs."""
    records = []
    for candidate in raw_dir.glob("bird/**/*.json"):
        if "dev" not in candidate.name.lower():
            continue
        try:
            with open(candidate) as f:
                data = json.load(f)
            items = data if isinstance(data, list) else data.get("data", [])
            for item in items:
                question = item.get("question", item.get("Question", "")).strip()
                sql = item.get("SQL", item.get("query", "")).strip()
                if question and sql:
                    records.append({
                        "nl_query": question,
                        "python_code": f"# SQL equivalent\n{sql}",
                        "source": "bird",
                    })
        except (json.JSONDecodeError, KeyError):
            continue
    print(f"  [BirdBench] loaded {len(records)} samples")
    return records


def load_mbpp(
    max_samples: int | None = None,
    splits: tuple[str, ...] = ("train", "validation"),
) -> list[dict]:
    """Load MBPP NL+Python pairs from Hugging Face (google-research-datasets/mbpp)."""
    records: list[dict] = []
    try:
        from datasets import load_dataset

        ds_dict = load_dataset("google-research-datasets/mbpp", "full")
        for split in splits:
            if split not in ds_dict:
                continue
            for item in ds_dict[split]:
                nl = (item.get("text") or "").strip()
                code = (item.get("code") or "").strip()
                setup = (item.get("test_setup_code") or "").strip()
                if setup:
                    code = f"{setup}\n{code}" if code else setup
                if nl and code:
                    records.append({
                        "nl_query": nl,
                        "python_code": code,
                        "source": "mbpp",
                    })
                if max_samples is not None and len(records) >= max_samples:
                    break
            if max_samples is not None and len(records) >= max_samples:
                break
    except Exception as e:
        print(f"  [MBPP] skipped ({e})")
    print(f"  [MBPP] loaded {len(records)} samples")
    return records


def load_bigquery_python(max_samples: int = 5000) -> list[dict]:
    """Load BigQuery/Python corpus from HuggingFace."""
    records = []
    try:
        from datasets import load_dataset
        ds = load_dataset("bigquery/bigquery-public-data-samples", split="train", streaming=True)
        count = 0
        for item in ds:
            if count >= max_samples:
                break
            desc = item.get("description", item.get("query", ""))
            code = item.get("code", item.get("sql", ""))
            if desc and code:
                records.append({
                    "nl_query": str(desc).strip(),
                    "python_code": str(code).strip(),
                    "source": "bigquery",
                })
                count += 1
    except Exception as e:
        print(f"  [BigQuery] skipped ({e})")
    print(f"  [BigQuery] loaded {len(records)} samples")
    return records


def load_codeparrot_python(max_samples: int = 10000) -> list[dict]:
    """Load Python code from CodeParrot; synthesize NL from docstrings/comments."""
    records = []
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
            if not code or len(code) < 50:
                continue
            nl = _extract_docstring_or_summary(code)
            if nl:
                records.append({
                    "nl_query": nl,
                    "python_code": code,
                    "source": "codeparrot",
                })
                count += 1
    except Exception as e:
        print(f"  [CodeParrot] skipped ({e})")
    print(f"  [CodeParrot] loaded {len(records)} samples")
    return records


def load_pile_code_subset(max_samples: int = 5000) -> list[dict]:
    """Load code subset from The Pile (via EleutherAI/pile subset)."""
    records = []
    try:
        from datasets import load_dataset
        ds = load_dataset("monology/pile-uncopyrighted", split="train", streaming=True)
        count = 0
        for item in ds:
            if count >= max_samples:
                break
            meta = item.get("meta", {})
            pile_set = meta.get("pile_set_name", "") if isinstance(meta, dict) else ""
            if "Github" not in pile_set and "Stack" not in pile_set:
                continue
            text = item.get("text", "").strip()
            if len(text) < 100:
                continue
            nl = f"Write Python code for: {text[:200].replace(chr(10), ' ')}"
            records.append({
                "nl_query": nl,
                "python_code": text[:2048],
                "source": "pile",
            })
            count += 1
    except Exception as e:
        print(f"  [Pile] skipped ({e})")
    print(f"  [Pile] loaded {len(records)} samples")
    return records


def _extract_docstring_or_summary(code: str) -> str | None:
    """Extract first docstring or top comment as NL description."""
    lines = code.split("\n")
    in_docstring = False
    docstring_lines = []
    for line in lines[:30]:
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            quote = stripped[:3]
            content = stripped[3:]
            if content.endswith(quote) and len(content) > 3:
                return content[:-3].strip()
            in_docstring = True
            if content:
                docstring_lines.append(content)
            continue
        if in_docstring:
            if quote in stripped:
                docstring_lines.append(stripped.replace(quote, ""))
                return " ".join(docstring_lines).strip()
            docstring_lines.append(stripped)
            continue
        if stripped.startswith("#") and len(stripped) > 2:
            return stripped.lstrip("# ").strip()
    if docstring_lines:
        return " ".join(docstring_lines).strip()
    first_def = next((l for l in lines if l.strip().startswith("def ")), None)
    if first_def:
        return f"Implement function: {first_def.strip()}"
    return None


def build_dataset(records: list[dict], val_ratio: float = 0.1) -> tuple[Dataset, Dataset]:
    """Split records into train/val and add formatted text column."""
    import random
    random.seed(42)
    random.shuffle(records)

    split_idx = max(1, int(len(records) * (1 - val_ratio)))
    train_records = records[:split_idx]
    val_records = records[split_idx:] or records[:max(1, len(records) // 10)]

    def to_rows(recs):
        return {
            "text": [format_nl2py(r["nl_query"], r["python_code"]) for r in recs],
            "nl_query": [r["nl_query"] for r in recs],
            "python_code": [r["python_code"] for r in recs],
            "source": [r["source"] for r in recs],
        }

    train_ds = Dataset.from_dict(to_rows(train_records))
    val_ds = Dataset.from_dict(to_rows(val_records))
    return train_ds, val_ds


def main():
    parser = argparse.ArgumentParser(description="Preprocess NL2Py datasets")
    parser.add_argument("--max-mbpp", type=int, default=0, help="Max MBPP samples (0 = all)")
    parser.add_argument("--max-codeparrot", type=int, default=0, help="0 = skip CodeParrot")
    parser.add_argument("--max-pile", type=int, default=0, help="0 = skip Pile")
    parser.add_argument("--max-bigquery", type=int, default=0, help="0 = skip BigQuery")
    parser.add_argument(
        "--include-sql",
        action="store_true",
        help="Also load Spider/BirdBench NL→SQL proxies (off by default)",
    )
    parser.add_argument("--skip-hf", action="store_true", help="Skip HuggingFace datasets")
    args = parser.parse_args()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading NL2Py datasets...")

    all_records: list[dict] = []
    if args.include_sql:
        all_records.extend(load_spider(RAW_DIR))
        all_records.extend(load_bird(RAW_DIR))
    else:
        print("  [Spider/Bird] skipped (default MBPP-only; pass --include-sql to enable)")

    if not args.skip_hf:
        max_mbpp = None if args.max_mbpp <= 0 else args.max_mbpp
        all_records.extend(load_mbpp(max_samples=max_mbpp))
        if args.max_codeparrot > 0:
            all_records.extend(load_codeparrot_python(args.max_codeparrot))
        if args.max_bigquery > 0:
            all_records.extend(load_bigquery_python(args.max_bigquery))
        if args.max_pile > 0:
            all_records.extend(load_pile_code_subset(args.max_pile))

    if not all_records:
        print("WARNING: No records loaded. Creating minimal synthetic dataset for testing.")
        all_records = [
            {
                "nl_query": "Write a function that returns the sum of two numbers",
                "python_code": "def add(a, b):\n    return a + b",
                "source": "synthetic",
            },
            {
                "nl_query": "Sort a list in ascending order",
                "python_code": "def sort_list(lst):\n    return sorted(lst)",
                "source": "synthetic",
            },
            {
                "nl_query": "Check if a number is prime",
                "python_code": (
                    "def is_prime(n):\n"
                    "    if n < 2:\n"
                    "        return False\n"
                    "    for i in range(2, int(n**0.5) + 1):\n"
                    "        if n % i == 0:\n"
                    "            return False\n"
                    "    return True"
                ),
                "source": "synthetic",
            },
        ]

    print(f"Total records: {len(all_records)}")
    train_ds, val_ds = build_dataset(all_records)

    out_dir = PROCESSED_DIR / "nl2py"
    train_ds.save_to_disk(str(out_dir / "train"))
    val_ds.save_to_disk(str(out_dir / "val"))
    print(f"Saved train ({len(train_ds)}) and val ({len(val_ds)}) to {out_dir}")


if __name__ == "__main__":
    main()
