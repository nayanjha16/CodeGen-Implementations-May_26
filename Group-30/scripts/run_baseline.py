"""End-to-end baseline runner — the spine the whole team plugs into.

  python scripts/run_baseline.py --smoke
      Runs the FULL pipeline (problem -> completion -> sandbox -> pass@k -> report) on a fixed
      fake "model" with NO dependencies and NO model download. Proves the wiring works and shows
      every teammate exactly where their piece slots in.

  python scripts/run_baseline.py --model Salesforce/codegen-350M-mono --n 5
      Real run: loads the model (needs transformers+torch+a GPU; do this on Kaggle/Colab),
      generates n samples per HumanEval-X problem, executes them, reports pass@1/pass@k.

The seams (marked TODO-OWNER) are deliberately thin so Lohitha/Tushnik can replace the stubs
without touching the harness.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.eval.passk import pass_at_k
from src.sandbox.execution import Outcome, check_correctness


# --- a couple of HumanEval-shaped problems so --smoke needs no dataset download -----------------
# TODO-OWNER(Lohitha): replace load_problems() with datasets.load_dataset("THUDM/humaneval-x", "python")
SMOKE_PROBLEMS = [
    {
        "task_id": "smoke/return_n",
        "prompt": "def return_n(n):\n    \"\"\"Return n unchanged.\"\"\"\n",
        "test": "def check(candidate):\n    assert candidate(3) == 3\n    assert candidate(-1) == -1\n",
        "entry_point": "return_n",
    },
    {
        "task_id": "smoke/add",
        "prompt": "def add(a, b):\n    \"\"\"Return a + b.\"\"\"\n",
        "test": "def check(candidate):\n    assert candidate(2, 3) == 5\n",
        "entry_point": "add",
    },
]


def load_problems(smoke: bool):
    if smoke:
        return SMOKE_PROBLEMS
    # TODO-OWNER(Lohitha): wire the real dataset here.
    from datasets import load_dataset
    ds = load_dataset("THUDM/humaneval-x", "python", split="test")
    return [
        {"task_id": r["task_id"], "prompt": r["prompt"], "test": r["test"],
         "entry_point": r["entry_point"]}
        for r in ds
    ]


def fake_generate(problem: dict, n: int):
    """Stand-in 'model': returns one correct body and (n-1) plausibly-wrong ones, so --smoke
    exercises both the PASS and FAIL paths of the sandbox.
    TODO-OWNER(Tushnik): replace with real model.generate() using configs/decoding.yaml."""
    ep = problem["entry_point"]
    correct = {"return_n": "    return n\n", "add": "    return a + b\n"}[ep]
    wrong = {"return_n": "    return n + 1\n", "add": "    return a - b\n"}[ep]
    return [correct] + [wrong] * (n - 1)


def real_generate(problem, n, model, tokenizer, cfg):
    """TODO-OWNER(Tushnik): batch-generate n completions with the locked decode config."""
    raise NotImplementedError("Real generation lands in src/model/. Use --smoke for now.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="run the no-dependency pipeline demo")
    ap.add_argument("--model", default="Salesforce/codegen-350M-mono")
    ap.add_argument("--n", type=int, default=5, help="samples per problem")
    ap.add_argument("--out", default="results/baseline.json")
    args = ap.parse_args()

    problems = load_problems(args.smoke)
    print(f"Loaded {len(problems)} problems ({'SMOKE' if args.smoke else args.model})\n")

    per_problem_correct = []
    failure_modes = Counter()
    records = []

    for prob in problems:
        completions = fake_generate(prob, args.n) if args.smoke else real_generate(prob, args.n, None, None, None)
        c = 0
        for i, comp in enumerate(completions):
            res = check_correctness(prob, comp, completion_id=i)
            if res.passed:
                c += 1
            else:
                failure_modes[res.outcome.value] += 1
            records.append({"task_id": prob["task_id"], "completion_id": i,
                            "outcome": res.outcome.value, "runtime_s": round(res.runtime_s, 3)})
        per_problem_correct.append(c)
        print(f"  {prob['task_id']:<22} {c}/{args.n} correct")

    p1 = pass_at_k(args.n, per_problem_correct, 1)
    summary = {"model": "SMOKE" if args.smoke else args.model, "n": args.n,
               "num_problems": len(problems), "pass@1": round(p1, 4),
               "failure_modes": dict(failure_modes)}
    if args.n >= 5:
        summary["pass@5"] = round(pass_at_k(args.n, per_problem_correct, 5), 4)

    print("\n=== BASELINE SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print("failure-mode breakdown (gate V10):", dict(failure_modes))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "records": records}, f, indent=2)
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
