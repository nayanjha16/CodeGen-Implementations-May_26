#!/usr/bin/env python3
"""Smoke-validate the design_patterns_solid corpus."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
DEFAULT_ROOT = PROJECT_ROOT / "data" / "raw" / "design_patterns_solid"


def load_manifest(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    train_path = root / "manifest_train.jsonl"
    test_path = root / "manifest_test.jsonl"
    if not train_path.exists() or not test_path.exists():
        return [f"Missing manifests under {root}"]

    train = load_manifest(train_path)
    test = load_manifest(test_path)
    train_ids = {r["id"] for r in train}
    test_ids = {r["id"] for r in test}
    overlap = train_ids & test_ids
    if overlap:
        errors.append(f"Train/test id overlap: {sorted(overlap)[:5]}")

    train_domains = {r["domain"] for r in train}
    test_domains = {r["domain"] for r in test}
    domain_overlap = train_domains & test_domains
    if domain_overlap:
        errors.append(f"Train/test domain overlap: {sorted(domain_overlap)}")

    seen: set[str] = set()
    for split_name, rows in (("train", train), ("test", test)):
        for r in rows:
            rid = r["id"]
            if rid in seen:
                errors.append(f"Duplicate id: {rid}")
            seen.add(rid)
            for key in ("java_path", "python_path", "java_test_path", "python_test_path"):
                p = root / r[key]
                if not p.exists():
                    errors.append(f"Missing {key} for {rid}: {p}")
                    continue
                text = p.read_text(encoding="utf-8")
                if not text.strip():
                    errors.append(f"Empty file {p}")
            py = root / r["python_path"]
            if py.exists():
                try:
                    ast.parse(py.read_text(encoding="utf-8"))
                except SyntaxError as e:
                    errors.append(f"Python syntax error {rid}: {e}")
            java = root / r["java_path"]
            if java.exists():
                jtxt = java.read_text(encoding="utf-8")
                if "class " not in jtxt and "interface " not in jtxt:
                    errors.append(f"Java missing class/interface: {rid}")

    # Coverage checks on test set
    labels = {r["pattern_or_principle"] for r in test}
    solid_needed = {"srp", "ocp", "lsp", "isp", "dip"}
    missing_solid = solid_needed - labels
    if missing_solid:
        errors.append(f"Test missing SOLID labels: {sorted(missing_solid)}")

    solid_counts = {}
    for r in test:
        if r["kind"] == "solid":
            solid_counts[r["pattern_or_principle"]] = solid_counts.get(r["pattern_or_principle"], 0) + 1
    for lab in solid_needed:
        if solid_counts.get(lab, 0) < 5:
            errors.append(f"Test SOLID {lab} has {solid_counts.get(lab, 0)} < 5 examples")

    print(f"train={len(train)} test={len(test)} unique_ids={len(seen)}")
    print(f"test_domains={sorted(test_domains)}")
    print(f"solid_test_counts={solid_counts}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=str, default=str(DEFAULT_ROOT))
    args = parser.parse_args()
    errors = validate(Path(args.root))
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("VALIDATION OK")


if __name__ == "__main__":
    main()
