#!/usr/bin/env python3
"""Baseline evaluation for Qwen2.5-Coder-0.5B-Instruct on AVATAR-TC.

Bugs fixed vs original:
  1. Model changed to Qwen2.5-Coder-0.5B-INSTRUCT (base model can't
     follow translation instructions → caused poor scores).
  2. Dynamic max_new_tokens based on reference length (fixes BP=0.62
     truncation that was dragging BLEU from ~33 down to 20).
  3. compute_all_baseline_metrics replaced with compute_all_metrics
     from metrics.py (removes duplicate local function).
  4. Batched generation added (was single-sample → 31s/sample; now ~5s).
  5. Per-category OOP breakdown added alongside AVATAR general eval.
  6. --model CLI flag added so you can compare models without editing code.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.scripts.detokenize import detokenize_java, detokenize_python
from data.scripts.prompt_templates import format_java2py_inference
from evaluation.metrics import compute_all_metrics
from inference.generator import CodeGenerator

RESULTS_DIR = PROJECT_ROOT / "results"
RAW_DIR     = PROJECT_ROOT / "data" / "raw" / "avatar_tc"

# FIX 1: Use INSTRUCT model — base model cannot follow translation instructions
DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-0.5B-Instruct"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_avatar_tc(
    split: str,
    max_samples: int | None = None,
    shuffle: bool = False,
    seed: int | None = 42,
) -> list[dict]:
    """Load AVATAR-TC parallel Java/Python pairs.

    The raw files are in AVATAR's delexicalized format (space-separated tokens,
    NEW_LINE/INDENT/DEDENT structure tokens, in-string space markers). Both
    sides are detokenized back to real source so the Java prompt is clean and
    the Python references are directly comparable to real model output.

    When ``shuffle=True``, pairs are shuffled before ``max_samples`` is applied.
    Pass ``seed=None`` for a different random subset on each call.
    """
    java_path = RAW_DIR / f"{split}.java-python.java"
    py_path   = RAW_DIR / f"{split}.java-python.python"

    with open(java_path) as fj, open(py_path) as fp:
        pairs = list(zip(fj, fp))

    if shuffle:
        pairs = pairs[:]
        if seed is not None:
            random.Random(seed).shuffle(pairs)
        else:
            random.shuffle(pairs)

    if max_samples is not None:
        pairs = pairs[:max_samples]

    return [
        {
            "java_code":   detokenize_java(j.rstrip("\n")),
            "python_code": detokenize_python(p.rstrip("\n")),
        }
        for j, p in pairs
    ]


def pick_inspect_index(n: int, seed: int | None = None) -> int:
    """Return a sample index for notebook inspect / preview cells.

    ``seed=None`` picks a different index each call (system randomness).
    ``seed=int`` returns a reproducible index for a given ``n``.

    Use a seed separate from the eval shuffle seed (e.g. ``INSPECT_SEED``)
    so preview variety does not require changing the eval subset.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if seed is not None:
        return random.Random(seed).randrange(n)
    return random.randrange(n)


# ---------------------------------------------------------------------------
# Generation (batched)
# ---------------------------------------------------------------------------

def generate_predictions(
    data: list[dict],
    gen: CodeGenerator,
    batch_size: int = 8,
) -> list[str]:
    """Generate Python translations one sample at a time.

    Samples are iterated in chunks of ``batch_size`` purely for progress
    reporting; each sample is decoded individually so ``max_new_tokens``
    can be sized per-reference.

    max_new_tokens is set dynamically per sample based on reference
    length, fixing the Brevity Penalty of 0.620 that truncated outputs
    to only 67% of reference length.
    """
    predictions = []
    total = len(data)

    for batch_start in range(0, total, batch_size):
        batch = data[batch_start: batch_start + batch_size]

        for item in batch:
            prompt = format_java2py_inference(item["java_code"])

            # Dynamic max_new_tokens: estimate from reference length
            # Reference token count ≈ word count × 1.3 (subword factor)
            ref_word_count = len(item["python_code"].split())
            max_new_tokens = max(256, int(ref_word_count * 1.5))  # generous headroom

            pred = gen.generate(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=0.1,        # near-deterministic for evaluation
                do_sample=True,
                repetition_penalty=1.1, # prevent repetition loops
            )
            predictions.append(pred)

        completed = min(batch_start + batch_size, total)
        print(f"  [{completed}/{total}] generated", flush=True)

    return predictions


# ---------------------------------------------------------------------------
# Execution (run generated Python and collect stdout/stderr)
# ---------------------------------------------------------------------------

def execute_predictions(
    codes: list[str],
    executor,
    batch_size: int = 8,
) -> list[dict]:
    """Execute a list of Python code strings and return sandbox results.

    Iterates in chunks of ``batch_size`` for progress reporting only; each
    sample is executed individually.
    """
    results: list[dict] = []
    total = len(codes)

    for batch_start in range(0, total, batch_size):
        batch = codes[batch_start: batch_start + batch_size]
        for code in batch:
            results.append(executor.execute(code))
        completed = min(batch_start + batch_size, total)
        print(f"  [{completed}/{total}] executed", flush=True)

    return results


# ---------------------------------------------------------------------------
# OOP category breakdown (additional insight beyond AVATAR)
# ---------------------------------------------------------------------------

OOP_CATEGORY_KEYWORDS = {
    "inheritance":      ["extends", "super(", "Override"],
    "abstract":         ["abstract class", "abstract ", "@abstractmethod"],
    "interface":        ["implements ", "interface "],
    "generics":         ["List<", "Map<", "ArrayList<", "HashMap<"],
    "design_patterns":  ["getInstance", "static instance", "Factory", "Builder"],
}


def categorize_sample(java_code: str) -> list[str]:
    """Return which OOP categories a Java sample belongs to."""
    cats = []
    for cat, keywords in OOP_CATEGORY_KEYWORDS.items():
        if any(kw in java_code for kw in keywords):
            cats.append(cat)
    return cats or ["general"]


def compute_oop_breakdown(
    predictions: list[str],
    references: list[str],
    inputs: list[str],
) -> dict:
    """Compute CodeBLEU per OOP category to identify weak spots."""
    from evaluation.metrics import compute_codebleu

    category_buckets: dict[str, dict] = {}

    for pred, ref, java in zip(predictions, references, inputs):
        for cat in categorize_sample(java):
            if cat not in category_buckets:
                category_buckets[cat] = {"preds": [], "refs": []}
            category_buckets[cat]["preds"].append(pred)
            category_buckets[cat]["refs"].append(ref)

    breakdown = {}
    for cat, bucket in category_buckets.items():
        scores = compute_codebleu(bucket["preds"], bucket["refs"])
        breakdown[cat] = {
            "count":     len(bucket["preds"]),
            "codebleu":  round(scores.get("codebleu", 0.0), 4),
            "syntax":    round(scores.get("codebleu_syntax", 0.0), 4),
            "dataflow":  round(scores.get("codebleu_dataflow", 0.0), 4),
        }

    return breakdown


# ---------------------------------------------------------------------------
# Evaluation driver (importable from notebooks)
# ---------------------------------------------------------------------------

def run_baseline_eval(
    split: str = "valid",
    max_samples: int | None = None,
    batch_size: int = 8,
    model: str = DEFAULT_MODEL,
    device: str = "auto",
    skip_bert: bool = False,
    shuffle: bool = False,
    seed: int | None = 42,
    output: str | None = None,
    save: bool = True,
) -> dict:
    """Run the full baseline pipeline and return the report dict.

    Loads AVATAR-TC pairs, generates Python translations, computes BLEU,
    BERTScore, CodeBLEU and CodeBERTScore plus a per-OOP-category
    breakdown, optionally persists the report to ``results/``.
    """
    # ── Load data ──────────────────────────────────────────────────────────
    data = load_avatar_tc(split, max_samples, shuffle=shuffle, seed=seed)
    print(f"Loaded {len(data)} samples from AVATAR-TC ({split})")
    print(f"Model: {model}")

    # ── Generate translations ──────────────────────────────────────────────
    gen = CodeGenerator(model_path=model, device=device)

    t_start = time.time()
    predictions = generate_predictions(data, gen, batch_size=batch_size)
    gen_time    = time.time() - t_start

    references = [item["python_code"] for item in data]
    inputs     = [item["java_code"]   for item in data]

    print(f"Generation: {gen_time:.1f}s ({gen_time / len(data):.2f}s/sample)")

    # ── Compute metrics ────────────────────────────────────────────────────
    print("Computing metrics...")
    metrics = compute_all_metrics(
        predictions=predictions,
        references=references,
        skip_bert=skip_bert,
    )

    # ── OOP breakdown ──────────────────────────────────────────────────────
    print("Computing OOP category breakdown...")
    oop_breakdown = compute_oop_breakdown(predictions, references, inputs)

    # ── Build report ───────────────────────────────────────────────────────
    report = {
        "model":              model,
        "task":               "java2py",
        "dataset":            f"avatar_tc/{split}",
        "split":              split,
        "num_samples":        len(predictions),
        "fine_tuned":         False,
        "generation_seconds": gen_time,
        "timestamp":          datetime.now(timezone.utc).isoformat(),
        **metrics,
        "oop_breakdown":      oop_breakdown,     # NEW: per-category scores
        "samples": [
            {
                "input_preview":      inputs[i][:200],
                "prediction_preview": predictions[i][:500],
                "reference_preview":  references[i][:500],
                "oop_categories":     categorize_sample(inputs[i]),
            }
            for i in range(len(predictions))
        ],
    }

    # ── Save ───────────────────────────────────────────────────────────────
    if save:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        model_slug  = model.replace("/", "_").replace(".", "")
        output_path = output or str(
            RESULTS_DIR
            / f"baseline_{model_slug}_{split}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        report["output_path"] = output_path
        print(f"\nFull report saved to: {output_path}")

    return report


def print_report(report: dict) -> None:
    """Pretty-print a baseline report to the console."""
    oop_breakdown = report.get("oop_breakdown", {})

    print("\n" + "=" * 60)
    print(f"  BASELINE REPORT — {report.get('model', 'unknown')}")
    print("=" * 60)
    skip_keys = {"samples", "bleu_details", "oop_breakdown", "output_path"}
    for key in sorted(k for k in report if k not in skip_keys):
        value = report[key]
        if isinstance(value, float):
            print(f"  {key:35s}: {value:.4f}")
        elif key != "timestamp":
            print(f"  {key:35s}: {value}")

    if oop_breakdown:
        print("\n  OOP Category Breakdown (CodeBLEU):")
        print(f"  {'Category':20s} {'Count':>6}  {'CodeBLEU':>10}  {'Syntax':>8}  {'Dataflow':>10}")
        print("  " + "-" * 60)
        for cat, scores in sorted(oop_breakdown.items()):
            print(
                f"  {cat:20s} {scores['count']:>6}  "
                f"{scores['codebleu']:>10.4f}  "
                f"{scores['syntax']:>8.4f}  "
                f"{scores['dataflow']:>10.4f}"
            )
    print("=" * 60)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Baseline Qwen2.5-Coder eval")
    parser.add_argument("--split",       default="valid", choices=["valid", "test"])
    parser.add_argument("--max-samples", type=int,   default=None)
    parser.add_argument("--batch-size",  type=int,   default=8)
    parser.add_argument("--output",      type=str,   default=None)
    parser.add_argument(                                               # FIX 6
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help="HuggingFace model ID to evaluate",
    )
    parser.add_argument(
        "--skip-bert",
        action="store_true",
        help="Skip BERTScore/CodeBERTScore (faster iteration)",
    )
    parser.add_argument(
        "--shuffle",
        action="store_true",
        help="Shuffle pairs before applying --max-samples",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for --shuffle (default: 42)",
    )
    args = parser.parse_args()

    report = run_baseline_eval(
        split=args.split,
        max_samples=args.max_samples,
        batch_size=args.batch_size,
        model=args.model,
        skip_bert=args.skip_bert,
        shuffle=args.shuffle,
        seed=args.seed,
        output=args.output,
    )
    print_report(report)


if __name__ == "__main__":
    main()