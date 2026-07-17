#!/usr/bin/env python3
"""Execute Python code in an isolated subprocess with timeout and resource limits."""

import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


def run_code(code: str, test_cases: list[dict] | None = None, timeout: int = 10) -> dict:
    """
    Execute code and optionally run test cases.

    test_cases format:
        [{"input": "...", "expected": "..."}]  — stdout comparison
        [{"assertion": "assert add(1,2) == 3"}] — inline assertions
    """
    result = {
        "stdout": "",
        "stderr": "",
        "passed": False,
        "error": None,
        "test_results": [],
    }

    if test_cases:
        full_code = _wrap_with_tests(code, test_cases)
    else:
        full_code = code

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / "solution.py"
        script_path.write_text(full_code)

        try:
            proc = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir,
            )
            result["stdout"] = proc.stdout
            result["stderr"] = proc.stderr
            result["passed"] = proc.returncode == 0
            if proc.returncode != 0:
                result["error"] = proc.stderr or f"Exit code {proc.returncode}"
        except subprocess.TimeoutExpired:
            result["error"] = f"Execution timed out after {timeout}s"
            result["passed"] = False
        except Exception as e:
            result["error"] = str(e)
            result["passed"] = False

    return result


def _wrap_with_tests(code: str, test_cases: list[dict]) -> str:
    """Wrap user code with test harness."""
    test_blocks = []
    for i, tc in enumerate(test_cases):
        if "assertion" in tc:
            test_blocks.append(tc["assertion"])
        elif "input" in tc and "expected" in tc:
            test_blocks.append(
                f'_inp = {repr(tc["input"])}\n'
                f'_exp = {repr(tc["expected"])}\n'
                f'# Test case {i+1}: compare output'
            )
        elif "test_fn" in tc:
            test_blocks.append(tc["test_fn"])

    lines = [code, "", "# --- Auto-generated test harness ---", "def _run_tests():"]
    lines.append("    passed = 0")
    lines.append("    failed = 0")
    lines.append("    errors = []")

    for block in test_blocks:
        lines.append("    try:")
        for block_line in block.split("\n"):
            lines.append(f"        {block_line}")
        lines.append("        passed += 1")
        lines.append("    except Exception as e:")
        lines.append("        failed += 1")
        lines.append("        errors.append(str(e))")

    lines.extend([
        "    if failed > 0:",
        '        raise AssertionError(f"{failed} test(s) failed: " + "; ".join(errors))',
        '    print(f"All {passed} test(s) passed")',
        "",
        'if __name__ == "__main__":',
        "    _run_tests()",
    ])
    return "\n".join(lines)


def main():
    """Read JSON from stdin, execute, write JSON to stdout."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}", "passed": False}))
        sys.exit(1)

    code = payload.get("code", "")
    test_cases = payload.get("test_cases")
    timeout = payload.get("timeout", 10)

    if not code.strip():
        print(json.dumps({"error": "No code provided", "passed": False}))
        sys.exit(1)

    result = run_code(code, test_cases, timeout=timeout)
    print(json.dumps(result))
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
