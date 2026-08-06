#!/usr/bin/env python3
"""Preprocess Java-to-Python datasets into HuggingFace Dataset format."""

import argparse
import json
import sys
from pathlib import Path

from datasets import Dataset

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from prompt_templates import format_java2py

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def load_codocbench(raw_dir: Path) -> list[dict]:
    """Load CoDocBench Java-Python translation pairs."""
    records = []
    codoc_dir = raw_dir / "codocbench"
    if not codoc_dir.exists():
        print(f"  [CoDocBench] not found at {codoc_dir}")
        return records

    for json_file in codoc_dir.rglob("*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)
            items = data if isinstance(data, list) else data.get("data", data.get("examples", []))
            if not isinstance(items, list):
                continue
            for item in items:
                java = (
                    item.get("java", item.get("java_code", item.get("source", "")))
                ).strip()
                python = (
                    item.get("python", item.get("python_code", item.get("target", "")))
                ).strip()
                if java and python:
                    records.append({
                        "java_code": java,
                        "python_code": python,
                        "source": "codocbench",
                    })
        except (json.JSONDecodeError, AttributeError):
            continue

    for pair_file in codoc_dir.rglob("*"):
        if pair_file.suffix in (".java",) and pair_file.with_suffix(".py").exists():
            java = pair_file.read_text()
            python = pair_file.with_suffix(".py").read_text()
            if java.strip() and python.strip():
                records.append({
                    "java_code": java.strip(),
                    "python_code": python.strip(),
                    "source": "codocbench_files",
                })

    print(f"  [CoDocBench] loaded {len(records)} samples")
    return records


def load_codeparrot_pairs(max_samples: int = 5000) -> list[dict]:
    """Create synthetic Java-Python pairs from CodeParrot (Java only, paired with stubs)."""
    records = []
    try:
        from datasets import load_dataset
        ds = load_dataset(
            "codeparrot/github-code",
            languages=["Java"],
            split="train",
            streaming=True,
            trust_remote_code=True,
        )
        count = 0
        for item in ds:
            if count >= max_samples:
                break
            java = item.get("code", "").strip()
            if not java or len(java) < 30:
                continue
            python_stub = _java_to_python_heuristic(java)
            if python_stub:
                records.append({
                    "java_code": java,
                    "python_code": python_stub,
                    "source": "codeparrot_java",
                })
                count += 1
    except Exception as e:
        print(f"  [CodeParrot Java] skipped ({e})")
    print(f"  [CodeParrot Java] loaded {len(records)} samples")
    return records


def _java_to_python_heuristic(java_code: str) -> str | None:
    """Simple heuristic mapping for bootstrapping when no Python reference exists."""
    lines = java_code.split("\n")
    py_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("//"):
            py_lines.append("#" + stripped[2:])
        elif "System.out.println" in stripped:
            content = stripped.split("System.out.println")[1].strip().rstrip(";")
            py_lines.append(f"print({content})")
        elif stripped.startswith("public class"):
            class_name = stripped.split()[-1].rstrip("{").strip()
            py_lines.append(f"class {class_name}:")
        elif stripped.startswith("public static void main"):
            py_lines.append("if __name__ == '__main__':")
        elif "int " in stripped and "(" in stripped and ")" in stripped:
            py_lines.append(stripped.replace("int ", "def ").replace("{", ":").rstrip(";"))
        else:
            converted = (
                stripped.replace(";", "")
                .replace("true", "True")
                .replace("false", "False")
                .replace("null", "None")
            )
            if converted:
                py_lines.append(converted)
    result = "\n".join(py_lines)
    return result if len(result) >= 10 else None


def build_dataset(records: list[dict], val_ratio: float = 0.1) -> tuple[Dataset, Dataset]:
    import random
    random.seed(42)
    random.shuffle(records)

    split_idx = max(1, int(len(records) * (1 - val_ratio)))
    train_records = records[:split_idx]
    val_records = records[split_idx:] or records[:max(1, len(records) // 10)]

    def to_rows(recs):
        return {
            "text": [format_java2py(r["java_code"], r["python_code"]) for r in recs],
            "java_code": [r["java_code"] for r in recs],
            "python_code": [r["python_code"] for r in recs],
            "source": [r["source"] for r in recs],
        }

    return (
        Dataset.from_dict(to_rows(train_records)),
        Dataset.from_dict(to_rows(val_records)),
    )


def main():
    parser = argparse.ArgumentParser(description="Preprocess Java2Py datasets")
    parser.add_argument("--max-codeparrot", type=int, default=3000)
    parser.add_argument("--skip-hf", action="store_true")
    args = parser.parse_args()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading Java2Py datasets...")

    all_records: list[dict] = []
    all_records.extend(load_codocbench(RAW_DIR))

    if not args.skip_hf:
        all_records.extend(load_codeparrot_pairs(args.max_codeparrot))

    if not all_records:
        print("WARNING: No records loaded. Creating minimal synthetic dataset for testing.")
        all_records = [
            {
                "java_code": (
                    "public class Hello {\n"
                    "    public static void main(String[] args) {\n"
                    "        System.out.println(\"Hello\");\n"
                    "    }\n"
                    "}"
                ),
                "python_code": 'print("Hello")',
                "source": "synthetic",
            },
            {
                "java_code": (
                    "public int add(int a, int b) {\n"
                    "    return a + b;\n"
                    "}"
                ),
                "python_code": "def add(a, b):\n    return a + b",
                "source": "synthetic",
            },
            {
                "java_code": (
                    "public boolean isEven(int n) {\n"
                    "    return n % 2 == 0;\n"
                    "}"
                ),
                "python_code": "def is_even(n):\n    return n % 2 == 0",
                "source": "synthetic",
            },
        ]

    print(f"Total records: {len(all_records)}")
    train_ds, val_ds = build_dataset(all_records)

    out_dir = PROCESSED_DIR / "java2py"
    train_ds.save_to_disk(str(out_dir / "train"))
    val_ds.save_to_disk(str(out_dir / "val"))
    print(f"Saved train ({len(train_ds)}) and val ({len(val_ds)}) to {out_dir}")


if __name__ == "__main__":
    main()
