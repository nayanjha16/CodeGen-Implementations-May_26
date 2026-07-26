#!/usr/bin/env python3
"""Run Stage 8 Docker integration tests (Chinook demo)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    env = dict(**{k: v for k, v in __import__("os").environ.items()})
    env["PYTHONPATH"] = str(REPO_ROOT)
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "agent/tests/test_integration_stage8.py",
        "-q",
    ]
    print("Running:", " ".join(cmd))
    return subprocess.call(cmd, cwd=str(REPO_ROOT), env=env)


if __name__ == "__main__":
    raise SystemExit(main())
