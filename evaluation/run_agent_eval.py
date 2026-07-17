#!/usr/bin/env python3
"""Evaluate LangGraph agent vs single-shot NL→Java→Python pipeline.

Usage:
  python evaluation/run_agent_eval.py [--limit N] [--use-rag] [--max-retries 3]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "inference"))
sys.path.insert(0, str(PROJECT_ROOT / "data" / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "sandbox"))


def _single_shot(prompt: str, generator) -> dict:
    from prompt_templates import format_java2py_inference, format_nl2java_inference
    from runner import run_code

    java = generator.generate(format_nl2java_inference(prompt))
    python = generator.generate(format_java2py_inference(java))
    result = run_code(python)
    return {
        "java_code": java,
        "python_code": python,
        "exit_ok": bool(result.get("passed")),
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
    }


def main():
    parser = argparse.ArgumentParser(description="Agent vs single-shot eval")
    parser.add_argument("--limit", type=int, default=5, help="Max problems from pack")
    parser.add_argument("--use-rag", action="store_true")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument(
        "--problem-ids",
        nargs="*",
        default=None,
        help="Optional subset of problem ids",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "evaluation" / "agent_eval_results.json",
    )
    args = parser.parse_args()

    from agent.graph import solve
    from agent.llms import set_codegen_generator
    from agent.problems import load_problem_pack
    from generator import load_generator

    gen = load_generator("java2py")
    set_codegen_generator(gen)

    problems = load_problem_pack()
    if args.problem_ids:
        problems = [p for p in problems if p["id"] in args.problem_ids]
    problems = problems[: args.limit]

    rows = []
    agent_yes = 0
    shot_ok = 0
    for prob in problems:
        if not prob.get("nl_prompt") and not prob.get("java_code"):
            continue
        print(f"\n=== {prob['id']} ===")
        agent = solve(
            prob.get("nl_prompt", ""),
            java_code=prob.get("java_code", ""),
            unit=prob.get("unit", "function"),
            use_rag=bool(prob.get("use_rag", args.use_rag)),
            max_retries=args.max_retries,
            pattern=prob.get("pattern", ""),
            repo_root=prob.get("repo_root", ""),
            input_type=prob.get("input_type"),
        )
        yes = bool(agent.get("judge_yes"))
        agent_yes += int(yes)
        print(f"agent judge_yes={yes} attempts={agent.get('attempts')} route={agent.get('route')}")

        shot = None
        if prob.get("nl_prompt"):
            shot = _single_shot(prob["nl_prompt"], gen)
            shot_ok += int(shot["exit_ok"])
            print(f"single_shot exit_ok={shot['exit_ok']}")

        rows.append(
            {
                "id": prob["id"],
                "agent_judge_yes": yes,
                "agent_attempts": agent.get("attempts"),
                "agent_route": agent.get("route"),
                "agent_stderr": (agent.get("stderr") or "")[:300],
                "single_shot_exit_ok": None if shot is None else shot["exit_ok"],
            }
        )

    n = max(len(rows), 1)
    summary = {
        "n": len(rows),
        "agent_judge_yes_rate": agent_yes / n,
        "single_shot_exit_ok_rate": shot_ok / n if any(r.get("single_shot_exit_ok") is not None for r in rows) else None,
        "rows": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nWrote {args.out}")
    print(json.dumps({k: summary[k] for k in ("n", "agent_judge_yes_rate", "single_shot_exit_ok_rate")}, indent=2))


if __name__ == "__main__":
    main()
