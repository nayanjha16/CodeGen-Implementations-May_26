"""Shared utilities for repo workspace agents (Ask / Code / Debug)."""

from __future__ import annotations

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
    }


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
) -> tuple[list[dict[str, str]], list[str], str | None]:
    """Load sources for picker selection and/or message file refs.

    Returns (sources, absolute_paths, error_message).
    """
    target_paths, err = resolve_active_file_queries(repo_root, message, active_files)
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
        lang = "java" if fpath.endswith(".java") else "python"
        ast_summary = ""
        if include_ast:
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


def extract_file_refs(question: str) -> list[str]:
    """Pull filenames like Repository.java or @src/Foo.py from a question."""
    refs = re.findall(r"@?([\w./-]+\.(?:java|py))", question, flags=re.IGNORECASE)
    refs += re.findall(r"\b(\w+\.(?:java|py))\b", question, flags=re.IGNORECASE)
    seen: set[str] = set()
    ordered: list[str] = []
    for ref in refs:
        key = ref.lower()
        if key not in seen:
            seen.add(key)
            ordered.append(ref)
    return ordered


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
    while attempts <= max_retries:
        attempts += 1
        val_res = validate_python_code.invoke({"code": python_code})
        if val_res == "OK":
            return python_code
        if attempts > max_retries:
            break
        fix_state = dict(
            initial_state_fn(
                f"Fix the python code.\n{context}\nError:\n{val_res}", unit="auto"
            )
        )
        fix_state["python_code"] = python_code
        fix_state["stderr"] = val_res
        fix_state = merge_fn(fix_state, attach_ast_fn(fix_state))
        fix_state = merge_fn(fix_state, fix_python_fn(fix_state))
        python_code = fix_state.get("python_code") or python_code
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
        fix_state = merge_fn(fix_state, attach_ast_fn(fix_state))
        fix_state = merge_fn(fix_state, fix_python_fn(fix_state))
        python_code = fix_state.get("python_code") or python_code

    static_ok = validate_python_code.invoke({"code": python_code}) == "OK"
    if not static_ok:
        last_error = validate_python_code.invoke({"code": python_code})
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
        runtime_msg = "\n".join(x for x in [stdout, stderr] if x)
        fix_state = dict(
            initial_state_fn(
                f"Fix the python code.\n{context}\nRuntime error:\n{runtime_msg}",
                unit="auto",
            )
        )
        fix_state["python_code"] = python_code
        fix_state["stderr"] = runtime_msg
        fix_state["stdout"] = stdout
        fix_state = merge_fn(fix_state, attach_ast_fn(fix_state))
        fix_state = merge_fn(fix_state, fix_python_fn(fix_state))
        python_code = fix_state.get("python_code") or python_code

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


def _detect_ask_code_language(message: str) -> str:
    """Prefer python vs java for NL code-gen prompts without an explicit prefix."""
    lower = message.strip().lower()
    if lower.startswith("python:") or lower.startswith("write python"):
        return "gen_python"
    if lower.startswith("java:") or lower.startswith("write java"):
        return "gen_java"
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
    return "gen_python"


def detect_ask_task(message: str) -> str:
    """Route Ask Agent: explain (default) vs inline NL code generation in chat."""
    if _is_ask_explain_intent(message):
        return "explain"
    if _is_ask_code_gen_intent(message):
        return _detect_ask_code_language(message)
    return "explain"


def detect_code_task(message: str, active_files: list[str] | None = None) -> str:
    lower = message.strip().lower()
    active = active_files or []
    if lower.startswith("python:") or lower.startswith("write python"):
        return "gen_python"
    if lower.startswith("java:") or lower.startswith("write java"):
        return "gen_java"
    if _is_migrate_intent(message, active):
        return "migrate"
    return "gen_python"


def _has_java_selection(active_files: list[str]) -> bool:
    return any(str(f).lower().endswith(".java") for f in active_files)


def _is_migrate_intent(message: str, active_files: list[str] | None = None) -> bool:
    lower = message.strip().lower()
    active = active_files or []

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
    if has_java and refers_selection:
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


def next_generated_name(repo_root: str, ext: str) -> Path:
    root = resolve_repo_root(repo_root)
    for i in range(1, 100):
        candidate = root / f"generated_{i}{ext}"
        if not candidate.exists():
            return candidate
    return root / f"generated{ext}"
