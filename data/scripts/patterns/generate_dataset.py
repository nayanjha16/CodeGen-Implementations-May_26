#!/usr/bin/env python3
"""Expand pattern/SOLID templates × domains × tiers into a parallel corpus."""

from __future__ import annotations

import argparse
import ast
import json
import random
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from code_templates import render
from define_catalog import (
    COMBOS,
    PATTERNS,
    SEED,
    SOLID,
    TEST_DOMAINS,
    TIERS,
    TRAIN_DOMAINS,
    DomainContext,
)

PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "design_patterns_solid"


def _python_test_for(record_id: str, pattern_id: str, ctx: DomainContext, module_src: str) -> str:
    """Write a pytest that loads the sibling solution and runs a light check."""
    c, s = ctx.pascal, ctx.snake
    checks: list[str] = [
        "    mod = _load()",
        "    assert any(isinstance(getattr(mod, n), type) for n in dir(mod) if not n.startswith('_'))",
    ]
    if pattern_id == "singleton":
        checks = [
            "    mod = _load()",
            f"    cls = getattr(mod, '{c}Singleton')",
            "    a, b = cls(), cls()",
            f'    a.set_value("{s}-one")',
            "    assert a is b",
            f'    assert b.get_value() == "{s}-one"',
        ]
    elif pattern_id == "strategy":
        checks = [
            "    mod = _load()",
            f"    ctx = mod.{c}Context(mod.{c}DiscountStrategy())",
            "    assert ctx.execute(10) == 5",
        ]
    elif pattern_id == "factory":
        checks = [
            "    mod = _load()",
            f"    f = mod.{c}Factory()",
            f'    assert f.create("premium").operate() == "premium-{s}"',
        ]
    elif pattern_id == "observer":
        checks = [
            "    mod = _load()",
            f"    subj, lis = mod.{c}Subject(), mod.{c}Listener()",
            "    subj.attach(lis)",
            '    subj.notify_all("e")',
            f'    assert lis.last == "{s}:e"',
        ]
    elif pattern_id == "ocp":
        checks = [
            "    mod = _load()",
            f"    eng = mod.{c}PriceEngine(mod.{c}TenPercent())",
            "    assert eng.quote(100) == 90",
        ]
    elif pattern_id == "srp":
        checks = [
            "    mod = _load()",
            f'    r = mod.{c}Record("a", 3)',
            f"    assert mod.{c}Formatter().format(r) == 'a=3'",
        ]
    elif pattern_id == "dip":
        checks = [
            "    mod = _load()",
            f"    app = mod.{c}AppService(mod.{c}HttpGateway())",
            f'    assert app.publish("p") == "http-{s}:p"',
        ]

    body = "\n".join(checks)
    return f'''"""Pytest for {record_id} ({pattern_id} / {ctx.domain})."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "solution" / "{record_id}.py"
    spec = importlib.util.spec_from_file_location("{record_id}", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_{record_id.replace("-", "_")}():
{body}
'''


def _candidate_specs() -> list[dict]:
    """Build the full expansion grid before sampling to targets."""
    specs: list[dict] = []
    catalog = (
        [("design_pattern", p) for p in PATTERNS]
        + [("solid", p) for p in SOLID]
        + [("combo", p) for p in COMBOS]
    )
    for kind, item in catalog:
        for domain in TRAIN_DOMAINS + TEST_DOMAINS:
            split = "test" if domain in TEST_DOMAINS else "train"
            for tier_i, tier in enumerate(TIERS):
                # Test split: prefer minimal + one richer tier for coverage without explosion
                if split == "test" and tier == "errors":
                    continue
                specs.append(
                    {
                        "kind": kind,
                        "pattern_id": item["id"],
                        "label": item["label"],
                        "category": item["category"],
                        "domain": domain,
                        "tier": tier,
                        "tier_index": tier_i,
                        "split": split,
                    }
                )
    return specs


def _select_specs(
    specs: list[dict],
    target_train: int,
    target_test: int,
    seed: int,
) -> list[dict]:
    rng = random.Random(seed)
    train = [s for s in specs if s["split"] == "train"]
    test = [s for s in specs if s["split"] == "test"]

    def cover_then_fill(pool: list[dict], target: int) -> list[dict]:
        # Ensure every pattern_id / solid appears at least once (per split pool)
        by_pid: dict[str, list[dict]] = defaultdict(list)
        for s in pool:
            by_pid[s["pattern_id"]].append(s)
        chosen: list[dict] = []
        seen_ids: set[str] = set()
        for pid, items in by_pid.items():
            # prefer minimal tier first
            items_sorted = sorted(items, key=lambda x: x["tier_index"])
            pick = items_sorted[0]
            chosen.append(pick)
            seen_ids.add(_spec_key(pick))
        remaining = [s for s in pool if _spec_key(s) not in seen_ids]
        rng.shuffle(remaining)
        for s in remaining:
            if len(chosen) >= target:
                break
            chosen.append(s)
        if len(chosen) < target:
            # Upsample by cloning with extra synthetic tier tags via domain reshuffle
            # Prefer unique structural variants; if short, cycle remaining
            while len(chosen) < target and remaining:
                s = dict(rng.choice(remaining))
                # bump as vN duplicate only if necessary — change tier label in id via copy index
                s["_dup"] = len(chosen)
                chosen.append(s)
        rng.shuffle(chosen)
        return chosen[:target]

    # SOLID test coverage: at least 5 per principle if possible
    test_selected = cover_then_fill(test, target_test)
    # Reinforce SOLID in test
    solid_test = [s for s in test if s["kind"] == "solid"]
    by_solid: dict[str, list[dict]] = defaultdict(list)
    for s in solid_test:
        by_solid[s["pattern_id"]].append(s)
    have = {s["pattern_id"] for s in test_selected if s["kind"] == "solid"}
    for pid, items in by_solid.items():
        count = sum(1 for s in test_selected if s["pattern_id"] == pid)
        need = max(0, 5 - count)
        for item in sorted(items, key=lambda x: x["tier_index"]):
            if need <= 0:
                break
            key = _spec_key(item)
            if any(_spec_key(x) == key for x in test_selected):
                continue
            test_selected.append(item)
            need -= 1
    # trim if overshot
    if len(test_selected) > target_test:
        # keep all solid first
        solid_keep = [s for s in test_selected if s["kind"] == "solid"]
        other = [s for s in test_selected if s["kind"] != "solid"]
        rng.shuffle(other)
        test_selected = (solid_keep + other)[:target_test]

    train_selected = cover_then_fill(train, target_train)
    return train_selected + test_selected


def _spec_key(s: dict) -> str:
    return f"{s['pattern_id']}::{s['domain']}::{s['tier']}"


def _record_id(s: dict) -> str:
    base = f"{s['pattern_id']}_{s['domain']}_{s['tier']}"
    if "_dup" in s:
        base = f"{base}_r{s['_dup']}"
    return base


def generate(
    target_train: int = 1500,
    target_test: int = 200,
    seed: int = SEED,
    out_root: Path | None = None,
) -> dict:
    out_root = out_root or RAW_ROOT
    if out_root.exists():
        # Keep README if present; wipe generated + manifests
        gen = out_root / "generated"
        if gen.exists():
            shutil.rmtree(gen)
        for name in ("manifest_train.jsonl", "manifest_test.jsonl", "split.json"):
            p = out_root / name
            if p.exists():
                p.unlink()

    dirs = {
        "java_sol": out_root / "generated" / "java" / "solution",
        "java_test": out_root / "generated" / "java" / "test",
        "py_sol": out_root / "generated" / "python" / "solution",
        "py_test": out_root / "generated" / "python" / "test",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    specs = _select_specs(_candidate_specs(), target_train, target_test, seed)
    train_manifest: list[dict] = []
    test_manifest: list[dict] = []
    counts: Counter[str] = Counter()
    split_ids = {"train": [], "test": [], "seed": seed}

    for spec in specs:
        rid = _record_id(spec)
        ctx = DomainContext.from_domain(spec["domain"])
        java, python, java_test, _ = render(spec["pattern_id"], ctx, spec["tier"])
        # Validate python parses before writing
        ast.parse(python)
        py_test = _python_test_for(rid, spec["pattern_id"], ctx, python)

        rel_java = f"generated/java/solution/{rid}.java"
        rel_py = f"generated/python/solution/{rid}.py"
        rel_jt = f"generated/java/test/{rid}Test.java"
        rel_pt = f"generated/python/test/test_{rid}.py"

        (out_root / rel_java).write_text(java, encoding="utf-8")
        (out_root / rel_py).write_text(python, encoding="utf-8")
        (out_root / rel_jt).write_text(java_test, encoding="utf-8")
        (out_root / rel_pt).write_text(py_test, encoding="utf-8")

        rec = {
            "id": rid,
            "category": spec["category"],
            "pattern_or_principle": spec["label"],
            "pattern_id": spec["pattern_id"],
            "kind": spec["kind"],
            "domain": spec["domain"],
            "tier": spec["tier"],
            "java_path": rel_java,
            "python_path": rel_py,
            "java_test_path": rel_jt,
            "python_test_path": rel_pt,
            "split": spec["split"],
        }
        if spec["split"] == "train":
            train_manifest.append(rec)
            split_ids["train"].append(rid)
        else:
            test_manifest.append(rec)
            split_ids["test"].append(rid)
        counts[spec["label"]] += 1

    def write_jsonl(path: Path, rows: list[dict]) -> None:
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row) + "\n")

    write_jsonl(out_root / "manifest_train.jsonl", train_manifest)
    write_jsonl(out_root / "manifest_test.jsonl", test_manifest)

    summary = {
        "seed": seed,
        "train_count": len(train_manifest),
        "test_count": len(test_manifest),
        "train_domains": TRAIN_DOMAINS,
        "test_domains": TEST_DOMAINS,
        "counts_by_label": dict(sorted(counts.items())),
        "train_ids": split_ids["train"],
        "test_ids": split_ids["test"],
    }
    (out_root / "split.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Convenience symlinks like ClassEval
    java_link = out_root / "Java"
    py_link = out_root / "Python"
    for link, target in (
        (java_link, Path("generated/java")),
        (py_link, Path("generated/python")),
    ):
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(target)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate design patterns + SOLID dataset")
    parser.add_argument("--target-train", type=int, default=1500)
    parser.add_argument("--target-test", type=int, default=200)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument(
        "--out-root",
        type=str,
        default=str(RAW_ROOT),
        help="Output directory for raw dataset",
    )
    args = parser.parse_args()
    summary = generate(
        target_train=args.target_train,
        target_test=args.target_test,
        seed=args.seed,
        out_root=Path(args.out_root),
    )
    print(
        f"Generated train={summary['train_count']} test={summary['test_count']} "
        f"-> {args.out_root}"
    )
    print("Labels:", len(summary["counts_by_label"]))


if __name__ == "__main__":
    main()
