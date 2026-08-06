"""Debug Agent — scan and fix Python issues in a repo workspace."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Generator

from agent.nodes import attach_ast, fix_python
from agent.repo_migrate import _merge
from agent.repo_utils import (
    append_bot,
    append_user,
    empty_session,
    index_repo_files,
    queue_write,
    resolve_active_file_queries,
    resolve_repo_root,
    set_active_files,
    update_last_bot,
    validate_run_and_fix_python,
    yield_chat,
)
from agent.state import initial_state
from agent.tools import read_text_file, validate_python_code

STATE_INIT = "init"
STATE_REVIEW = "review"

_FIX_ALL_MIGRATED_RE = re.compile(
    r"\bfix\s+(all\s+)?(migrated|converted)\b", re.IGNORECASE
)
_FIX_ALL_SCANNED_RE = re.compile(r"\bfix\s+all\s+scanned\b", re.IGNORECASE)
_FIX_ALL_RE = re.compile(r"\bfix\s+all\b", re.IGNORECASE)


def chat_debug_generator(
    user_message: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    repo_root: str,
    max_files: int = 20,
    max_retries: int = 3,
) -> Generator[dict[str, Any], None, None]:
    if not session_state:
        session_state = empty_session(repo_root)

    if repo_root:
        session_state["repo_root"] = repo_root

    root = (session_state.get("repo_root") or "").strip()
    if not root:
        append_user(history, user_message)
        append_bot(history, "Set the **Project root** path above, then describe what to debug.")
        yield yield_chat(history, {"session_state": session_state})
        return

    append_user(history, user_message)
    append_bot(history, "Debug Agent scanning...")
    yield yield_chat(history, {"session_state": session_state})

    try:
        resolve_repo_root(root)
    except FileNotFoundError:
        update_last_bot(history, f"Repo path not found: `{root}`")
        yield yield_chat(history, {"session_state": session_state})
        return

    msg = user_message.strip().lower()
    if msg.startswith("scan") or msg == "scan for errors":
        yield from _scan_repo(history, session_state, root, max_files)
        return

    if _is_fix_all_command(user_message):
        yield from _fix_all(
            user_message, history, session_state, root, max_files, max_retries
        )
        return

    yield from _fix_target(
        user_message, history, session_state, root, max_files, max_retries
    )


def _is_fix_all_command(message: str) -> bool:
    lower = message.strip().lower()
    return bool(
        _FIX_ALL_MIGRATED_RE.search(lower)
        or _FIX_ALL_SCANNED_RE.search(lower)
        or _FIX_ALL_RE.search(lower)
    )


def _resolve_abs_path(repo_root: str, rel_or_abs: str) -> str:
    root = resolve_repo_root(repo_root)
    p = Path(rel_or_abs)
    if p.is_absolute():
        return str(p.resolve())
    return str((root / rel_or_abs).resolve())


def _collect_scan_issues(
    repo_root: str, max_files: int
) -> dict[str, str]:
    issues: dict[str, str] = {}
    py_files = [f for f in index_repo_files(repo_root, max_files=max_files) if f.endswith(".py")]
    for fpath in py_files:
        code = read_text_file.invoke({"path": fpath})
        if code.startswith("(missing"):
            continue
        val = validate_python_code.invoke({"code": code})
        if val != "OK":
            issues[fpath] = val
    return issues


def _scan_repo(
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    repo_root: str,
    max_files: int,
) -> Generator[dict[str, Any], None, None]:
    py_files = [f for f in index_repo_files(repo_root, max_files=max_files) if f.endswith(".py")]
    if not py_files:
        update_last_bot(history, "No `.py` files found to scan.")
        yield yield_chat(history, {"session_state": session_state})
        return

    issues: dict[str, str] = {}
    for fpath in py_files:
        code = read_text_file.invoke({"path": fpath})
        if code.startswith("(missing"):
            continue
        val = validate_python_code.invoke({"code": code})
        if val != "OK":
            issues[fpath] = val

    session_state["scan_issues"] = {
        str(Path(k).name): v[:200] for k, v in issues.items()
    }

    if not issues:
        update_last_bot(history, f"Scanned {len(py_files)} Python file(s). No issues found.")
    else:
        lines = [f"- `{Path(k).name}`: {v[:200]}" for k, v in list(issues.items())[:15]]
        update_last_bot(
            history,
            f"Found **{len(issues)}** issue(s):\n"
            + "\n".join(lines)
            + ("\n...(truncated)" if len(issues) > 15 else "")
            + "\n\nSend `fix @file.py`, `fix all migrated`, or `fix all scanned`.",
        )
    yield yield_chat(history, {"session_state": session_state})


def _strip_fix_prefix(text: str) -> str:
    target_hint = text.strip()
    for prefix in ("fix ", "debug ", "repair "):
        if target_hint.lower().startswith(prefix):
            return target_hint[len(prefix) :].strip()
    return target_hint


def _resolve_fix_all_targets(
    message: str,
    session_state: dict[str, Any],
    repo_root: str,
    active_files: list[str],
    max_files: int,
) -> tuple[list[str], str]:
    """Return absolute paths to fix for fix-all commands."""
    lower = message.strip().lower()
    root = resolve_repo_root(repo_root)

    if _FIX_ALL_MIGRATED_RE.search(lower):
        rels = list(session_state.get("migrated_py_paths") or [])
        if not rels:
            return [], "No migrated files in session. Convert files with Code Agent first."
        abs_paths = [_resolve_abs_path(repo_root, r) for r in rels[:max_files]]
        return abs_paths, ""

    if _FIX_ALL_SCANNED_RE.search(lower):
        scan = _collect_scan_issues(repo_root, max_files)
        if not scan:
            return [], "No scanned issues found. Run `scan` first."
        return list(scan.keys())[:max_files], ""

    # fix all — migrated first, else scan issues, else active_files
    migrated = list(session_state.get("migrated_py_paths") or [])
    if migrated:
        return [_resolve_abs_path(repo_root, r) for r in migrated[:max_files]], ""

    scan = _collect_scan_issues(repo_root, max_files)
    if scan:
        return list(scan.keys())[:max_files], ""

    if active_files:
        abs_paths, err = resolve_active_file_queries(
            repo_root, "", active_files, extensions=".py"
        )
        return abs_paths[:max_files], err or ""

    return [], "Nothing to fix. Try `scan`, select files, or migrate with Code Agent."


def _format_fix_result(name: str, result: dict[str, Any]) -> str:
    static = "OK" if result.get("static_ok") else "FAIL"
    if not result.get("static_ok"):
        runtime = "skipped"
    elif result.get("runtime_ok"):
        runtime = "OK"
    else:
        runtime = "FAIL"
    line = f"`{name}` — static: {static}, runtime: {runtime}"
    if not result.get("static_ok") or not result.get("runtime_ok"):
        err = (result.get("last_error") or "")[:120]
        if err:
            line += f" ({err})"
    return line


def _fix_one_file(
    target_path: str,
    session_state: dict[str, Any],
    max_retries: int,
    on_progress: Callable[[str], None] | None = None,
) -> tuple[bool, str, dict[str, Any] | None]:
    """Fix a single Python file; returns (queued, status_message, result_dict)."""
    code = read_text_file.invoke({"path": target_path})
    name = Path(target_path).name
    if code.startswith("(missing"):
        return False, f"Could not read `{name}`.", None

    result = validate_run_and_fix_python(
        code,
        f"Fix this Python file: {name}",
        max_retries,
        _merge,
        attach_ast,
        fix_python,
        initial_state,
        run_after_static=True,
        on_progress=on_progress,
    )
    fixed = result.get("code") or code

    if not result.get("changed") and result.get("static_ok") and result.get("runtime_ok"):
        return False, f"`{name}` — static: OK, runtime: OK (no changes needed).", result

    if fixed != code:
        queue_write(
            session_state,
            target_path,
            fixed,
            action="modify",
            original=code,
            name=name,
            python=fixed,
            language="python",
        )
        return True, _format_fix_result(name, result), result

    return False, _format_fix_result(name, result), result


def _fix_all(
    user_message: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    repo_root: str,
    max_files: int,
    max_retries: int,
) -> Generator[dict[str, Any], None, None]:
    active_files = session_state.get("active_files") or []
    target_paths, err = _resolve_fix_all_targets(
        user_message, session_state, repo_root, active_files, max_files
    )
    if err:
        update_last_bot(history, err)
        yield yield_chat(history, {"session_state": session_state})
        return

    if not target_paths:
        update_last_bot(history, "No Python files matched for batch fix.")
        yield yield_chat(history, {"session_state": session_state})
        return

    set_active_files(session_state, repo_root, target_paths)
    total = len(target_paths)
    update_last_bot(history, f"Batch fixing **{total}** file(s)...")
    yield yield_chat(history, {"session_state": session_state})

    queued = 0
    notes: list[str] = []
    for index, target_path in enumerate(target_paths, start=1):
        name = Path(target_path).name
        progress_msg = f"Fixing {index}/{total}: `{name}`..."

        def on_progress(msg: str, _n=name, _i=index, _t=total) -> None:
            update_last_bot(history, f"Fixing {_i}/{_t}: `{_n}` — {msg}")

        update_last_bot(history, progress_msg)
        yield yield_chat(history, {"session_state": session_state})

        did_queue, note, _ = _fix_one_file(
            target_path, session_state, max_retries, on_progress=on_progress
        )
        notes.append(note)
        if did_queue:
            queued += 1

    if queued:
        session_state["state"] = STATE_REVIEW
        summary = "\n".join(f"- {n}" for n in notes)
        append_bot(
            history,
            f"Batch complete. Queued **{queued}** fix(es):\n{summary}\n\nReview, then Keep All or Undo All.",
        )
        yield yield_chat(history, {"session_state": session_state, "show_action_buttons": True})
        return

    update_last_bot(history, "Batch complete:\n" + "\n".join(f"- {n}" for n in notes))
    yield yield_chat(history, {"session_state": session_state})


def _fix_target(
    user_message: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    repo_root: str,
    max_files: int,
    max_retries: int,
) -> Generator[dict[str, Any], None, None]:
    active_files = session_state.get("active_files") or []
    target_hint = _strip_fix_prefix(user_message)
    target_paths: list[str] = []

    if target_hint or active_files:
        abs_paths, err = resolve_active_file_queries(
            repo_root, target_hint, active_files, extensions=".py"
        )
        if err:
            update_last_bot(history, err)
            yield yield_chat(history, {"session_state": session_state})
            return
        target_paths = abs_paths

    if not target_paths and not target_hint and not active_files:
        py_files = [f for f in index_repo_files(repo_root, max_files=max_files) if f.endswith(".py")]
        for fpath in py_files:
            code = read_text_file.invoke({"path": fpath})
            if validate_python_code.invoke({"code": code}) != "OK":
                target_paths = [fpath]
                break

    if not target_paths:
        update_last_bot(history, "No Python file to fix. Try `scan` or `fix path/to/file.py`.")
        yield yield_chat(history, {"session_state": session_state})
        return

    set_active_files(session_state, repo_root, target_paths)
    update_last_bot(
        history, f"Fixing {len(target_paths)} selected Python file(s)..."
    )
    yield yield_chat(history, {"session_state": session_state})

    queued = 0
    notes: list[str] = []
    for target_path in target_paths:
        name = Path(target_path).name

        def on_progress(msg: str, _n=name) -> None:
            update_last_bot(history, f"Fixing `{_n}` — {msg}")

        did_queue, note, _ = _fix_one_file(
            target_path,
            session_state,
            max_retries,
            on_progress=on_progress,
        )
        notes.append(note)
        if did_queue:
            queued += 1
        yield yield_chat(history, {"session_state": session_state})

    if queued:
        session_state["state"] = STATE_REVIEW
        summary = "\n".join(f"- {n}" for n in notes)
        append_bot(
            history,
            f"Queued **{queued}** fix(es):\n{summary}\n\nReview, then Keep All or Undo All.",
        )
        yield yield_chat(history, {"session_state": session_state, "show_action_buttons": True})
        return

    update_last_bot(history, "\n".join(notes))
    yield yield_chat(history, {"session_state": session_state})
