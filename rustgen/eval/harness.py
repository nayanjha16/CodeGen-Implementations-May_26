"""Compile-and-test runner: code + tests -> rustc -> run the binary."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HarnessResult:
    passed: bool
    stage: str        # "compile" | "run" | "ok"
    stderr: str = ""


def run_rust(code: str, tests: str, timeout: int = 30) -> HarnessResult:
    """Compile ``code`` followed by ``tests`` (a fn main with asserts) and run it."""
    if shutil.which("rustc") is None:
        raise RuntimeError(
            "rustc not found on PATH. Install Rust (https://rustup.rs) to use "
            "the evaluation harness."
        )
    with tempfile.TemporaryDirectory(prefix="rustgen-") as tmp:
        source = Path(tmp) / "main.rs"
        binary = Path(tmp) / "main"
        source.write_text(code.rstrip() + "\n\n" + tests.strip() + "\n")

        try:
            compile_proc = subprocess.run(
                ["rustc", "--edition", "2021", str(source), "-o", str(binary)],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return HarnessResult(False, "compile", f"compilation timed out after {timeout}s")
        if compile_proc.returncode != 0:
            return HarnessResult(False, "compile", compile_proc.stderr)

        try:
            run_proc = subprocess.run(
                [str(binary)], capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            return HarnessResult(False, "run", f"execution timed out after {timeout}s")
        if run_proc.returncode != 0:
            return HarnessResult(False, "run", run_proc.stderr)

        return HarnessResult(True, "ok")
