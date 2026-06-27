"""Gate V5 — sandbox correctness self-test.

A buggy sandbox is worse than no sandbox: it produces confidently-wrong accuracy numbers.
Before the harness is allowed to score any real model output, it must prove that:
  * every KNOWN-GOOD solution is reported PASSED, and
  * every KNOWN-BAD solution FAILS, and fails for the EXPECTED reason (right failure class).

Run: python tests/test_sandbox_gate_v5.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.sandbox.execution import Outcome, check_correctness

# A tiny battery of problems with a known-correct reference and a `check` function, in the
# HumanEval shape: prompt (signature + docstring), test (defines check), entry_point.
PROBLEMS = {
    "add": {
        "task_id": "add",
        "prompt": "def add(a, b):\n    \"\"\"Return a + b.\"\"\"\n",
        "test": "def check(candidate):\n    assert candidate(2, 3) == 5\n    assert candidate(-1, 1) == 0\n",
        "entry_point": "add",
    },
    "is_even": {
        "task_id": "is_even",
        "prompt": "def is_even(n):\n    \"\"\"Return True iff n is even.\"\"\"\n",
        "test": "def check(candidate):\n    assert candidate(4) is True\n    assert candidate(7) is False\n",
        "entry_point": "is_even",
    },
}

# 20 known-GOOD completions (10 per problem, varied-but-correct).
GOOD = []
for _ in range(10):
    GOOD.append(("add", "    return a + b\n"))
    GOOD.append(("is_even", "    return n % 2 == 0\n"))
# add a couple of correct-but-stylistically-different ones to catch over-strict matching
GOOD[0] = ("add", "    return sum([a, b])\n")
GOOD[1] = ("is_even", "    return (n & 1) == 0\n")

# 20 known-BAD completions, each tagged with the failure class the sandbox MUST report.
BAD = [
    ("add", "    return a - b\n", Outcome.WRONG_OUTPUT),          # logic wrong
    ("add", "    return a +\n", Outcome.COMPILE_ERROR),          # syntax error
    ("add", "    return a + undefined_var\n", Outcome.RUNTIME_ERROR),  # NameError
    ("add", "    while True:\n        pass\n", Outcome.TIMEOUT),  # infinite loop
    ("add", "    x = [0] * (10**9 * 50)\n    return a + b\n", Outcome.OOM),  # runaway alloc
    ("add", "    raise ValueError('boom')\n", Outcome.RUNTIME_ERROR),
    ("add", "    return None\n", Outcome.WRONG_OUTPUT),
    ("add", "    import os\n    os.system('echo hacked')\n    return a + b\n", Outcome.RUNTIME_ERROR),  # blocked -> raises
    ("add", "    return a * b\n", Outcome.WRONG_OUTPUT),
    ("add", "  return a + b\n", Outcome.COMPILE_ERROR),           # bad indent
    ("is_even", "    return n % 2 == 1\n", Outcome.WRONG_OUTPUT),
    ("is_even", "    return\n", Outcome.WRONG_OUTPUT),            # returns None
    ("is_even", "    return n /// 2\n", Outcome.COMPILE_ERROR),
    ("is_even", "    return 1 / 0\n", Outcome.RUNTIME_ERROR),     # ZeroDivisionError
    ("is_even", "    for _ in iter(int, 1):\n        pass\n", Outcome.TIMEOUT),
    ("is_even", "    return bool(n)\n", Outcome.WRONG_OUTPUT),
    ("is_even", "    raise RuntimeError('x')\n", Outcome.RUNTIME_ERROR),
    ("is_even", "    return 'yes'\n", Outcome.WRONG_OUTPUT),
    ("is_even", "    return not n\n", Outcome.WRONG_OUTPUT),
    ("is_even", "    return [][5]\n", Outcome.RUNTIME_ERROR),  # IndexError (clean runtime error; assert would alias wrong_output)
]


def main() -> int:
    failures = []

    print(f"-- {len(GOOD)} known-good (must all PASS) --")
    good_pass = 0
    for i, (pid, comp) in enumerate(GOOD):
        r = check_correctness(PROBLEMS[pid], comp, timeout_s=5.0, memory_mb=512, completion_id=i)
        ok = r.passed
        good_pass += ok
        if not ok:
            print(f"  [FAIL] good#{i} {pid}: got {r.outcome.value} ({r.detail})")
            failures.append(("good", i, r.outcome))
    print(f"  {good_pass}/{len(GOOD)} good passed")

    print(f"-- {len(BAD)} known-bad (must all FAIL for the right reason) --")
    bad_ok = 0
    for i, (pid, comp, expected) in enumerate(BAD):
        r = check_correctness(PROBLEMS[pid], comp, timeout_s=5.0, memory_mb=256, completion_id=i)
        # must NOT pass, and the failure class must match expectation
        ok = (not r.passed) and (r.outcome == expected)
        bad_ok += ok
        if not ok:
            tag = "PASSED(!!)" if r.passed else f"{r.outcome.value} != {expected.value}"
            print(f"  [FAIL] bad#{i} {pid}: {tag} ({r.detail})")
            failures.append(("bad", i, r.outcome, expected))
    print(f"  {bad_ok}/{len(BAD)} bad failed correctly")

    if failures:
        print(f"\nGATE V5 FAILED: {len(failures)} fixture(s) wrong. Do NOT trust the harness yet.")
        return 1
    print("\nGATE V5 GREEN — sandbox is trustworthy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
