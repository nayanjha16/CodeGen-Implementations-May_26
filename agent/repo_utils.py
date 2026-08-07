"""Shared utilities for repo workspace agents (Ask / Code / Debug)."""

from __future__ import annotations

import ast
import json
import logging
import re
from pathlib import Path
from typing import Any

from agent.llms import codegen_generate
from agent.tools import (
    list_repo_source_files,
    parse_ast,
    read_text_file,
    run_python_dict,
    validate_python_code,
    write_text_file,
)
from data.scripts.prompt_templates import format_comment_inference

logger = logging.getLogger(__name__)

MAX_CHARS_PER_FILE = 4000
MAX_TOTAL_SOURCE_CHARS = 16000


def empty_session(repo_root: str = "") -> dict[str, Any]:
    return {
        "repo_root": repo_root,
        "state": "init",
        "pending_writes": [],
        "file_index": [],
        "sources_cache": [],
        "pending_files": [],
        "deps_found": [],
        "active_files": [],
        "migrated_py_paths": [],
        "scan_issues": {},
        "sources_from_rag": False,
    }


def clear_ask_session_context(session: dict[str, Any]) -> None:
    """Reset Ask Agent retrieval cache so the next question re-scans the repo."""
    session["state"] = "init"
    session["sources_cache"] = []
    session["sources_from_rag"] = False
    session["file_index"] = []
    session["active_files"] = []


def format_chat_history_block(
    history: list[dict[str, str]], max_turns: int = 3
) -> str:
    """Format recent chat turns for inclusion in an LLM prompt."""
    if not history:
        return ""
    recent = history[-(max_turns * 2) :]
    lines: list[str] = []
    for turn in recent:
        role = turn.get("role", "")
        if role not in ("user", "assistant"):
            continue
        label = "User" if role == "user" else "Assistant"
        content = str(turn.get("content", "")).strip()
        if not content or content in ("Thinking...", "Analyzing repository..."):
            continue
        if len(content) > 500:
            content = content[:500] + "..."
        lines.append(f"{label}: {content}")
    return "\n".join(lines)


def record_migrated_py(session: dict[str, Any], repo_root: str, py_path: str) -> None:
    """Track converted Python paths for Debug Agent batch fix."""
    root = resolve_repo_root(repo_root)
    try:
        rel = str(Path(py_path).resolve().relative_to(root))
    except ValueError:
        rel = Path(py_path).name
    paths = list(session.get("migrated_py_paths") or [])
    if rel not in paths:
        paths.append(rel)
    session["migrated_py_paths"] = paths


def resolve_repo_root(path: str) -> Path:
    root = Path(path.strip()).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Repo path not found: {path}")
    return root


def ensure_inside_repo(repo_root: Path, target: Path) -> Path:
    target = target.resolve()
    root = repo_root.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"Path {target} is outside repo root {root}") from exc
    return target


def resolve_in_repo(repo_root: str, user_path: str) -> Path:
    root = resolve_repo_root(repo_root)
    p = Path(user_path.strip())
    if not p.is_absolute():
        p = root / p
    return ensure_inside_repo(root, p)


class AmbiguousFileMatch(Exception):
    """Raised when a filename query matches multiple files in the repo."""

    def __init__(self, candidates: list[str]):
        self.candidates = candidates
        super().__init__(f"Ambiguous file match: {len(candidates)} candidates")


def _parse_extensions(extensions: str) -> set[str]:
    exts = {e.strip().lower() for e in extensions.split(",") if e.strip()}
    return exts or {".java", ".py"}


def list_repo_relative_files(
    repo_root: str,
    extensions: str = ".java,.py",
    max_files: int = 5000,
) -> list[str]:
    """List source files under repo root as relative paths (for UI autocomplete)."""
    root = resolve_repo_root(repo_root)
    exts = _parse_extensions(extensions)
    files: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in exts:
            continue
        try:
            files.append(str(path.resolve().relative_to(root)))
        except ValueError:
            continue
        if len(files) >= max_files:
            break
    return files


def search_repo_files(
    repo_root: str,
    query: str,
    extensions: str = ".java,.py",
    max_results: int = 50,
) -> list[str]:
    """Filter relative repo paths by basename or partial path (case-insensitive)."""
    q = query.strip().lstrip("@").lower()
    if not q:
        return list_repo_relative_files(repo_root, extensions=extensions)[:max_results]
    matches: list[str] = []
    for rel in list_repo_relative_files(repo_root, extensions=extensions):
        rel_lower = rel.lower()
        base = Path(rel).name.lower()
        if base == q or q in rel_lower or rel_lower.endswith(q):
            matches.append(rel)
            if len(matches) >= max_results:
                break
    return matches


def to_relative_repo_path(repo_root: str, abs_path: str | Path) -> str:
    root = resolve_repo_root(repo_root)
    p = Path(abs_path)
    if not p.is_absolute():
        p = root / p
    return str(p.resolve().relative_to(root))


def set_active_files(
    session_state: dict[str, Any], repo_root: str, abs_paths: list[str]
) -> None:
    """Store deduplicated relative paths in session."""
    seen: set[str] = set()
    rel_paths: list[str] = []
    for p in abs_paths:
        try:
            rel = to_relative_repo_path(repo_root, p)
        except (FileNotFoundError, ValueError):
            continue
        if rel not in seen:
            seen.add(rel)
            rel_paths.append(rel)
    session_state["active_files"] = rel_paths


def _infer_file_query_from_message(message: str) -> str | None:
    """Return a single basename token when the message likely names one file without extension."""
    text = message.strip()
    for prefix in ("migrate", "fix", "debug", "repair", "convert"):
        if text.lower().startswith(prefix):
            text = text[len(prefix) :].strip(" :—-")
    text = text.lstrip("@").strip()
    if not text or extract_file_refs(text):
        return None
    skip = {"the", "a", "an", "this", "that", "it", "please", "explain", "what", "how"}
    tokens = [t for t in re.split(r"\s+", text) if t and t.lower() not in skip]
    if len(tokens) != 1:
        return None
    token = tokens[0].strip("`'\"")
    if "/" in token or token.startswith("."):
        return token
    if "." in token:
        return None
    return token


def resolve_active_file_queries(
    repo_root: str,
    message: str,
    active_files: list[str],
    extensions: str = ".java,.py",
) -> tuple[list[str], str | None]:
    """Resolve from picker selection first, else message refs. Returns abs paths."""
    refs = extract_file_refs(message)
    queries: list[str] = []
    if active_files:
        queries = list(active_files)
    elif refs:
        queries = list(refs)
    else:
        inferred = _infer_file_query_from_message(message)
        if inferred:
            matches = search_repo_files(repo_root, inferred, extensions=extensions)
            if len(matches) == 1:
                queries = [matches[0]]
            elif len(matches) > 1:
                return [], format_disambiguation_message(matches)

    if not queries:
        return [], None

    abs_paths: list[str] = []
    missing: list[str] = []
    for q in queries:
        try:
            abs_paths.append(str(resolve_file_query(repo_root, q, extensions=extensions)))
        except AmbiguousFileMatch as exc:
            return [], format_disambiguation_message(exc.candidates)
        except FileNotFoundError:
            missing.append(q)

    if not abs_paths:
        if missing:
            return [], f"Could not find: {', '.join(missing)}"
        return [], None

    seen: set[str] = set()
    unique: list[str] = []
    for p in abs_paths:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique, None


def load_context_sources(
    repo_root: str,
    message: str,
    active_files: list[str],
    max_files: int = 20,
    extensions: str = ".java,.py",
) -> tuple[list[dict[str, str]], list[str], str | None]:
    """Load sources for picker selection and/or message file refs.

    Returns (sources, absolute_paths, error_message).
    """
    target_paths, err = resolve_active_file_queries(
        repo_root, message, active_files, extensions=extensions
    )
    if err:
        return [], [], err
    if target_paths:
        sources = read_repo_sources(repo_root, target_paths, include_ast=False)
        return sources, target_paths, None
    if active_files or extract_file_refs(message):
        return [], [], "Could not load the selected file(s)."
    files = index_repo_files(repo_root, max_files=max_files)
    if not files:
        return [], [], f"No `.java` or `.py` files found under `{repo_root}`."
    sources = read_repo_sources(repo_root, files, include_ast=False)
    return sources, files, None


def resolve_active_file_paths(
    repo_root: str,
    message: str,
    active_files: list[str],
    extensions: str = ".java,.py",
) -> tuple[list[str], str | None]:
    """Resolve active context to absolute paths (picker + message refs)."""
    return resolve_active_file_queries(
        repo_root, message, active_files, extensions=extensions
    )


def format_active_files_html(active_files: list[str]) -> str:
    if not active_files:
        return ""
    chips = " ".join(f'<span class="file-chip">{f}</span>' for f in active_files)
    return f'<div class="file-context">{chips}</div>'


def format_disambiguation_message(candidates: list[str]) -> str:
    lines = [
        "Multiple files match. Please mention the full path in chat:\n"
    ]
    for i, path in enumerate(candidates[:20], start=1):
        lines.append(f"{i}. `{path}`")
    if len(candidates) > 20:
        lines.append(f"... (+{len(candidates) - 20} more)")
    return "\n".join(lines)


def resolve_file_query(
    repo_root: str,
    query: str,
    extensions: str = ".java,.py",
) -> Path:
    """Resolve a user file query to an absolute path inside the repo.

    Supports explicit relative paths (``src/Foo.java``) and basename-only
    lookups (``Foo.java``) via recursive search.
    """
    root = resolve_repo_root(repo_root)
    q = query.strip().lstrip("@")
    if not q:
        raise FileNotFoundError("No file specified.")

    exts = _parse_extensions(extensions)

    if "/" in q or q.startswith("."):
        candidate = root / q
        if candidate.exists():
            return ensure_inside_repo(root, candidate)

    q_name = Path(q).name
    if Path(q_name).suffix.lower() not in exts:
        # Allow queries without extension only when unambiguous among known exts.
        pass

    matches: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in exts:
            continue
        if path.name.lower() == q_name.lower() or path.name.lower() == q.lower():
            matches.append(path.resolve())

    if not matches:
        raise FileNotFoundError(
            f"No `{q}` found under `{root}`. "
            "Try a relative path like `src/main/Foo.java` or use the file picker."
        )

    if len(matches) == 1:
        return ensure_inside_repo(root, matches[0])

    rel_paths = sorted(
        str(m.relative_to(root)) for m in matches
    )
    raise AmbiguousFileMatch(rel_paths)


def index_repo_files(repo_root: str, max_files: int = 20) -> list[str]:
    raw = list_repo_source_files.invoke(
        {"repo_root": repo_root, "max_files": max_files, "extensions": ".java,.py"}
    )
    try:
        data = json.loads(raw)
    except Exception:
        return []
    if "error" in data:
        return []
    return data.get("files", [])


def _source_language(file_path: str) -> str:
    lower = str(file_path).lower()
    if lower.endswith(".java"):
        return "java"
    if lower.endswith((".md", ".txt", ".rst")):
        return "markdown"
    return "python"


def read_repo_sources(
    repo_root: str,
    files: list[str],
    max_chars_per_file: int = MAX_CHARS_PER_FILE,
    max_total_chars: int = MAX_TOTAL_SOURCE_CHARS,
    include_ast: bool = True,
) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    if not files:
        return entries

    # Split the total budget evenly so every selected file gets into the prompt.
    per_file_limit = min(
        max_chars_per_file,
        max(max_total_chars // len(files), 400),
    )
    root = resolve_repo_root(repo_root)
    for fpath in files:
        content = read_text_file.invoke({"path": fpath})
        if content.startswith("(missing"):
            continue
        snippet = content[:per_file_limit]
        if len(content) > per_file_limit:
            snippet += "\n... (truncated)"
        lang = _source_language(fpath)
        ast_summary = ""
        if include_ast and lang in ("java", "python"):
            ast_summary = parse_ast.invoke({"code": snippet, "language": lang})
            if len(ast_summary) > 600:
                ast_summary = ast_summary[:600] + "..."
        try:
            rel = str(Path(fpath).resolve().relative_to(root))
        except ValueError:
            rel = Path(fpath).name
        entries.append(
            {
                "path": fpath,
                "name": rel,
                "language": lang,
                "snippet": snippet,
                "ast_summary": ast_summary,
            }
        )
    return entries


def format_sources_block(
    sources: list[dict[str, str]], *, for_doc: bool = False
) -> str:
    parts: list[str] = []
    for s in sources:
        if for_doc:
            parts.append(
                f"File `{s['name']}`:\n"
                f"```{s['language']}\n{s['snippet']}\n```"
            )
            continue
        summary = (s.get("ast_summary") or "")[:600]
        parts.append(
            f"#### {s['name']} ({s['language']})\n"
            f"Structure: {summary}\n"
            f"```{s['language']}\n{s['snippet']}\n```"
        )
    return "\n\n".join(parts)


def _dedupe_refs(refs: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for ref in refs:
        key = ref.lower()
        if key not in seen:
            seen.add(key)
            ordered.append(ref)
    return ordered


def extract_file_refs(question: str) -> list[str]:
    """Pull filenames like Repository.java or @src/Foo.py from a question."""
    refs = re.findall(r"@?([\w./-]+\.(?:java|py))", question, flags=re.IGNORECASE)
    refs += re.findall(r"\b(\w+\.(?:java|py))\b", question, flags=re.IGNORECASE)
    return _dedupe_refs(refs)


def extract_doc_file_refs(question: str) -> list[str]:
    """Pull documentation filenames like README.md or docs/setup.rst from a question.

    Kept separate from :func:`extract_file_refs` because the Debug and Code
    agents resolve refs against source extensions only.
    """
    refs = re.findall(r"@?([\w./-]+\.(?:md|txt|rst))", question, flags=re.IGNORECASE)
    refs += re.findall(r"\b(\w+\.(?:md|txt|rst))\b", question, flags=re.IGNORECASE)
    return _dedupe_refs(refs)


def filter_sources_for_question(
    sources: list[dict[str, str]], question: str
) -> list[dict[str, str]]:
    """When the user names a file, focus on that file instead of the whole repo."""
    refs = extract_file_refs(question)
    if not refs:
        return sources
    matched: list[dict[str, str]] = []
    for source in sources:
        name_lower = source["name"].lower()
        base = Path(source["name"]).name.lower()
        for ref in refs:
            ref_lower = ref.lower()
            ref_base = Path(ref_lower).name
            if (
                ref_lower in name_lower
                or name_lower.endswith(ref_lower)
                or base == ref_base
            ):
                matched.append(source)
                break
    return matched if matched else sources


def trim_sources_for_prompt(
    sources: list[dict[str, str]], max_chars: int = MAX_TOTAL_SOURCE_CHARS
) -> list[dict[str, str]]:
    """Keep every source in the prompt with a fair per-file character budget."""
    if not sources:
        return []
    per_file = max(max_chars // len(sources), 400)
    trimmed: list[dict[str, str]] = []
    for source in sources:
        copy = dict(source)
        snippet = source.get("snippet", "")
        if len(snippet) > per_file:
            copy["snippet"] = snippet[:per_file] + "\n... (truncated)"
        summary = copy.get("ast_summary") or ""
        if len(summary) > 600:
            copy["ast_summary"] = summary[:600] + "..."
        trimmed.append(copy)
    return trimmed


def add_python_comments(python_code: str) -> str:
    try:
        commented = codegen_generate(
            format_comment_inference(python_code), response_type="code"
        )
        if commented and validate_python_code.invoke({"code": commented}) == "OK":
            return commented
    except Exception as exc:
        logger.warning("Comment generation failed: %s", exc)
    return python_code


def _parse_traceback_context(error_text: str) -> dict[str, str]:
    """Extract error type, line number, and offending source line from a traceback."""
    text = error_text or ""
    ctx: dict[str, str] = {}
    line_match = re.search(r'File "[^"]+", line (\d+)', text)
    if line_match:
        ctx["line"] = line_match.group(1)
    exc_match = re.search(r"^(\w+(?:Error|Exception)):\s*(.+)$", text, re.MULTILINE)
    if exc_match:
        ctx["error_type"] = exc_match.group(1)
        ctx["error_message"] = exc_match.group(2).strip()
    elif text.strip():
        first = text.strip().splitlines()[0]
        ctx["error_type"] = first.split(":", 1)[0].strip()
    return ctx


def _format_traceback_hint(error_text: str, code: str) -> str:
    """Build a concise, error-agnostic hint for the fix model from traceback + source."""
    ctx = _parse_traceback_context(error_text)
    parts: list[str] = []
    if ctx.get("error_type"):
        parts.append(f"Error type: {ctx['error_type']}")
    if ctx.get("error_message"):
        parts.append(f"Message: {ctx['error_message']}")
    line_no = ctx.get("line")
    if line_no:
        parts.append(f"Traceback line: {line_no}")
        try:
            idx = int(line_no) - 1
            lines = (code or "").splitlines()
            if 0 <= idx < len(lines):
                parts.append(f"Offending source: {lines[idx].strip()!r}")
        except ValueError:
            pass
    return "\n".join(parts)


def _public_api_names(code: str) -> set[str]:
    """Return top-level function and class names (program structure to preserve)."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return set()
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def _executable_statement_segments(code: str) -> set[str]:
    """Fingerprint executable statements (calls, assignments, returns) for diffing."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return set()
    segments: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Return)):
            segment = ast.get_source_segment(code, node)
            if segment:
                segments.add(segment.strip())
        elif isinstance(node, ast.Expr):
            segment = ast.get_source_segment(code, node)
            if segment and not (
                isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                segments.add(segment.strip())
    return segments


def _has_meaningful_repair(original: str, fixed: str) -> bool:
    """True when fixed code adds guards, handlers, or new definitions vs original."""
    try:
        orig_tree = ast.parse(original)
        fixed_tree = ast.parse(fixed)
    except SyntaxError:
        return False

    def _count(tree: ast.AST, node_type: type) -> int:
        return sum(1 for n in ast.walk(tree) if isinstance(n, node_type))

    repair_nodes = (ast.Try, ast.If, ast.ExceptHandler, ast.Assert)
    for node_type in repair_nodes:
        if _count(fixed_tree, node_type) > _count(orig_tree, node_type):
            return True

    orig_defs = _public_api_names(original)
    fixed_defs = _public_api_names(fixed)
    if len(fixed_defs - orig_defs) > 0:
        return True

    orig_stmts = _executable_statement_segments(original)
    fixed_stmts = _executable_statement_segments(fixed)
    if len(fixed_stmts - orig_stmts) > 0 and len(fixed_stmts) >= len(orig_stmts):
        return True
    return False


def _traceback_offending_line_removed(original: str, fixed: str, error_text: str) -> bool:
    ctx = _parse_traceback_context(error_text)
    line_no = ctx.get("line")
    if not line_no:
        return False
    try:
        idx = int(line_no) - 1
    except ValueError:
        return False
    lines = original.splitlines()
    if not (0 <= idx < len(lines)):
        return False
    offending = lines[idx].strip()
    if not offending or offending.startswith("#"):
        return False
    return offending not in fixed


def _is_inadequate_runtime_fix(original: str, fixed: str, last_error: str) -> bool:
    """Reject fixes that silence runtime errors by deleting code without real repair."""
    if not last_error.strip() or fixed.strip() == original.strip():
        return False
    if _has_meaningful_repair(original, fixed):
        return False

    orig_stmts = _executable_statement_segments(original)
    fixed_stmts = _executable_statement_segments(fixed)
    removed = orig_stmts - fixed_stmts
    if removed:
        return True

    if _traceback_offending_line_removed(original, fixed, last_error):
        return True

    orig_api = _public_api_names(original)
    fixed_api = _public_api_names(fixed)
    if orig_api and orig_api - fixed_api:
        return True

    return False


# Backward-compatible alias for tests
_is_lazy_runtime_fix = _is_inadequate_runtime_fix

_INADEQUATE_FIX_HINT = (
    "(inadequate fix rejected: do not delete or hollow out code to silence the error — "
    "fix the root cause at the traceback line or add proper handling)"
)


def _runtime_fix_feedback(error_text: str, code: str) -> str:
    hint = _format_traceback_hint(error_text, code)
    return f"{hint}\n{_INADEQUATE_FIX_HINT}" if hint else _INADEQUATE_FIX_HINT


_STATIC_FIX_REJECTED_HINT = (
    "(static fix rejected: complete the expression, do not only add parentheses)"
)

_DANGLING_OP_BEFORE_PAREN_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*([+\-*/%])\s*\)"
)
_DANGLING_OP_AT_EOL_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*([+\-*/%])\s*$"
)


def _static_error_signature(val_res: str) -> str:
    if "incomplete expression" in val_res:
        return "incomplete_expression"
    match = re.search(r": '([^']+)'", val_res or "")
    if match:
        return f"syntax_line:{match.group(1)}"
    return (val_res or "")[:120]


def _is_stagnant_static_fix(before: str, candidate: str, before_error: str) -> bool:
    """True when a static fix attempt did not meaningfully improve the syntax error."""
    candidate_error = validate_python_code.invoke({"code": candidate})
    if candidate_error == "OK":
        return False
    if _static_error_signature(before_error) == _static_error_signature(candidate_error):
        return True
    before_lines = (before or "").splitlines()
    candidate_lines = (candidate or "").splitlines()
    if len(before_lines) == len(candidate_lines):
        for left, right in zip(before_lines, candidate_lines):
            if left.rstrip() + ")" == right.strip():
                return True
    return False


def _try_structural_syntax_repair(code: str, val_res: str) -> str | None:
    """Last-resort pattern repair for incomplete expressions and unclosed parens."""
    if not val_res or (
        "incomplete expression" not in val_res and "was never closed" not in val_res
    ):
        return None

    lines = (code or "").splitlines()
    if not lines:
        return None

    lineno = 1
    line_match = re.search(r"at line (\d+)", val_res)
    if line_match:
        lineno = int(line_match.group(1))
    idx = max(0, min(lineno - 1, len(lines) - 1))
    line = lines[idx]

    match = _DANGLING_OP_BEFORE_PAREN_RE.search(line)
    if match:
        left, op = match.group(1), match.group(2)
        lines[idx] = _DANGLING_OP_BEFORE_PAREN_RE.sub(
            f"{left} {op} {left})", line, count=1
        )
    else:
        match = _DANGLING_OP_AT_EOL_RE.search(line)
        if match:
            left, _op = match.group(1), match.group(2)
            lines[idx] = f"{line.rstrip()} {left})"
        elif "was never closed" in val_res and line.count("(") > line.count(")"):
            lines[idx] = line + ")"

    candidate = "\n".join(lines)
    try:
        ast.parse(candidate)
    except SyntaxError:
        return None
    if validate_python_code.invoke({"code": candidate}) == "OK":
        return candidate
    return None


def _apply_static_fix_candidate(
    python_code: str,
    candidate: str,
    val_res: str,
    last_error_holder: list[str],
    notify,
) -> str:
    """Adopt a static fix candidate or reject stagnant patches."""
    if _is_stagnant_static_fix(python_code, candidate, val_res):
        notify("Static fix made no progress; retrying with stronger hint...")
        candidate_err = validate_python_code.invoke({"code": candidate})
        last_error_holder[0] = f"{candidate_err}\n{_STATIC_FIX_REJECTED_HINT}"
        return python_code
    return candidate


def validate_and_fix_python(
    python_code: str,
    context: str,
    max_retries: int,
    merge_fn,
    attach_ast_fn,
    fix_python_fn,
    initial_state_fn,
) -> str:
    attempts = 0
    original = python_code
    last_val_res = ""
    while attempts <= max_retries:
        attempts += 1
        val_res = validate_python_code.invoke({"code": python_code})
        if val_res == "OK":
            return python_code
        last_val_res = val_res
        if attempts > max_retries:
            break
        fix_state = dict(
            initial_state_fn(
                f"Fix the python code.\n{context}\nError:\n{val_res}", unit="auto"
            )
        )
        fix_state["python_code"] = python_code
        fix_state["stderr"] = val_res
        fix_state["attempts"] = attempts - 1
        fix_state["max_retries"] = max_retries
        fix_state = merge_fn(fix_state, attach_ast_fn(fix_state))
        fix_state = merge_fn(fix_state, fix_python_fn(fix_state))
        candidate = fix_state.get("python_code") or python_code
        holder = [last_val_res]
        python_code = _apply_static_fix_candidate(
            python_code,
            candidate,
            val_res,
            holder,
            lambda _msg: None,
        )
        last_val_res = holder[0]

    if validate_python_code.invoke({"code": python_code}) != "OK":
        repaired = _try_structural_syntax_repair(original, last_val_res)
        if repaired:
            return repaired
        if python_code != original and _is_stagnant_static_fix(
            original, python_code, last_val_res
        ):
            return original
    return python_code


def validate_run_and_fix_python(
    python_code: str,
    context: str,
    max_retries: int,
    merge_fn,
    attach_ast_fn,
    fix_python_fn,
    initial_state_fn,
    *,
    run_after_static: bool = True,
    run_fn=None,
    on_progress=None,
) -> dict[str, Any]:
    """Static validate/fix loop, then optional sandbox run/fix loop.

    Returns dict with keys: code, static_ok, runtime_ok, static_attempts,
    runtime_attempts, last_error, trace_notes, changed.
    """
    run_fn = run_fn or run_python_dict
    trace_notes: list[str] = []
    static_attempts = 0
    runtime_attempts = 0
    last_error = ""
    original = python_code

    def _notify(msg: str) -> None:
        trace_notes.append(msg)
        if on_progress:
            on_progress(msg)

    # Phase A — static validation + fix
    while static_attempts <= max_retries:
        static_attempts += 1
        val_res = validate_python_code.invoke({"code": python_code})
        if val_res == "OK":
            break
        last_error = val_res
        if static_attempts > max_retries:
            _notify(f"Static validation failed after {max_retries} fix attempt(s).")
            repaired = _try_structural_syntax_repair(original, last_error)
            if repaired:
                python_code = repaired
                break
            if python_code != original and _is_stagnant_static_fix(
                original, python_code, last_error
            ):
                python_code = original
            return {
                "code": python_code,
                "static_ok": False,
                "runtime_ok": False,
                "static_attempts": static_attempts,
                "runtime_attempts": 0,
                "last_error": last_error,
                "trace_notes": trace_notes,
                "changed": python_code != original,
            }
        _notify(f"Static fix attempt {static_attempts}/{max_retries}")
        fix_state = dict(
            initial_state_fn(
                f"Fix the python code.\n{context}\nError:\n{val_res}", unit="auto"
            )
        )
        fix_state["python_code"] = python_code
        fix_state["stderr"] = val_res
        fix_state["attempts"] = static_attempts - 1
        fix_state["max_retries"] = max_retries
        fix_state = merge_fn(fix_state, attach_ast_fn(fix_state))
        fix_state = merge_fn(fix_state, fix_python_fn(fix_state))
        candidate = fix_state.get("python_code") or python_code
        holder = [last_error]
        python_code = _apply_static_fix_candidate(
            python_code,
            candidate,
            val_res,
            holder,
            _notify,
        )
        last_error = holder[0]

    static_ok = validate_python_code.invoke({"code": python_code}) == "OK"
    if not static_ok:
        last_error = validate_python_code.invoke({"code": python_code})
        repaired = _try_structural_syntax_repair(original, last_error)
        if repaired:
            python_code = repaired
            static_ok = True
        elif python_code != original and _is_stagnant_static_fix(
            original, python_code, last_error
        ):
            python_code = original
            last_error = validate_python_code.invoke({"code": python_code})
    if not static_ok:
        return {
            "code": python_code,
            "static_ok": False,
            "runtime_ok": False,
            "static_attempts": static_attempts,
            "runtime_attempts": 0,
            "last_error": last_error,
            "trace_notes": trace_notes,
            "changed": python_code != original,
        }

    if not run_after_static:
        return {
            "code": python_code,
            "static_ok": True,
            "runtime_ok": True,
            "static_attempts": static_attempts,
            "runtime_attempts": 0,
            "last_error": "",
            "trace_notes": trace_notes,
            "changed": python_code != original,
        }

    # Phase B — sandbox run + fix
    while runtime_attempts <= max_retries:
        _notify("Running in sandbox...")
        result = run_fn(python_code, timeout=10)
        stdout = result.get("stdout") or ""
        stderr = result.get("stderr") or result.get("error") or ""
        exit_ok = bool(result.get("passed") or result.get("exit_ok"))

        if exit_ok:
            if (
                python_code != original
                and last_error
                and _is_inadequate_runtime_fix(original, python_code, last_error)
            ):
                runtime_attempts += 1
                _notify("Inadequate fix rejected (silenced error by deleting code); retrying...")
                last_error = _runtime_fix_feedback(last_error, original)
                python_code = original
                if runtime_attempts > max_retries:
                    _notify(f"Runtime fix failed after {max_retries} attempt(s).")
                    return {
                        "code": python_code,
                        "static_ok": True,
                        "runtime_ok": False,
                        "static_attempts": static_attempts,
                        "runtime_attempts": runtime_attempts,
                        "last_error": last_error,
                        "trace_notes": trace_notes,
                        "changed": False,
                    }
                continue
            return {
                "code": python_code,
                "static_ok": True,
                "runtime_ok": True,
                "static_attempts": static_attempts,
                "runtime_attempts": runtime_attempts,
                "last_error": "",
                "trace_notes": trace_notes,
                "changed": python_code != original,
            }

        runtime_attempts += 1
        last_error = stderr or stdout or "Nonzero exit code"
        if runtime_attempts > max_retries:
            _notify(f"Runtime fix failed after {max_retries} attempt(s).")
            return {
                "code": python_code,
                "static_ok": True,
                "runtime_ok": False,
                "static_attempts": static_attempts,
                "runtime_attempts": runtime_attempts,
                "last_error": last_error,
                "trace_notes": trace_notes,
                "changed": python_code != original,
            }

        _notify(f"Runtime fix attempt {runtime_attempts}/{max_retries}")
        traceback_hint = _format_traceback_hint(last_error, python_code)
        runtime_msg = "\n".join(x for x in [stdout, stderr, traceback_hint] if x)
        fix_state = dict(
            initial_state_fn(
                f"Fix the python code.\n{context}\nRuntime error:\n{runtime_msg}",
                unit="auto",
            )
        )
        fix_state["python_code"] = python_code
        fix_state["stderr"] = runtime_msg
        fix_state["stdout"] = stdout
        fix_state["attempts"] = runtime_attempts - 1
        fix_state["max_retries"] = max_retries
        fix_state = merge_fn(fix_state, attach_ast_fn(fix_state))
        fix_state = merge_fn(fix_state, fix_python_fn(fix_state))
        candidate = fix_state.get("python_code") or python_code
        if _is_inadequate_runtime_fix(original, candidate, last_error):
            _notify("Inadequate fix rejected (deleted code without repair); retrying...")
            last_error = _runtime_fix_feedback(last_error, python_code)
            continue
        python_code = candidate

        val_res = validate_python_code.invoke({"code": python_code})
        if val_res != "OK":
            _notify("Runtime fix introduced static errors; applying static fixes.")
            python_code = validate_and_fix_python(
                python_code,
                context,
                max_retries,
                merge_fn,
                attach_ast_fn,
                fix_python_fn,
                initial_state_fn,
            )
            if validate_python_code.invoke({"code": python_code}) != "OK":
                last_error = validate_python_code.invoke({"code": python_code})
                return {
                    "code": python_code,
                    "static_ok": False,
                    "runtime_ok": False,
                    "static_attempts": static_attempts,
                    "runtime_attempts": runtime_attempts,
                    "last_error": last_error,
                    "trace_notes": trace_notes,
                    "changed": python_code != original,
                }

    return {
        "code": python_code,
        "static_ok": True,
        "runtime_ok": False,
        "static_attempts": static_attempts,
        "runtime_attempts": runtime_attempts,
        "last_error": last_error,
        "trace_notes": trace_notes,
        "changed": python_code != original,
    }


def queue_write(
    session: dict[str, Any],
    abs_path: str,
    content: str,
    *,
    action: str = "create",
    original: str = "",
    **meta: Any,
) -> None:
    pending = list(session.get("pending_writes") or [])
    pending.append(
        {
            "path": abs_path,
            "content": content,
            "action": action,
            "original": original,
            "name": meta.get("name") or Path(abs_path).name,
            "java": meta.get("java", ""),
            "python": meta.get("python", content if abs_path.endswith(".py") else ""),
            "language": meta.get("language", "python"),
        }
    )
    session["pending_writes"] = pending


def apply_pending_writes(session: dict[str, Any]) -> list[str]:
    written: list[str] = []
    for item in session.get("pending_writes") or []:
        path = item.get("path")
        content = item.get("content", "")
        if path:
            write_text_file.invoke({"path": path, "content": content})
            written.append(path)
    session["pending_writes"] = []
    session["state"] = "init"
    return written


def discard_pending_writes(session: dict[str, Any]) -> int:
    n = len(session.get("pending_writes") or [])
    session["pending_writes"] = []
    session["state"] = "init"
    return n


def pending_to_review_data(session: dict[str, Any]) -> list[dict]:
    review: list[dict] = []
    for item in session.get("pending_writes") or []:
        entry = {
            "name": item.get("name") or Path(item.get("path", "")).name,
            "path": item.get("path", ""),
            "java": item.get("java", ""),
            "python": item.get("python", ""),
            "content": item.get("content", ""),
            "language": item.get("language", "python"),
        }
        if entry["language"] == "java" and not entry["java"]:
            entry["java"] = entry["content"]
        if entry["language"] == "python" and not entry["python"]:
            entry["python"] = entry["content"]
        review.append(entry)
    return review


def yield_chat(history: list[dict[str, str]], payload: dict[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out["history"] = list(history)
    return out


def append_user(history: list[dict[str, str]], content: str) -> None:
    history.append({"role": "user", "content": content})


def append_bot(history: list[dict[str, str]], content: str) -> None:
    history.append({"role": "assistant", "content": content})


def update_last_bot(history: list[dict[str, str]], content: str) -> None:
    if history and history[-1]["role"] == "assistant":
        history[-1]["content"] = content
    else:
        append_bot(history, content)


def chat_action_undo(session_state: dict[str, Any], history: list[dict[str, str]]) -> dict[str, Any]:
    n = discard_pending_writes(session_state)
    append_bot(history, f"Undone. Discarded {n} pending change(s).")
    return yield_chat(
        history,
        {"session_state": session_state, "show_action_buttons": False, "review_data": []},
    )


def chat_action_keep(session_state: dict[str, Any], history: list[dict[str, str]]) -> dict[str, Any]:
    written = apply_pending_writes(session_state)
    append_bot(history, f"Kept. Wrote {len(written)} file(s) to disk.")
    return yield_chat(
        history,
        {"session_state": session_state, "show_action_buttons": False, "review_data": []},
    )


def chat_action_review(session_state: dict[str, Any], history: list[dict[str, str]]) -> dict[str, Any]:
    append_bot(history, "Review pending changes below.")
    return yield_chat(
        history,
        {
            "session_state": session_state,
            "show_action_buttons": True,
            "review_data": pending_to_review_data(session_state),
        },
    )


_ASK_CODE_ARTIFACTS = (
    "code",
    "function",
    "functions",
    "class",
    "classes",
    "script",
    "scripts",
    "module",
    "modules",
    "app",
    "application",
    "program",
    "converter",
    "parser",
    "handler",
    "loader",
    "reader",
    "writer",
    "scraper",
    "crawler",
    "api",
    "endpoint",
    "endpoints",
    "server",
    "client",
    "service",
    "services",
    "utility",
    "utilities",
    "helper",
    "helpers",
    "algorithm",
    "algorithms",
    "method",
    "methods",
    "routine",
    "routines",
    "tool",
    "tools",
    "library",
    "component",
    "components",
    "controller",
    "controllers",
    "model",
    "models",
    "middleware",
    "daemon",
    "worker",
    "workers",
    "pipeline",
    "pipelines",
    "solution",
    "system",
    "feature",
    "snippet",
    "boilerplate",
    "template",
    "skeleton",
    "stub",
    "interface",
    "enum",
    "struct",
    "bean",
    "entity",
    "repository",
    "mapper",
    "serializer",
    "validator",
    "formatter",
    "calculator",
    "scheduler",
    "webhook",
    "socket",
    "cli",
    "command",
    "lambda",
    "decorator",
    "fixture",
    "mock",
    "regex",
    "expression",
    "query",
    "dataframe",
    "plot",
    "chart",
    "visualization",
    "test",
    "tests",
    "unit test",
)

_ASK_CODE_VERBS = (
    "write",
    "create",
    "generate",
    "implement",
    "build",
    "develop",
    "make",
    "produce",
    "draft",
    "code",
    "program",
    "script",
    "add",
    "design",
    "craft",
    "compose",
    "author",
)

_ASK_CODE_ACTIONS = (
    "read",
    "parse",
    "convert",
    "transform",
    "translate",
    "load",
    "save",
    "fetch",
    "process",
    "handle",
    "validate",
    "sort",
    "filter",
    "merge",
    "split",
    "iterate",
    "loop",
    "compute",
    "calculate",
    "search",
    "match",
    "extract",
    "download",
    "upload",
    "send",
    "receive",
    "connect",
    "authenticate",
    "authorize",
    "encrypt",
    "decrypt",
    "serialize",
    "deserialize",
    "render",
    "display",
    "log",
    "monitor",
    "schedule",
    "retry",
    "cache",
    "stream",
)

_ASK_EXPLAIN_RE = (
    re.compile(r"^convert (the )?(selected )?files?\b"),
    re.compile(r"^migrate\b"),
    re.compile(r"\b(selected files|these files|the files)\b"),
    re.compile(r"^(explain|describe|summarize|document)\b"),
    re.compile(r"\b(explain|describe|summarize|document)\s+(this|the|selected|these)\b"),
    re.compile(r"\bwhat (does|is|are|was|were)\b"),
    re.compile(r"\bhow does\b"),
    re.compile(r"\bwhy (does|is|are|do|did)\b"),
    re.compile(r"\btell me about\b"),
    re.compile(r"\bwalk me through\b"),
    re.compile(r"\bwhere is\b"),
    re.compile(r"\bwho (wrote|created|owns)\b"),
    re.compile(r"\bpurpose of\b"),
    re.compile(r"\boverview of\b"),
    re.compile(r"\barchitecture of\b"),
    re.compile(r"\.(java|py|js|ts|go|rs|cpp|c|h)\b.*\?$"),
    re.compile(r"^what is this\b"),
    re.compile(r"^what does this\b"),
)

_ASK_CODE_STRONG_RE = (
    re.compile(r"^python:"),
    re.compile(r"^java:"),
    re.compile(r"^write python\b"),
    re.compile(r"^write java\b"),
    re.compile(r"\bgenerate python\b"),
    re.compile(r"\bgenerate java\b"),
    re.compile(r"\bcreate (a )?python\b"),
    re.compile(r"\bcreate (a )?java\b"),
    re.compile(r"\bimplement in python\b"),
    re.compile(r"\bimplement in java\b"),
    re.compile(r"\bwrite (a )?python\b"),
    re.compile(r"\bwrite (a )?java\b"),
    re.compile(r"\bshow me (the )?code\b"),
    re.compile(r"\bneed (some )?code\b"),
    re.compile(r"\bwant (some )?code\b"),
    re.compile(r"\bcode (for|to|that)\b"),
    re.compile(r"\bsnippet (for|to|that)\b"),
    re.compile(r"\bin python\b"),
    re.compile(r"\bin java\b"),
    re.compile(r"\busing python\b"),
    re.compile(r"\busing java\b"),
    re.compile(r"\bwith python\b"),
    re.compile(r"\bwith java\b"),
    re.compile(r"\bjava to python\b"),
    re.compile(r"\bpython to java\b"),
)


def _ask_artifacts_pattern() -> str:
    return "|".join(re.escape(a) for a in _ASK_CODE_ARTIFACTS)


def _ask_verbs_pattern() -> str:
    return "|".join(_ASK_CODE_VERBS)


def _ask_actions_pattern() -> str:
    return "|".join(_ASK_CODE_ACTIONS)


def _is_ask_explain_intent(message: str) -> bool:
    """Prompts that should document/explain, not generate inline code."""
    lower = message.strip().lower()
    if any(p.search(lower) for p in _ASK_CODE_STRONG_RE):
        return False
    return any(p.search(lower) for p in _ASK_EXPLAIN_RE)


def _is_ask_code_gen_intent(message: str) -> bool:
    """Detect natural-language requests to generate code in Ask chat."""
    lower = message.strip().lower()
    if not lower:
        return False
    if any(p.search(lower) for p in _ASK_CODE_STRONG_RE):
        return True

    artifacts = _ask_artifacts_pattern()
    verbs = _ask_verbs_pattern()
    actions = _ask_actions_pattern()

    patterns = (
        rf"\b(give me|show me|i need|i want|can you|could you|please|help me)\b"
        rf".{{0,30}}\b({artifacts}|program|code)\b",
        rf"\b({verbs})\s+(me\s+)?(a|an|the|some)?\s*({artifacts})\b",
        rf"\b({verbs})\s+(me\s+)?(a|an|the)\s+program\b",
        rf"\bprogram that ({actions}|converts|translates|transforms)\b",
        rf"\b({verbs})\b.{{0,80}}\b(that|to)\s+({actions})\b",
        rf"\b({artifacts})\b.{{0,40}}\b({verbs})\b",
        rf"^({verbs})\b[:\s]",
        rf"^how to ({verbs})\b",
        rf"^help me ({verbs})\b",
        rf"\bcoding (challenge|exercise|task|problem)\b",
        rf"\bleetcode\b",
        rf"\bfactorial\b",
        rf"\bfibonacci\b",
        rf"\bquicksort\b",
        rf"\bbinary search\b",
        rf"\bmerge sort\b",
        rf"\blinked list\b",
        rf"\bbinary tree\b",
        rf"\bdynamic programming\b",
        rf"\brest api\b.*\b({verbs})\b",
        rf"\b({verbs})\b.*\brest api\b",
    )
    return any(re.search(p, lower) for p in patterns)


def _language_from_prompt_hints(message: str) -> str | None:
    """Return gen_java/gen_python when the message explicitly names a language."""
    lower = message.strip().lower()
    if any(p in lower for p in ("java to python", "java2py", "j2py")):
        return "gen_python"
    if any(p in lower for p in ("python to java", "py2java")):
        return "gen_java"
    java_hints = (
        r"\bin java\b",
        r"\busing java\b",
        r"\bwith java\b",
        r"\bjava program\b",
        r"\bjava class\b",
        r"\bgenerate java\b",
        r"\bwrite java\b",
        r"\bcreate java\b",
        r"\bimplement in java\b",
    )
    python_hints = (
        r"\bin python\b",
        r"\busing python\b",
        r"\bwith python\b",
        r"\bpython program\b",
        r"\bpython script\b",
        r"\bgenerate python\b",
        r"\bwrite python\b",
        r"\bcreate python\b",
        r"\bimplement in python\b",
    )
    if any(re.search(p, lower) for p in java_hints):
        return "gen_java"
    if any(re.search(p, lower) for p in python_hints):
        return "gen_python"
    return None


def _detect_ask_code_language(message: str) -> str:
    """Prefer python vs java for NL code-gen prompts without an explicit prefix."""
    lower = message.strip().lower()
    if lower.startswith("python:") or lower.startswith("write python"):
        return "gen_python"
    if lower.startswith("java:") or lower.startswith("write java"):
        return "gen_java"
    hinted = _language_from_prompt_hints(message)
    if hinted:
        return hinted
    return "gen_python"


def detect_ask_task(message: str) -> str:
    """Route Ask Agent: explain (default) vs inline NL code generation in chat."""
    if _is_ask_explain_intent(message):
        return "explain"
    if _is_ask_code_gen_intent(message):
        return _detect_ask_code_language(message)
    return "explain"


def detect_code_task(
    message: str,
    active_files: list[str] | None = None,
    repo_root: str | None = None,
) -> str:
    lower = message.strip().lower()
    active = active_files or []
    if lower.startswith("python:") or lower.startswith("write python"):
        return "gen_python"
    if lower.startswith("java:") or lower.startswith("write java"):
        return "gen_java"
    if _is_migrate_intent(message, active):
        return "migrate"

    hinted = _language_from_prompt_hints(message)
    if hinted:
        return hinted

    if active:
        java_sel = all(str(f).lower().endswith(".java") for f in active)
        py_sel = all(str(f).lower().endswith(".py") for f in active)
        if java_sel and not py_sel:
            return "gen_java"
        if py_sel and not java_sel:
            return "gen_python"

    if repo_root:
        primary = detect_repo_primary_language(repo_root)
        if primary == "java":
            return "gen_java"
        if primary == "python":
            return "gen_python"

    return "gen_python"


def _has_java_selection(active_files: list[str]) -> bool:
    return any(str(f).lower().endswith(".java") for f in active_files)


_NL_CREATE_GUARD_RE = (
    re.compile(r"\bsimilar to\b"),
    re.compile(r"\blike the (selected|file)\b"),
    re.compile(r"\bnew class\b"),
    re.compile(r"\bbased on (the )?(selected|file)\b"),
)


def _is_nl_create_intent(message: str) -> bool:
    """Detect NL requests to create new same-language code from a template."""
    if _is_ask_code_gen_intent(message):
        return True
    lower = message.strip().lower()
    return any(p.search(lower) for p in _NL_CREATE_GUARD_RE)


def _is_migrate_intent(message: str, active_files: list[str] | None = None) -> bool:
    lower = message.strip().lower()
    active = active_files or []

    if _is_nl_create_intent(message):
        return False

    if lower.endswith(".java") or "/" in message:
        return True
    if "migrate" in lower:
        return True

    for phrase in ("java to python", "port to python", "java2py", "j2py"):
        if phrase in lower:
            return True

    has_java = _has_java_selection(active)
    wants_convert = "convert" in lower or "translate" in lower
    refers_selection = any(
        hint in lower
        for hint in (
            "selected",
            "these files",
            "the files",
            "this file",
            "the file",
        )
    )
    nl_python = any(
        hint in lower
        for hint in (" in python", "write python", "generate python", "create python")
    )
    if nl_python:
        return False

    if wants_convert and (refers_selection or ".java" in lower):
        return True
    if has_java and wants_convert and len(lower.split()) <= 4:
        return True
    return False


def strip_task_prefix(message: str) -> str:
    lower = message.strip().lower()
    for prefix in ("python:", "java:", "write python", "write java"):
        if lower.startswith(prefix):
            return message.strip()[len(prefix) :].strip()
    for prefix in ("migrate", "convert", "translate"):
        if lower.startswith(prefix):
            return message.strip()[len(prefix) :].strip()
    return message.strip()


_SPEC_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "for",
        "to",
        "in",
        "of",
        "with",
        "using",
        "write",
        "create",
        "generate",
        "implement",
        "build",
        "design",
        "code",
        "program",
        "class",
        "function",
        "method",
        "pattern",
        "python",
        "java",
        "file",
        "please",
        "help",
        "make",
        "add",
        "new",
    }
)

_PY_CLASS_RE = re.compile(r"^class\s+(\w+)", re.MULTILINE)
_PY_DEF_RE = re.compile(r"^def\s+(\w+)", re.MULTILINE)
_JAVA_CLASS_RE = re.compile(r"(?:public\s+)?(?:final\s+)?class\s+(\w+)", re.MULTILINE)


def _to_snake(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.replace("-", "_").lower()


def _to_pascal(name: str) -> str:
    parts = re.split(r"[_\s-]+", name.strip())
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def detect_repo_primary_language(repo_root: str) -> str:
    """Return ``java``, ``python``, or ``mixed`` from file counts under the repo."""
    try:
        files = list_repo_relative_files(repo_root, extensions=".java,.py")
    except (FileNotFoundError, OSError):
        return "mixed"
    java_count = sum(1 for f in files if f.lower().endswith(".java"))
    py_count = sum(1 for f in files if f.lower().endswith(".py"))
    if java_count >= 2 * max(py_count, 1) and java_count > 0:
        return "java"
    if py_count >= 2 * max(java_count, 1) and py_count > 0:
        return "python"
    return "mixed"


def _spec_keywords(spec: str) -> list[str]:
    text = strip_task_prefix(spec).lower()
    words = re.findall(r"[a-z][a-z0-9_]{2,}", text)
    return [w for w in words if w not in _SPEC_STOP_WORDS]


def _explicit_generated_path(root: Path, spec: str, ext: str) -> Path | None:
    for ref in extract_file_refs(spec):
        if not ref.lower().endswith(ext.lower()):
            continue
        rel = Path(ref)
        if "/" in ref or "\\" in ref:
            parent = root / rel.parent
            return _unique_path(parent, rel.stem, ext)
        return _unique_path(root, rel.stem, ext)
    return None


def _pattern_basename(spec: str) -> str | None:
    from agent.prompts import _first_known_pattern

    pattern = _first_known_pattern(spec)
    if not pattern:
        return None
    return pattern.replace(" ", "_").lower()


def _code_basename(code: str, ext: str) -> str | None:
    if not code.strip():
        return None
    if ext == ".py":
        match = _PY_CLASS_RE.search(code)
        if match:
            return _to_snake(match.group(1))
        match = _PY_DEF_RE.search(code)
        if match:
            return match.group(1).lower()
    elif ext == ".java":
        match = _JAVA_CLASS_RE.search(code)
        if match:
            return match.group(1)
    return None


def _spec_slug(spec: str) -> str | None:
    keywords = _spec_keywords(spec)
    if not keywords:
        return None
    return "_".join(keywords[:3])


def _unique_path(root: Path, base: str, ext: str) -> Path:
    safe = re.sub(r"[^\w.-]", "_", base).strip("._") or "generated"
    candidate = root / f"{safe}{ext}"
    if not candidate.exists():
        return candidate
    for i in range(2, 100):
        candidate = root / f"{safe}_{i}{ext}"
        if not candidate.exists():
            return candidate
    return next_generated_name(str(root), ext)


def _output_dir_from_active_files(
    repo_root: str,
    active_files: list[str] | None,
    ext: str,
) -> Path | None:
    """Return the parent directory of the first active file matching ``ext``."""
    if not active_files:
        return None
    for rel in active_files:
        if not str(rel).lower().endswith(ext.lower()):
            continue
        try:
            abs_path = resolve_file_query(repo_root, rel, extensions=ext)
        except (AmbiguousFileMatch, FileNotFoundError):
            continue
        return abs_path.parent
    return None


def _active_file_snippets(
    repo_root: str,
    active_files: list[str] | None,
    ext: str,
    max_files: int = 2,
) -> list[tuple[str, str]]:
    """Load content from picker-selected files matching ``ext``."""
    if not active_files:
        return []
    root = resolve_repo_root(repo_root)
    snippets: list[tuple[str, str]] = []
    for rel in active_files:
        if not str(rel).lower().endswith(ext.lower()):
            continue
        try:
            abs_path = resolve_file_query(repo_root, rel, extensions=ext)
        except (AmbiguousFileMatch, FileNotFoundError):
            continue
        content = read_text_file.invoke({"path": str(abs_path)})
        if content.startswith("(missing"):
            continue
        try:
            rel_path = str(abs_path.relative_to(root))
        except ValueError:
            rel_path = abs_path.name
        snippets.append((rel_path, content.strip()))
        if len(snippets) >= max_files:
            break
    return snippets


def suggest_generated_path(
    repo_root: str,
    ext: str,
    spec: str,
    code: str = "",
    active_files: list[str] | None = None,
) -> Path:
    """Pick an output path from the prompt, generated code, or a numbered fallback."""
    root = resolve_repo_root(repo_root)
    out_dir = _output_dir_from_active_files(repo_root, active_files, ext) or root

    explicit = _explicit_generated_path(root, spec, ext)
    if explicit is not None:
        return explicit

    base = _pattern_basename(spec)
    if not base:
        base = _code_basename(code, ext)
    if not base:
        base = _spec_slug(spec)
    if base:
        if ext == ".java":
            base = _to_pascal(base)
        else:
            base = _to_snake(base)
        return _unique_path(out_dir, base, ext)

    if out_dir != root:
        return next_generated_name(str(out_dir), ext)
    return next_generated_name(repo_root, ext)


def _score_repo_files_for_spec(files: list[str], keywords: list[str]) -> list[str]:
    if not keywords:
        return files[:2]
    scored: list[tuple[int, str]] = []
    for rel in files:
        rel_lower = rel.lower()
        base = Path(rel).stem.lower()
        score = sum(1 for kw in keywords if kw in rel_lower or kw in base)
        if score:
            scored.append((score, rel))
    scored.sort(key=lambda item: (-item[0], item[1]))
    if scored:
        return [rel for _, rel in scored[:2]]
    return files[:2]


def build_codegen_few_shot(
    repo_root: str,
    spec: str,
    language: str,
    max_chars: int = 1500,
    active_files: list[str] | None = None,
) -> str:
    """Build a repo-style few-shot prefix for NL code generation."""
    from data.scripts.prompt_templates import format_codegen_repo_style
    from inference.repo_rag_pipeline import get_repo_rag_pipeline, rag_index_exists

    ext = ".java" if language == "java" else ".py"
    lang_tag = "java" if language == "java" else "python"
    snippets: list[tuple[str, str]] = []
    seen_paths: set[str] = set()
    keywords = _spec_keywords(spec)

    for rel_path, content in _active_file_snippets(repo_root, active_files, ext):
        snippets.append((rel_path, content[:800]))
        seen_paths.add(rel_path.lower())

    if rag_index_exists(repo_root):
        pipeline = get_repo_rag_pipeline(repo_root)
        for chunk in pipeline.retrieve(spec, top_k=6):
            meta = chunk.get("metadata") or {}
            rel_path = str(meta.get("file_path") or "")
            if not rel_path.lower().endswith(ext):
                continue
            if rel_path.lower() in seen_paths:
                continue
            content = (chunk.get("content") or "").strip()
            if content:
                snippets.append((rel_path, content))
                seen_paths.add(rel_path.lower())
            if len(snippets) >= 2:
                break

    if len(snippets) < 2:
        try:
            files = [
                f
                for f in list_repo_relative_files(repo_root, extensions=ext)
            ]
        except (FileNotFoundError, OSError):
            files = []
        picked = _score_repo_files_for_spec(files, keywords)
        root = resolve_repo_root(repo_root)
        for rel in picked:
            if rel.lower() in seen_paths:
                continue
            content = read_text_file.invoke({"path": str(root / rel)})
            if content.startswith("(missing"):
                continue
            snippets.append((rel, content[:800]))
            seen_paths.add(rel.lower())
            if len(snippets) >= 2:
                break

    if not snippets:
        return ""

    parts: list[str] = []
    budget = max_chars
    for name, snippet in snippets:
        block = format_codegen_repo_style(name, lang_tag, snippet)
        if len(block) > budget:
            trimmed = format_codegen_repo_style(
                name,
                lang_tag,
                snippet[: max(200, budget - 120)],
            )
            parts.append(trimmed)
            break
        parts.append(block)
        budget -= len(block)
    return "".join(parts)


def code_task_language_note(task: str, repo_root: str) -> str:
    """Short suffix for status messages explaining language choice."""
    if task == "gen_java":
        primary = detect_repo_primary_language(repo_root)
        if primary == "java":
            return " (repo is Java-dominant)"
    return ""


def next_generated_name(repo_root: str, ext: str) -> Path:
    root = resolve_repo_root(repo_root)
    for i in range(1, 100):
        candidate = root / f"generated_{i}{ext}"
        if not candidate.exists():
            return candidate
    return root / f"generated{ext}"
