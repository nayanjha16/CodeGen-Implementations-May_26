"""LangChain tools: sandbox execution, RAG retrieve, AST parse, repo helpers."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "sandbox"))

_rag_cache: dict[str, Any] = {}


@tool
def run_python(code: str, timeout: int = 10) -> str:
    """Execute Python code in an isolated sandbox and return JSON results."""
    from runner import run_code

    result = run_code(code, test_cases=None, timeout=timeout)
    return json.dumps(
        {
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "passed": result.get("passed", False),
            "error": result.get("error"),
            "exit_ok": bool(result.get("passed")),
        }
    )


def run_python_dict(code: str, timeout: int = 10) -> dict[str, Any]:
    """Same as run_python tool but returns a dict (used by graph nodes)."""
    raw = run_python.invoke({"code": code, "timeout": timeout})
    return json.loads(raw)


@tool
def retrieve_examples(query: str, task: str = "nl2py", top_k: int = 3) -> str:
    """Retrieve few-shot code examples via the project RAG pipeline."""
    try:
        rag = _get_rag(task)
        if rag is None or getattr(rag, "index", None) is None:
            return ""
        # Prefer build_prompt few-shot section when available
        if hasattr(rag, "retrieve"):
            hits = rag.retrieve(query)[:top_k]
            if not hits:
                return ""
            parts = []
            for i, h in enumerate(hits, 1):
                parts.append(f"### Retrieved example {i}:\n{json.dumps(h, default=str)[:800]}")
            return "\n\n".join(parts)
        return ""
    except Exception as e:
        return f"(RAG unavailable: {e})"


def _get_rag(task: str):
    if task in _rag_cache:
        return _rag_cache[task]
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "inference"))
        from rag_pipeline import RAGPipeline

        rag = RAGPipeline(task=task)
        _rag_cache[task] = rag
        return rag
    except Exception:
        _rag_cache[task] = None
        return None


@tool
def parse_ast(code: str, language: str = "python") -> str:
    """Parse code and return a short AST / structure summary for repair prompts."""
    language = (language or "python").lower()
    if language != "python":
        # Lightweight fallback for Java: surface class/method signatures via regex-ish scan
        return _java_structure_summary(code)
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"SyntaxError: {e.msg} at line {e.lineno}"

    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    imports = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            imports.extend(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            imports.append(n.module or "")
    return (
        f"classes={classes}; functions={funcs}; imports={imports}; "
        f"num_nodes={sum(1 for _ in ast.walk(tree))}"
    )


def _java_structure_summary(code: str) -> str:
    lines = [ln.strip() for ln in code.splitlines() if ln.strip()]
    classes = [ln for ln in lines if "class " in ln][:10]
    methods = [ln for ln in lines if "(" in ln and ")" in ln and "{" in ln][:15]
    return f"java_classes≈{classes}; java_methods≈{methods}"


@tool
def list_repo_files(repo_root: str) -> str:
    """List Python files under a toy repository root."""
    root = Path(repo_root)
    if not root.exists():
        return json.dumps({"error": f"repo not found: {repo_root}", "files": []})
    files = sorted(str(p.relative_to(root)) for p in root.rglob("*.py") if p.is_file())
    return json.dumps({"files": files})


@tool
def read_repo_file(repo_root: str, relative_path: str) -> str:
    """Read a file from the toy repository."""
    path = Path(repo_root) / relative_path
    if not path.exists():
        return f"(missing file: {relative_path})"
    return path.read_text(encoding="utf-8")
