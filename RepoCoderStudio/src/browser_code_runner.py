"""Guarded demo runner used by the browser-facing Gradio showcase.

The button lives in the browser, but execution happens on the notebook/app
host.  This is deliberately a small demonstration runner, not a security
boundary or a replacement for the Docker functional-evaluation harness.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Dict, Optional


_MAX_SOURCE_CHARS = 20_000
_MAX_OUTPUT_CHARS = 8_000

_PYTHON_ALLOWED_IMPORT_ROOTS = {
    "bisect",
    "collections",
    "datetime",
    "decimal",
    "fractions",
    "functools",
    "heapq",
    "itertools",
    "json",
    "math",
    "operator",
    "random",
    "re",
    "statistics",
    "string",
    "typing",
}
_PYTHON_BLOCKED_CALLS = {
    "__import__",
    "breakpoint",
    "compile",
    "delattr",
    "eval",
    "exec",
    "exit",
    "getattr",
    "globals",
    "input",
    "locals",
    "open",
    "quit",
    "setattr",
    "vars",
}
_PYTHON_BLOCKED_ATTRIBUTES = {
    "connect",
    "fork",
    "kill",
    "open",
    "popen",
    "remove",
    "rename",
    "replace",
    "rmdir",
    "socket",
    "system",
    "unlink",
}
_JAVA_BLOCKED_PATTERNS = (
    r"\bRuntime\s*\.\s*getRuntime\b",
    r"\bProcessBuilder\b",
    r"\bSystem\s*\.\s*(exit|setSecurityManager)\b",
    r"\b(java\.io|java\.nio\.file|java\.net|javax\.net)\b",
    r"\b(ClassLoader|URLClassLoader|MethodHandles|setAccessible)\b",
    r"\bClass\s*\.\s*forName\b",
    r"\bjava\.lang\.reflect\b",
)


def _result(status: str, message: str, **extra) -> Dict[str, object]:
    return {"status": status, "message": message, **extra}


def _bounded(value: Optional[str]) -> str:
    text = str(value or "")
    if len(text) <= _MAX_OUTPUT_CHARS:
        return text
    return text[:_MAX_OUTPUT_CHARS] + "\n...[output truncated]"


def _minimal_env() -> Dict[str, str]:
    keep = ("PATH", "SYSTEMROOT", "WINDIR", "JAVA_HOME", "LANG", "LC_ALL")
    return {key: os.environ[key] for key in keep if key in os.environ}


def format_code_for_display(language: Optional[str], source: str) -> str:
    """Return readable UI text without changing the validated raw artifact."""

    code = str(source or "").strip()
    if language != "java" or not code or '"""' in code:
        return code
    return _format_java_for_display(code)


def _format_java_for_display(source: str) -> str:
    """Conservatively expand compact Java into indented display lines."""

    lines = []
    current = []
    indent = 0
    paren_depth = 0
    state = "code"
    quote = ""
    escaped = False
    index = 0

    def emit():
        text = "".join(current).strip()
        current.clear()
        if text:
            lines.append("    " * max(0, indent) + text)

    while index < len(source):
        char = source[index]
        nxt = source[index + 1] if index + 1 < len(source) else ""

        if state in {"string", "char"}:
            current.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                state = "code"
            index += 1
            continue

        if state == "line_comment":
            current.append(char)
            if char == "\n":
                emit()
                state = "code"
            index += 1
            continue

        if state == "block_comment":
            current.append(char)
            if char == "*" and nxt == "/":
                current.append(nxt)
                index += 2
                state = "code"
                continue
            if char == "\n":
                emit()
            index += 1
            continue

        if char == "/" and nxt == "/":
            if current and not current[-1].isspace():
                current.append(" ")
            current.extend((char, nxt))
            state = "line_comment"
            index += 2
            continue
        if char == "/" and nxt == "*":
            if current and not current[-1].isspace():
                current.append(" ")
            current.extend((char, nxt))
            state = "block_comment"
            index += 2
            continue
        if char in {'"', "'"}:
            quote = char
            state = "string" if char == '"' else "char"
            current.append(char)
            index += 1
            continue

        if char.isspace():
            if current and not current[-1].isspace():
                current.append(" ")
            index += 1
            continue
        if char == "(":
            paren_depth += 1
            current.append(char)
        elif char == ")":
            paren_depth = max(0, paren_depth - 1)
            current.append(char)
        elif char == "{":
            if current and not current[-1].isspace():
                current.append(" ")
            current.append("{")
            emit()
            indent += 1
        elif char == "}":
            emit()
            indent = max(0, indent - 1)
            current.append("}")
            lookahead = source[index + 1 :].lstrip()
            if lookahead and (lookahead[0].isalpha() or lookahead[0] == "_"):
                current.append(" ")
        elif char == ";":
            current.append(char)
            if paren_depth == 0:
                emit()
            else:
                current.append(" ")
        else:
            current.append(char)
        index += 1

    emit()
    return "\n".join(line.rstrip() for line in lines if line.strip())


class _PythonSafetyVisitor(ast.NodeVisitor):
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".", 1)[0]
            if root not in _PYTHON_ALLOWED_IMPORT_ROOTS:
                raise ValueError(f"import '{root}' is not allowed in the demo runner")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        root = str(node.module or "").split(".", 1)[0]
        if root not in _PYTHON_ALLOWED_IMPORT_ROOTS:
            raise ValueError(f"import '{root}' is not allowed in the demo runner")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in _PYTHON_BLOCKED_CALLS:
            raise ValueError(f"call '{node.func.id}' is not allowed in the demo runner")
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in _PYTHON_BLOCKED_ATTRIBUTES
        ):
            raise ValueError(
                f"attribute call '{node.func.attr}' is not allowed in the demo runner"
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr.startswith("__"):
            raise ValueError("dunder attribute access is not allowed in the demo runner")
        self.generic_visit(node)


class DemoCodeRunner:
    """Compile or execute generated Python/Java with strict demo limits."""

    def __init__(self, timeout_seconds: int = 4, compile_timeout_seconds: int = 12):
        self.timeout_seconds = max(1, int(timeout_seconds))
        self.compile_timeout_seconds = max(
            self.timeout_seconds,
            int(compile_timeout_seconds),
        )

    def run(self, language: str, source: str) -> Dict[str, object]:
        code = str(source or "").strip()
        if not code:
            return _result("NOT_RUN", "There is no generated code to run.")
        if len(code) > _MAX_SOURCE_CHARS:
            return _result(
                "BLOCKED",
                f"Source exceeds the {_MAX_SOURCE_CHARS:,}-character demo limit.",
            )
        if language == "python":
            return self._run_python(code)
        if language == "java":
            return self._run_java(code)
        return _result(
            "NOT_APPLICABLE",
            "This task produces natural language, so there is no code to run.",
        )

    def _run_python(self, code: str) -> Dict[str, object]:
        try:
            tree = ast.parse(code)
            _PythonSafetyVisitor().visit(tree)
        except (SyntaxError, ValueError) as exc:
            return _result("BLOCKED", f"Python safety/parse check failed: {exc}")

        with tempfile.TemporaryDirectory(prefix="repocoder_ui_py_") as temp:
            source_path = Path(temp) / "snippet.py"
            source_path.write_text(code, encoding="utf-8")
            try:
                completed = subprocess.run(
                    [sys.executable, "-I", "-S", str(source_path)],
                    cwd=temp,
                    env=_minimal_env(),
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                return _result(
                    "TIMEOUT",
                    f"Python execution exceeded {self.timeout_seconds} seconds.",
                )
            except OSError as exc:
                return _result("NOT_FEASIBLE", f"Python could not be started: {exc}")

        stdout = _bounded(completed.stdout).strip()
        stderr = _bounded(completed.stderr).strip()
        if completed.returncode != 0:
            return _result(
                "RUNTIME_ERROR",
                stderr or f"Python exited with code {completed.returncode}.",
                stdout=stdout,
            )
        return _result(
            "PASS",
            stdout or "Execution completed successfully (no stdout was produced).",
        )

    def _run_java(self, code: str) -> Dict[str, object]:
        for pattern in _JAVA_BLOCKED_PATTERNS:
            if re.search(pattern, code):
                return _result(
                    "BLOCKED",
                    "Java source uses file, network, process, reflection or exit APIs "
                    "that are disabled in the demo runner.",
                )

        class_match = re.search(
            r"\bpublic\s+(?:final\s+)?class\s+([A-Za-z_$][\w$]*)",
            code,
        ) or re.search(r"\bclass\s+([A-Za-z_$][\w$]*)", code)
        if not class_match:
            return _result("COMPILE_ERROR", "No Java class declaration was found.")

        class_name = class_match.group(1)
        package_match = re.search(
            r"^\s*package\s+([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*)\s*;",
            code,
            flags=re.MULTILINE,
        )
        fqcn = f"{package_match.group(1)}.{class_name}" if package_match else class_name
        has_main = bool(
            re.search(
                r"\bstatic\s+void\s+main\s*\(\s*String(?:\s*\[\s*\]|\.\.\.)",
                code,
            )
        )

        with tempfile.TemporaryDirectory(prefix="repocoder_ui_java_") as temp:
            source_path = Path(temp) / f"{class_name}.java"
            source_path.write_text(code, encoding="utf-8")
            try:
                compiled = subprocess.run(
                    ["javac", "-encoding", "UTF-8", "-d", temp, str(source_path)],
                    cwd=temp,
                    env=_minimal_env(),
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.compile_timeout_seconds,
                    check=False,
                )
            except FileNotFoundError:
                return _result(
                    "NOT_FEASIBLE",
                    "javac is unavailable. Install a JDK in the Colab/runtime host.",
                )
            except subprocess.TimeoutExpired:
                return _result(
                    "TIMEOUT",
                    "Java compilation exceeded "
                    f"{self.compile_timeout_seconds} seconds.",
                )

            if compiled.returncode != 0:
                return _result(
                    "COMPILE_ERROR",
                    _bounded(compiled.stderr).strip() or "javac failed.",
                )
            if not has_main:
                return _result(
                    "COMPILE_PASS",
                    "Java compiled successfully. No main(String[] args) method was "
                    "present, so there was nothing to execute.",
                )

            try:
                executed = subprocess.run(
                    ["java", "-Xms16m", "-Xmx128m", "-cp", temp, fqcn],
                    cwd=temp,
                    env=_minimal_env(),
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout_seconds,
                    check=False,
                )
            except FileNotFoundError:
                return _result(
                    "NOT_FEASIBLE",
                    "The Java runtime is unavailable even though javac was found.",
                )
            except subprocess.TimeoutExpired:
                return _result(
                    "TIMEOUT",
                    f"Java execution exceeded {self.timeout_seconds} seconds.",
                )

        stdout = _bounded(executed.stdout).strip()
        stderr = _bounded(executed.stderr).strip()
        if executed.returncode != 0:
            return _result(
                "RUNTIME_ERROR",
                stderr or f"Java exited with code {executed.returncode}.",
                stdout=stdout,
            )
        return _result(
            "PASS",
            stdout or "Java ran successfully (no stdout was produced).",
        )
