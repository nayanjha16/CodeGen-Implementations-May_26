#!/usr/bin/env python3
"""Smoke-evaluate the multi-task model on held-out val samples per task."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "inference"))
sys.path.insert(0, str(PROJECT_ROOT / "data" / "scripts"))

from datasets import load_from_disk

from generator import load_generator
from prompt_templates import (
    format_code2doc_inference,
    format_comment_inference,
    format_java2py_inference,
    format_nl2py_inference,
)

TASK_PROMPT_BUILDERS = {
    "java2py": lambda ex: format_java2py_inference(ex.get("java_code", "")),
    "nl2py": lambda ex: format_nl2py_inference(ex.get("nl_query", "")),
    "code2doc": lambda ex: format_code2doc_inference(ex.get("python_code", "")),
    "comments": lambda ex: format_comment_inference(ex.get("code_no_comments", "")),
}


def _extract_fields_from_text(text: str, task: str) -> dict:
    """Best-effort field extraction from formatted training text."""
    if task == "java2py":
        java_m = re.search(r"```java\n(.*?)```", text, re.DOTALL)
        if java_m:
            return {"java_code": java_m.group(1).strip()}
    if task == "nl2py":
        m = re.search(r"Write Python for: (.*?)\n### Response:", text, re.DOTALL)
        if m:
            return {"nl_query": m.group(1).strip()}
    if task == "code2doc":
        m = re.search(r"```python\n(.*?)```", text, re.DOTALL)
        if m:
            return {"python_code": m.group(1).strip()}
    if task == "comments":
        m = re.search(r"```python\n(.*?)```", text, re.DOTALL)
        if m:
            return {"code_no_comments": m.group(1).strip()}
    return {}


def run_eval(
    split: str = "val",
    max_per_task: int = 5,
    device: str = "auto",
    output: str | None = None,
) -> dict:
    val_path = PROJECT_ROOT / "data" / "processed" / "qwen_multitask" / split
    if not val_path.exists():
        raise FileNotFoundError(
            f"Multi-task dataset not found at {val_path}. "
            "Run: python data/scripts/preprocess_multitask.py"
        )

    ds = load_from_disk(str(val_path))
    results: dict[str, list[dict]] = {t: [] for t in TASK_PROMPT_BUILDERS}

    generators = {task: load_generator(task) for task in TASK_PROMPT_BUILDERS}

    for i in range(len(ds)):
        task = ds[i]["task"]
        if task not in results or len(results[task]) >= max_per_task:
            continue

        fields = _extract_fields_from_text(ds[i]["text"], task)
        if task not in TASK_PROMPT_BUILDERS or not fields:
            continue

        prompt = TASK_PROMPT_BUILDERS[task](fields)
        gen = generators[task]
        response_type = "doc" if task == "code2doc" else "code"
        output_text = gen.generate(prompt, response_type=response_type)

        results[task].append({
            "index": i,
            "source": ds[i]["source"],
            "prompt_preview": prompt[:200],
            "generated_preview": output_text[:300],
            "reference_preview": ds[i]["text"][-300:],
        })

    summary = {task: len(samples) for task, samples in results.items()}
    report = {"summary": summary, "samples": results}

    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Wrote eval report to {out_path}")

    print("Multi-task eval summary:", summary)
    return report


def main():
    parser = argparse.ArgumentParser(description="Multi-task model smoke eval")
    parser.add_argument("--split", default="val", choices=["val", "train"])
    parser.add_argument("--max-per-task", type=int, default=5)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    run_eval(
        split=args.split,
        max_per_task=args.max_per_task,
        device=args.device,
        output=args.output,
    )


if __name__ == "__main__":
    main()
