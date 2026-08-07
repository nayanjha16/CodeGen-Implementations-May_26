"""LangChain tools: sandbox execution, RAG retrieve, AST parse, repo helpers."""

from __future__ import annotations

import ast
import json
import re
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
        return _syntax_error_summary(code, e)

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


_INCOMPLETE_EXPR_RE = re.compile(
    r"(?P<trailing>[+\-*/%@^|&~]|//|<<|>>)\s*$"
    r"|(?P<before_paren>[+\-*/%@^|&~]|//|<<|>>)\s*\)"
)


def _incomplete_expression_hint(offending: str) -> str:
    """Return a hint when a line ends with a dangling operator."""
    match = _INCOMPLETE_EXPR_RE.search(offending)
    if not match:
        return ""
    op = match.group("trailing") or match.group("before_paren")
    return f" (incomplete expression: add the missing operand after {op!r})"


def _syntax_error_summary(code: str, exc: SyntaxError) -> str:
    """Describe a syntax error with the offending line so a retry is actionable.

    Without the source line every failure looks like the same generic
    "invalid syntax at line 1", which hides the real cause (leftover markdown
    fences, Java that leaked through, or prose instead of code).
    """
    lines = (code or "").splitlines()
    lineno = exc.lineno or 0
    offending = lines[lineno - 1].strip() if 1 <= lineno <= len(lines) else ""

    summary = f"SyntaxError: {exc.msg} at line {lineno}"
    if offending:
        summary += f": {offending[:120]!r}"

    if offending.startswith("```") or offending.lower() in ("python", "py"):
        summary += " (leftover markdown fence, not Python)"
    elif any(m in code for m in ("public class", "public static", "System.out.print")):
        summary += " (looks like Java, not Python)"
    else:
        summary += _incomplete_expression_hint(offending)
    return summary


def _java_structure_summary(code: str) -> str:
    lines = [ln.strip() for ln in code.splitlines() if ln.strip()]
    classes = [ln for ln in lines if "class " in ln][:10]
    methods = [ln for ln in lines if "(" in ln and ")" in ln and "{" in ln][:15]
    return f"java_classes≈{classes}; java_methods≈{methods}"


@tool
def list_repo_source_files(
    repo_root: str,
    max_files: int = 20,
    extensions: str = ".java,.py",
) -> str:
    """List Java and Python source files under a repository root."""
    root = Path(repo_root)
    if not root.exists():
        return json.dumps({"error": f"repo not found: {repo_root}", "files": []})

    exts = {e.strip().lower() for e in extensions.split(",") if e.strip()}
    if not exts:
        exts = {".java", ".py"}

    files: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in exts:
            continue
        files.append(str(path.resolve()))
        if len(files) >= max_files:
            break
    return json.dumps({"files": files})


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


@tool
def list_java_files(path: str, recursive: bool = True, max_files: int = 5) -> str:
    """List Java files under a path (file or directory)."""
    p = Path(path)
    if not p.exists():
        return json.dumps({"error": f"path not found: {path}", "files": []})
    
    if p.is_file():
        return json.dumps({"files": [str(p.resolve())]})
    
    pattern = "**/*.java" if recursive else "*.java"
    files = sorted([str(f.resolve()) for f in p.glob(pattern) if f.is_file()])
    return json.dumps({"files": files[:max_files]})


@tool
def read_text_file(path: str) -> str:
    """Read UTF-8 source from a file."""
    p = Path(path)
    if not p.exists():
        return f"(missing file: {path})"
    return p.read_text(encoding="utf-8")


@tool
def write_text_file(path: str, content: str) -> str:
    """Write text content to a file, creating parent directories if needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Successfully wrote {len(content)} bytes to {path}"


_RETURN_VALUE_PREFIXES = ("get_", "compute_", "calculate_", "to_", "fetch_", "read_")

_JAVA_LEAKAGE_RE = re.compile(
    r"\b(null|boolean|void)\b|"
    r"\bnew\s+[A-Z]\w*\s*\(|"
    r"System\.out\.|"
    r"public\s+(static\s+)?(class|void|int|String)\b"
)


def _annotation_is_none(node: ast.expr | None) -> bool:
    if node is None:
        return True
    if isinstance(node, ast.Constant) and node.value is None:
        return True
    if isinstance(node, ast.Name) and node.id in ("None", "NoneType"):
        return True
    return False


def _function_has_return(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Return):
            return True
    return False


def _body_is_only_pass(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    body = node.body
    if len(body) != 1:
        return False
    stmt = body[0]
    return isinstance(stmt, ast.Pass) or (
        isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Constant)
        and stmt.value.value is Ellipsis
    )


def _looks_like_value_getter(name: str) -> bool:
    lower = name.lower()
    return any(lower.startswith(p) for p in _RETURN_VALUE_PREFIXES)


def _semantic_python_issues(code: str) -> list[str]:
    """Lightweight AST checks beyond syntax (missing return, Java leakage)."""
    issues: list[str] = []
    if _JAVA_LEAKAGE_RE.search(code):
        issues.append(
            "Semantic: possible Java syntax leakage (null/boolean/void/System.out/public class)"
        )

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return issues

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        name = node.name
        has_return = _function_has_return(node)
        only_pass = _body_is_only_pass(node)

        if node.returns is not None and not _annotation_is_none(node.returns):
            if not has_return:
                issues.append(
                    f"Semantic: function `{name}` has non-None return annotation but no return statement"
                )
        elif only_pass and _looks_like_value_getter(name):
            issues.append(
                f"Semantic: function `{name}` looks like it should return a value but body is only pass"
            )
    return issues


def _run_pyflakes(code: str) -> str:
    from pyflakes.api import check
    from pyflakes.reporter import Reporter
    import io

    out = io.StringIO()
    err = io.StringIO()
    reporter = Reporter(out, err)
    check(code, "<string>", reporter)
    out_val = out.getvalue().strip()
    err_val = err.getvalue().strip()
    if out_val or err_val:
        return f"Pyflakes validation errors:\n{out_val}\n{err_val}".strip()
    return ""


@tool
def validate_python_code(code: str) -> str:
    """Runs ast.parse, semantic heuristics, and pyflakes. Returns 'OK' or error trace."""
    try:
        ast.parse(code)
    except SyntaxError as e:
        return _syntax_error_summary(code, e)

    semantic = _semantic_python_issues(code)
    if semantic:
        return "Semantic validation errors:\n" + "\n".join(semantic)

    try:
        flake_err = _run_pyflakes(code)
        if flake_err:
            return flake_err
    except ImportError:
        pass

    return "OK"


@tool
def find_local_java_dependencies(java_code: str, repo_root: str) -> str:
    """Regex scan for imports or same-package usage, returning paths to other .java files."""
    root = Path(repo_root)
    if not root.exists():
        return json.dumps({"error": f"repo not found: {repo_root}", "dependencies": []})
        
    import_pattern = re.compile(r"import\s+([\w\.]+);")
    imports = import_pattern.findall(java_code)
    
    class_names = [imp.split(".")[-1] for imp in imports if not imp.startswith("java.")]
    
    usage_pattern = re.compile(r"\b([A-Z][a-zA-Z0-9_]*)\b")
    used_classes = usage_pattern.findall(java_code)
    
    all_potential_classes = set(class_names + used_classes)
    
    common = {
        "String", "Integer", "Long", "Double", "Boolean", "Object", "List", 
        "Map", "Set", "Collection", "System", "Exception", "RuntimeException", 
        "IllegalArgumentException", "Math", "Override", "Override", "Test", 
        "Before", "After"
    }
    targets = [c for c in all_potential_classes if c not in common]
    
    found_paths = []
    all_java = list(root.rglob("*.java"))
    for target in targets:
        for jf in all_java:
            if jf.stem == target:
                found_paths.append(str(jf.resolve()))
                break
                
    unique_paths = list(set(found_paths))
    return json.dumps({"dependencies": unique_paths[:5]})

