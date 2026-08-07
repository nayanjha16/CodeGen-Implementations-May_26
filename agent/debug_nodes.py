"""LangGraph node functions for the Debug Agent."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Generator

from agent.debug_state import STATE_DEBUG_QA, STATE_INIT, STATE_REVIEW
from agent.debug_state import DebugAgentState
from agent.nodes import attach_ast, fix_python
from agent.repo_migrate import _merge
from agent.repo_utils import (
    append_bot,
    append_user,
    empty_session,
    extract_file_refs,
    format_sources_block,
    index_repo_files,
    load_context_sources,
    queue_write,
    resolve_active_file_queries,
    resolve_repo_root,
    set_active_files,
    trim_sources_for_prompt,
    update_last_bot,
    yield_chat,
)
from agent.state import initial_state
from agent.tools import read_text_file, run_python_dict, validate_python_code
from data.scripts.prompt_templates import (
    format_debug_diagnose_inference,
    format_debug_fix_context,
    format_debug_followup_inference,
)

STATE_INIT = "init"
STATE_REVIEW = "review"
STATE_DEBUG_QA = "debug_qa"

_FIX_ALL_MIGRATED_RE = re.compile(
    r"\bfix\s+(all\s+)?(migrated|converted)\b", re.IGNORECASE
)
_FIX_ALL_SCANNED_RE = re.compile(r"\bfix\s+all\s+scanned\b", re.IGNORECASE)
_FIX_ALL_RE = re.compile(r"\bfix\s+all\b", re.IGNORECASE)
_FIX_INTENT_RE = re.compile(r"\b(fix|repair|patch)\b", re.IGNORECASE)


def _codegen_generate(prompt: str, **kwargs: Any) -> str:
    from agent.repo_debug_chat import codegen_generate

    return codegen_generate(prompt, **kwargs)


def _validate_run_and_fix_python(*args: Any, **kwargs: Any):
    from agent.repo_debug_chat import validate_run_and_fix_python

    return validate_run_and_fix_python(*args, **kwargs)


def _ensure_session(state: DebugAgentState) -> dict[str, Any]:
    from agent.repo_utils import empty_session

    session = state.get("session_state") or {}
    if not session:
        session = empty_session(state.get("repo_root", ""))
    if state.get("repo_root"):
        session["repo_root"] = state["repo_root"]
    return session


def check_repo(state: DebugAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = (session.get("repo_root") or "").strip()
    if not root:
        return {
            "done": True,
            "answer": "Set the **Project root** path above, then describe what to debug.",
        }
    try:
        resolve_repo_root(root)
    except FileNotFoundError:
        return {"done": True, "answer": f"Repo path not found: `{root}`"}
    return {"session_state": session}


def route_command(state: DebugAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    user_message = state.get("user_message", "")
    msg = user_message.strip().lower()
    active_files = session.get("active_files") or []

    if msg.startswith("scan") or msg == "scan for errors":
        session["state"] = STATE_INIT
        return {"route": "scan", "session_state": session, "statuses": ["Scanning Python files..."]}

    if _is_fix_all_command(user_message):
        return {"route": "fix_all", "statuses": ["Batch fixing..."]}

    if (
        session.get("state") == STATE_DEBUG_QA
        and session.get("sources_cache")
        and not _has_new_file_selection(session, active_files, user_message)
    ):
        return {"route": "followup", "statuses": ["Continuing debug session..."]}

    status = (
        "Diagnosing before fix..." if _is_fix_intent(user_message) else "Diagnosing..."
    )
    return {"route": "diagnose", "statuses": [status]}


def route_command_edge(state: DebugAgentState) -> str:
    if state.get("done"):
        return "end"
    return str(state.get("route", "diagnose"))


def scan_repo_node(state: DebugAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = session.get("repo_root", "")
    max_files = state.get("max_files", 20)
    py_files = [
        f for f in index_repo_files(root, max_files=max_files) if f.endswith(".py")
    ]
    if not py_files:
        return {"done": True, "answer": "No `.py` files found to scan.", "session_state": session}

    issues: dict[str, str] = {}
    for fpath in py_files:
        code = read_text_file.invoke({"path": fpath})
        if code.startswith("(missing"):
            continue
        val = validate_python_code.invoke({"code": code})
        if val != "OK":
            issues[fpath] = val

    session["scan_issues"] = {
        str(Path(k).name): v[:200] for k, v in issues.items()
    }

    if not issues:
        answer = f"Scanned {len(py_files)} Python file(s). No issues found."
    else:
        lines = [f"- `{Path(k).name}`: {v[:200]}" for k, v in list(issues.items())[:15]]
        answer = (
            f"Found **{len(issues)}** issue(s):\n"
            + "\n".join(lines)
            + ("\n...(truncated)" if len(issues) > 15 else "")
            + "\n\nSend `fix @file.py`, `fix all migrated`, or `fix all scanned`."
        )
    return {"done": True, "answer": answer, "session_state": session}


def fix_all_node(state: DebugAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = session.get("repo_root", "")
    user_message = state.get("user_message", "")
    max_files = state.get("max_files", 20)
    max_retries = state.get("max_retries", 3)
    active_files = session.get("active_files") or []
    debug_context = _extract_debug_context(user_message)
    target_paths, err = _resolve_fix_all_targets(
        user_message, session, root, active_files, max_files
    )
    if err:
        return {"done": True, "answer": err, "session_state": session}
    if not target_paths:
        return {"done": True, "answer": "No Python files matched for batch fix.", "session_state": session}

    set_active_files(session, root, target_paths)
    statuses = [f"Batch fixing **{len(target_paths)}** file(s)..."]
    queued = 0
    notes: list[str] = []
    for index, target_path in enumerate(target_paths, start=1):
        name = Path(target_path).name
        statuses.append(f"Fixing {index}/{len(target_paths)}: `{name}`...")
        code = read_text_file.invoke({"path": target_path})
        evidence = _collect_file_evidence(code) if not code.startswith("(missing") else {}
        did_queue, note, _ = _fix_one_file(
            target_path,
            session,
            max_retries,
            debug_context=debug_context,
            evidence=evidence,
            allow_behavioral_fix=bool(debug_context.strip()),
        )
        notes.append(note)
        if did_queue:
            queued += 1

    if queued:
        session["state"] = STATE_REVIEW
        summary = "\n".join(f"- {n}" for n in notes)
        answer = f"Batch complete. Queued **{queued}** fix(es):\n{summary}\n\nReview, then Keep All or Undo All."
        return {
            "done": True,
            "answer": answer,
            "session_state": session,
            "show_action_buttons": True,
            "statuses": statuses,
        }
    return {
        "done": True,
        "answer": "Batch complete:\n" + "\n".join(f"- {n}" for n in notes),
        "session_state": session,
        "statuses": statuses,
    }


def diagnose_node(state: DebugAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = session.get("repo_root", "")
    user_message = state.get("user_message", "")
    max_files = state.get("max_files", 20)
    debug_context = _extract_debug_context(user_message)
    problem = debug_context or user_message.strip() or "Review this file for bugs."

    target_paths, err = _resolve_target_paths(user_message, session, root, max_files)
    if err:
        return {"done": True, "answer": err, "session_state": session}
    if not target_paths:
        return {
            "done": True,
            "answer": "No Python file to debug. Select files, mention `@path/to/file.py`, or run `scan`.",
            "session_state": session,
        }

    set_active_files(session, root, target_paths)
    sources, files, load_err = load_context_sources(
        root, user_message, session.get("active_files") or [], max_files=max_files
    )
    if load_err:
        return {"done": True, "answer": load_err, "session_state": session}

    if not sources:
        sources = []
        for path in target_paths:
            code = read_text_file.invoke({"path": path})
            if code.startswith("(missing"):
                continue
            sources.append({
                "name": Path(path).name,
                "language": "python",
                "snippet": code,
                "ast_summary": "",
            })

    focused = trim_sources_for_prompt(sources)
    evidence_by_path: dict[str, dict[str, str]] = {}
    statuses: list[str] = []
    for source in focused:
        path_key = next(
            (p for p in target_paths if Path(p).name == source["name"]),
            source["name"],
        )
        evidence_by_path[path_key] = _collect_file_evidence(source.get("snippet") or "")

    session["file_index"] = list(session.get("active_files") or [])
    session["sources_cache"] = focused
    session["last_evidence"] = {Path(k).name: v for k, v in evidence_by_path.items()}
    session["state"] = STATE_DEBUG_QA

    sections: list[str] = []
    any_mechanical = False
    total = len(focused)
    for index, source in enumerate(focused, start=1):
        path_key = next(
            (p for p in target_paths if Path(p).name == source["name"]),
            source["name"],
        )
        evidence = evidence_by_path.get(path_key, {})
        if _has_mechanical_errors(evidence):
            any_mechanical = True
        statuses.extend([
            f"Checking validation for `{source['name']}` ({index}/{total})...",
            f"Diagnosing `{source['name']}` ({index}/{total})...",
        ])
        diagnosis = _diagnose_one_file(root, source, problem, evidence)
        body = diagnosis or "(No diagnosis generated.)"
        if total == 1:
            sections.append(body)
        else:
            sections.append(f"### {Path(source['name']).name}\n{body}")

    diagnosis_text = _format_diagnosis_block("\n\n".join(sections))
    session["last_diagnosis"] = diagnosis_text
    result: dict[str, Any] = {
        "session_state": session,
        "target_paths": target_paths,
        "evidence_by_path": evidence_by_path,
        "debug_context": debug_context,
        "diagnosis_text": diagnosis_text,
        "any_mechanical": any_mechanical,
        "allow_behavioral_fix": _is_fix_intent(user_message),
        "statuses": statuses,
        "answer": diagnosis_text,
    }
    if any_mechanical:
        result["route"] = "fix"
    else:
        result["done"] = True
        result["append_answer"] = True
        if _is_fix_intent(user_message):
            result["followup_prompt"] = (
                "Static/runtime OK. Say **`fix it`** to attempt a behavioral patch based on your description."
            )
        else:
            result["followup_prompt"] = (
                "Say **`fix it`** to apply a patch, or paste a traceback for deeper analysis."
            )
    return result


def route_after_diagnose(state: DebugAgentState) -> str:
    if state.get("route") == "fix":
        return "fix"
    return "end"


def fix_node(state: DebugAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = session.get("repo_root", "")
    user_message = state.get("user_message", "")
    max_files = state.get("max_files", 20)
    max_retries = state.get("max_retries", 3)
    target_paths = state.get("target_paths") or []
    evidence_by_path = state.get("evidence_by_path") or {}
    debug_context = state.get("debug_context") or _extract_debug_context(user_message)
    diagnosis_text = state.get("diagnosis_text") or session.get("last_diagnosis") or ""
    allow_behavioral = bool(state.get("allow_behavioral_fix"))

    if not target_paths:
        target_paths, err = _resolve_target_paths(user_message, session, root, max_files)
        if err:
            return {"done": True, "answer": err, "session_state": session}
    if not target_paths:
        return {
            "done": True,
            "answer": "No Python file to fix. Try `scan` or `fix path/to/file.py`.",
            "session_state": session,
        }

    set_active_files(session, root, target_paths)
    statuses = ["Applying fix..."]
    queued = 0
    notes: list[str] = []
    for target_path in target_paths:
        name = Path(target_path).name
        evidence = evidence_by_path.get(target_path) or evidence_by_path.get(name)
        if evidence is None:
            code = read_text_file.invoke({"path": target_path})
            evidence = _collect_file_evidence(code) if not code.startswith("(missing") else {}
        did_queue, note, _ = _fix_one_file(
            target_path,
            session,
            max_retries,
            debug_context=debug_context,
            evidence=evidence,
            allow_behavioral_fix=allow_behavioral,
            diagnosis_text=diagnosis_text,
        )
        notes.append(note)
        if did_queue:
            queued += 1

    if queued:
        session["state"] = STATE_REVIEW
        summary = "\n".join(f"- {n}" for n in notes)
        answer = _format_fix_result_block(
            [f"Queued **{queued}** fix(es):", summary, "Review, then Keep All or Undo All."]
        )
        return {
            "done": True,
            "answer": answer,
            "session_state": session,
            "show_action_buttons": True,
            "append_answer": True,
        }
    return {
        "done": True,
        "answer": _format_fix_result_block(notes) if notes else "\n".join(notes),
        "session_state": session,
        "append_answer": bool(notes),
    }


def followup_node(state: DebugAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = session.get("repo_root", "")
    user_message = state.get("user_message", "")
    max_files = state.get("max_files", 20)
    max_retries = state.get("max_retries", 3)
    debug_context = _extract_debug_context(user_message)
    problem = debug_context or user_message.strip()

    if _is_fix_intent(user_message):
        root_path = resolve_repo_root(root)
        target_paths = [
            str((root_path / rel).resolve()) for rel in (session.get("file_index") or [])
        ]
        if not target_paths:
            target_paths, _ = _resolve_target_paths(user_message, session, root, max_files)
        evidence_by_path = {}
        for path in target_paths:
            code = read_text_file.invoke({"path": path})
            cached = (session.get("last_evidence") or {}).get(Path(path).name)
            evidence_by_path[path] = cached if isinstance(cached, dict) else _collect_file_evidence(code)
        return {
            "route": "fix",
            "target_paths": target_paths,
            "evidence_by_path": evidence_by_path,
            "debug_context": problem,
            "allow_behavioral_fix": True,
            "diagnosis_text": session.get("last_diagnosis") or "",
            "session_state": session,
        }

    sources = trim_sources_for_prompt(session.get("sources_cache") or [])
    cached_evidence = session.get("last_evidence") or {}
    sections: list[str] = []
    for source in sources:
        raw_evidence = cached_evidence.get(Path(source["name"]).name)
        if isinstance(raw_evidence, dict):
            evidence = _format_evidence_block(raw_evidence)
        elif isinstance(raw_evidence, str):
            evidence = raw_evidence
        else:
            evidence = _format_evidence_block(
                _collect_file_evidence(source.get("snippet") or "")
            )
        prompt = format_debug_followup_inference(
            repo_root=root,
            file_name=source["name"],
            source=format_sources_block([source], for_doc=True),
            problem=problem,
            evidence=evidence,
        )
        answer = _codegen_generate(prompt, response_type="doc", max_new_tokens=768)
        body = answer or "(No answer generated.)"
        if len(sources) == 1:
            sections.append(body)
        else:
            sections.append(f"### {Path(source['name']).name}\n{body}")

    return {
        "done": True,
        "answer": "\n\n".join(sections),
        "append_answer": True,
        "followup_prompt": "Say **`fix it`** to apply a patch based on this analysis.",
        "session_state": session,
    }


def route_followup_edge(state: DebugAgentState) -> str:
    if state.get("route") == "fix":
        return "fix"
    return "end"


# --- legacy generator helpers (used by tests via repo_debug_chat re-exports) ---
def _is_fix_all_command(message: str) -> bool:
    lower = message.strip().lower()
    return bool(
        _FIX_ALL_MIGRATED_RE.search(lower)
        or _FIX_ALL_SCANNED_RE.search(lower)
        or _FIX_ALL_RE.search(lower)
    )


def _is_fix_intent(message: str) -> bool:
    if _is_fix_all_command(message):
        return True
    return bool(_FIX_INTENT_RE.search(message))


def _has_new_file_selection(
    session_state: dict[str, Any],
    active_files: list[str],
    message: str,
) -> bool:
    cached = session_state.get("file_index") or []
    if active_files and set(active_files) != set(cached):
        return True
    refs = extract_file_refs(message)
    if refs and not cached:
        return True
    if refs:
        cached_names = {Path(p).name.lower() for p in cached}
        for ref in refs:
            if Path(ref).name.lower() not in cached_names and ref.lower() not in {
                p.lower() for p in cached
            }:
                return True
    return False


def _extract_debug_context(message: str) -> str:
    """Return the problem description after stripping commands and file refs."""
    text = message.strip()
    for prefix in ("debug ", "fix ", "repair ", "patch ", "scan "):
        if text.lower().startswith(prefix):
            text = text[len(prefix) :].strip()
    for ref in extract_file_refs(text):
        text = re.sub(r"@?" + re.escape(ref), "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b[\w./-]+\.py\b", "", text, flags=re.IGNORECASE)
    text = re.sub(
        r"\b(selected|this file|the file|it)\b", "", text, flags=re.IGNORECASE
    )
    text = re.sub(r"\s+", " ", text).strip(" ,:-")
    return text


def _resolve_abs_path(repo_root: str, rel_or_abs: str) -> str:
    root = resolve_repo_root(repo_root)
    p = Path(rel_or_abs)
    if p.is_absolute():
        return str(p.resolve())
    return str((root / rel_or_abs).resolve())


def _collect_file_evidence(code: str) -> dict[str, str]:
    evidence: dict[str, str] = {}
    static = validate_python_code.invoke({"code": code})
    evidence["static"] = static
    if static == "OK":
        result = run_python_dict(code, timeout=10)
        stdout = (result.get("stdout") or "").strip()
        stderr = (result.get("stderr") or result.get("error") or "").strip()
        passed = bool(result.get("passed") or result.get("exit_ok"))
        evidence["runtime_ok"] = str(passed)
        if stdout:
            evidence["stdout"] = stdout[:500]
        if stderr:
            evidence["stderr"] = stderr[:500]
    return evidence


def _format_evidence_block(evidence: dict[str, str]) -> str:
    lines: list[str] = []
    static = evidence.get("static", "OK")
    lines.append(f"Static validation: {static}")
    if "runtime_ok" in evidence:
        lines.append(f"Runtime passed: {evidence['runtime_ok']}")
    if evidence.get("stdout"):
        lines.append(f"stdout: {evidence['stdout']}")
    if evidence.get("stderr"):
        lines.append(f"stderr: {evidence['stderr']}")
    return "\n".join(lines)


def _has_mechanical_errors(evidence: dict[str, str]) -> bool:
    if evidence.get("static", "OK") != "OK":
        return True
    return evidence.get("runtime_ok") == "False"


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
    for prefix in ("fix ", "debug ", "repair ", "patch "):
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
    notes = result.get("trace_notes") or []
    if notes:
        line += "\n  - " + "\n  - ".join(notes)
    return line


def _strip_diagnosis_header(diagnosis_text: str) -> str:
    return re.sub(r"^### Diagnosis\s*\n?", "", (diagnosis_text or "").strip(), count=1)


def _build_fix_context(
    debug_context: str,
    evidence: dict[str, str] | None,
    file_name: str,
    *,
    diagnosis_text: str = "",
) -> str:
    base = format_debug_fix_context(
        debug_context,
        _format_evidence_block(evidence or {}),
        file_name=file_name,
    )
    prior = _strip_diagnosis_header(diagnosis_text)
    if prior:
        base = f"{base}\n\n### Prior diagnosis\n{prior}"
    return base


def _format_diagnosis_block(diagnosis_text: str) -> str:
    body = (diagnosis_text or "").strip() or "(No diagnosis generated.)"
    return f"### Diagnosis\n{body}"


def _format_fix_result_block(notes: list[str]) -> str:
    body = "\n".join(notes).strip()
    return f"### Fix result\n{body}"


def _no_changes_message(name: str) -> str:
    return (
        f"`{name}` — static: OK, runtime: OK. "
        "No code changes needed — static and runtime checks passed."
    )


def _attempt_behavioral_fix(
    code: str,
    fix_context: str,
    max_retries: int,
) -> tuple[str, dict[str, Any]]:
    """Try one LLM fix when static/runtime pass but the user reported a bug."""
    fix_state = dict(
        initial_state(f"Fix the python code.\n{fix_context}", unit="auto")
    )
    fix_state["python_code"] = code
    fix_state["stderr"] = fix_context
    fix_state["max_retries"] = max_retries
    fix_state = _merge(fix_state, attach_ast(fix_state))
    fix_state = _merge(fix_state, fix_python(fix_state))
    fixed = fix_state.get("python_code") or code
    val = validate_python_code.invoke({"code": fixed})
    runtime_ok = False
    if val == "OK":
        run_result = run_python_dict(fixed, timeout=10)
        runtime_ok = bool(run_result.get("passed") or run_result.get("exit_ok"))
    return fixed, {
        "code": fixed,
        "static_ok": val == "OK",
        "runtime_ok": runtime_ok,
        "changed": fixed != code,
        "last_error": "" if val == "OK" and runtime_ok else val,
        "trace_notes": ["Behavioral fix based on user description."],
    }


def _fix_one_file(
    target_path: str,
    session_state: dict[str, Any],
    max_retries: int,
    on_progress: Callable[[str], None] | None = None,
    *,
    debug_context: str = "",
    evidence: dict[str, str] | None = None,
    allow_behavioral_fix: bool = False,
    diagnosis_text: str = "",
) -> tuple[bool, str, dict[str, Any] | None]:
    """Fix a single Python file; returns (queued, status_message, result_dict)."""
    code = read_text_file.invoke({"path": target_path})
    name = Path(target_path).name
    if code.startswith("(missing"):
        return False, f"Could not read `{name}`.", None

    if not diagnosis_text.strip():
        diagnosis_text = session_state.get("last_diagnosis") or ""

    fix_context = _build_fix_context(
        debug_context, evidence, name, diagnosis_text=diagnosis_text
    )
    result = _validate_run_and_fix_python(
        code,
        fix_context,
        max_retries,
        _merge,
        attach_ast,
        fix_python,
        initial_state,
        run_after_static=True,
        on_progress=on_progress,
    )
    fixed = result.get("code") or code

    if (
        not result.get("changed")
        and result.get("static_ok")
        and result.get("runtime_ok")
    ):
        if allow_behavioral_fix and debug_context.strip():
            fixed, result = _attempt_behavioral_fix(code, fix_context, max_retries)
            if fixed != code and result.get("static_ok") and result.get("runtime_ok"):
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
                return (
                    True,
                    f"`{name}` — fix applied based on your description.",
                    result,
                )
            return (
                False,
                _no_changes_message(name),
                result,
            )
        return False, _no_changes_message(name), result

    if (
        fixed != code
        and result.get("static_ok")
        and result.get("runtime_ok", True)
    ):
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
    debug_context = _extract_debug_context(user_message)
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

        code = read_text_file.invoke({"path": target_path})
        evidence = _collect_file_evidence(code) if not code.startswith("(missing") else {}
        did_queue, note, _ = _fix_one_file(
            target_path,
            session_state,
            max_retries,
            on_progress=on_progress,
            debug_context=debug_context,
            evidence=evidence,
            allow_behavioral_fix=bool(debug_context.strip()),
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


def _resolve_target_paths(
    user_message: str,
    session_state: dict[str, Any],
    repo_root: str,
    max_files: int,
) -> tuple[list[str], str | None]:
    active_files = session_state.get("active_files") or []
    target_hint = _strip_fix_prefix(user_message)
    target_paths: list[str] = []

    if target_hint or active_files:
        abs_paths, err = resolve_active_file_queries(
            repo_root, target_hint, active_files, extensions=".py"
        )
        if err:
            return [], err
        target_paths = abs_paths

    if not target_paths and not target_hint and not active_files:
        py_files = [f for f in index_repo_files(repo_root, max_files=max_files) if f.endswith(".py")]
        for fpath in py_files:
            code = read_text_file.invoke({"path": fpath})
            if validate_python_code.invoke({"code": code}) != "OK":
                target_paths = [fpath]
                break

    if not target_paths:
        return [], None
    return target_paths, None


def _diagnose_one_file(
    repo_root: str,
    source: dict[str, str],
    problem: str,
    evidence: dict[str, str],
) -> str:
    prompt = format_debug_diagnose_inference(
        repo_root=repo_root,
        file_name=source["name"],
        source=format_sources_block([source], for_doc=True),
        problem=problem,
        evidence=_format_evidence_block(evidence),
    )
    return _codegen_generate(prompt, response_type="doc", max_new_tokens=768) or ""


def _diagnose_target(
    user_message: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    repo_root: str,
    max_files: int,
    max_retries: int,
) -> Generator[dict[str, Any], None, None]:
    debug_context = _extract_debug_context(user_message)
    problem = debug_context or user_message.strip() or "Review this file for bugs."

    target_paths, err = _resolve_target_paths(
        user_message, session_state, repo_root, max_files
    )
    if err:
        update_last_bot(history, err)
        yield yield_chat(history, {"session_state": session_state})
        return

    if not target_paths:
        update_last_bot(
            history,
            "No Python file to debug. Select files, mention `@path/to/file.py`, or run `scan`.",
        )
        yield yield_chat(history, {"session_state": session_state})
        return

    set_active_files(session_state, repo_root, target_paths)
    sources, files, load_err = load_context_sources(
        repo_root, user_message, session_state.get("active_files") or [], max_files=max_files
    )
    if load_err:
        update_last_bot(history, load_err)
        yield yield_chat(history, {"session_state": session_state})
        return

    if not sources:
        sources = []
        for path in target_paths:
            code = read_text_file.invoke({"path": path})
            if code.startswith("(missing"):
                continue
            sources.append(
                {
                    "name": Path(path).name,
                    "language": "python",
                    "snippet": code,
                    "ast_summary": "",
                }
            )
        files = target_paths

    focused = trim_sources_for_prompt(sources)
    evidence_by_path: dict[str, dict[str, str]] = {}
    for source in focused:
        path_key = next(
            (p for p in target_paths if Path(p).name == source["name"]),
            source["name"],
        )
        evidence_by_path[path_key] = _collect_file_evidence(source.get("snippet") or "")

    session_state["file_index"] = list(session_state.get("active_files") or [])
    session_state["sources_cache"] = focused
    session_state["last_evidence"] = {
        Path(k).name: v for k, v in evidence_by_path.items()
    }
    session_state["state"] = STATE_DEBUG_QA

    sections: list[str] = []
    any_mechanical = False
    total = len(focused)
    for index, source in enumerate(focused, start=1):
        path_key = next(
            (p for p in target_paths if Path(p).name == source["name"]),
            source["name"],
        )
        evidence = evidence_by_path.get(path_key, {})
        if _has_mechanical_errors(evidence):
            any_mechanical = True

        update_last_bot(
            history,
            f"Checking validation for `{source['name']}` ({index}/{total})...",
        )
        yield yield_chat(history, {"session_state": session_state})

        update_last_bot(
            history,
            f"Diagnosing `{source['name']}` ({index}/{total})...",
        )
        yield yield_chat(history, {"session_state": session_state})

        diagnosis = _diagnose_one_file(repo_root, source, problem, evidence)
        body = diagnosis or "(No diagnosis generated.)"
        if total == 1:
            sections.append(body)
        else:
            sections.append(f"### {Path(source['name']).name}\n{body}")

    diagnosis_text = "\n\n".join(sections)
    labeled_diagnosis = _format_diagnosis_block(diagnosis_text)
    session_state["last_diagnosis"] = labeled_diagnosis
    update_last_bot(history, labeled_diagnosis)
    yield yield_chat(history, {"session_state": session_state})

    should_fix = any_mechanical
    if should_fix:
        append_bot(history, "Applying fix...")
        yield yield_chat(history, {"session_state": session_state})
        yield from _fix_target(
            user_message,
            history,
            session_state,
            repo_root,
            max_files,
            max_retries,
            debug_context=debug_context,
            evidence_by_path=evidence_by_path,
            target_paths=target_paths,
            allow_behavioral_fix=_is_fix_intent(user_message),
            append_diagnosis=False,
            diagnosis_text=labeled_diagnosis,
        )
        return

    if _is_fix_intent(user_message) and not any_mechanical:
        append_bot(
            history,
            "Static/runtime OK. Say **`fix it`** to attempt a behavioral patch based on your description.",
        )
    else:
        append_bot(
            history,
            "Say **`fix it`** to apply a patch, or paste a traceback for deeper analysis.",
        )
    yield yield_chat(history, {"session_state": session_state})


def _debug_followup(
    user_message: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    repo_root: str,
    max_files: int,
    max_retries: int,
) -> Generator[dict[str, Any], None, None]:
    debug_context = _extract_debug_context(user_message)
    problem = debug_context or user_message.strip()
    sources = trim_sources_for_prompt(session_state.get("sources_cache") or [])
    cached_evidence = session_state.get("last_evidence") or {}

    if _is_fix_intent(user_message):
        root_path = resolve_repo_root(repo_root)
        target_paths = [str((root_path / rel).resolve()) for rel in (session_state.get("file_index") or [])]
        if not target_paths:
            target_paths, _ = _resolve_target_paths(
                user_message, session_state, repo_root, max_files
            )
        evidence_by_path = {}
        for path in target_paths:
            code = read_text_file.invoke({"path": path})
            evidence_by_path[path] = cached_evidence.get(
                Path(path).name, _collect_file_evidence(code)
            )
        yield from _fix_target(
            user_message,
            history,
            session_state,
            repo_root,
            max_files,
            max_retries,
            debug_context=problem,
            evidence_by_path=evidence_by_path,
            target_paths=target_paths,
            allow_behavioral_fix=True,
            append_diagnosis=False,
            diagnosis_text=session_state.get("last_diagnosis") or "",
        )
        return

    sections: list[str] = []
    for source in sources:
        raw_evidence = cached_evidence.get(Path(source["name"]).name)
        if isinstance(raw_evidence, dict):
            evidence = _format_evidence_block(raw_evidence)
        elif isinstance(raw_evidence, str):
            evidence = raw_evidence
        else:
            evidence = _format_evidence_block(
                _collect_file_evidence(source.get("snippet") or "")
            )

        prompt = format_debug_followup_inference(
            repo_root=repo_root,
            file_name=source["name"],
            source=format_sources_block([source], for_doc=True),
            problem=problem,
            evidence=evidence,
        )
        answer = codegen_generate(prompt, response_type="doc", max_new_tokens=768)
        body = answer or "(No answer generated.)"
        if len(sources) == 1:
            sections.append(body)
        else:
            sections.append(f"### {Path(source['name']).name}\n{body}")

    update_last_bot(history, "\n\n".join(sections))
    append_bot(
        history,
        "Say **`fix it`** to apply a patch based on this analysis.",
    )
    yield yield_chat(history, {"session_state": session_state})


def _fix_target(
    user_message: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    repo_root: str,
    max_files: int,
    max_retries: int,
    *,
    debug_context: str = "",
    evidence_by_path: dict[str, dict[str, str]] | None = None,
    target_paths: list[str] | None = None,
    allow_behavioral_fix: bool = False,
    append_diagnosis: bool = True,
    diagnosis_text: str = "",
) -> Generator[dict[str, Any], None, None]:
    if debug_context == "":
        debug_context = _extract_debug_context(user_message)

    if target_paths is None:
        target_paths, err = _resolve_target_paths(
            user_message, session_state, repo_root, max_files
        )
        if err:
            update_last_bot(history, err)
            yield yield_chat(history, {"session_state": session_state})
            return

    if not target_paths:
        update_last_bot(history, "No Python file to fix. Try `scan` or `fix path/to/file.py`.")
        yield yield_chat(history, {"session_state": session_state})
        return

    set_active_files(session_state, repo_root, target_paths)
    if append_diagnosis:
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

        if append_diagnosis:
            update_last_bot(history, f"Applying fix to `{name}`...")
            yield yield_chat(history, {"session_state": session_state})

        evidence = (evidence_by_path or {}).get(target_path)
        if evidence is None and evidence_by_path:
            evidence = evidence_by_path.get(name)
        if evidence is None:
            code = read_text_file.invoke({"path": target_path})
            evidence = _collect_file_evidence(code) if not code.startswith("(missing") else {}

        did_queue, note, _ = _fix_one_file(
            target_path,
            session_state,
            max_retries,
            on_progress=on_progress,
            debug_context=debug_context,
            evidence=evidence,
            allow_behavioral_fix=allow_behavioral_fix,
            diagnosis_text=diagnosis_text,
        )
        notes.append(note)
        if did_queue:
            queued += 1
        yield yield_chat(history, {"session_state": session_state})

    if queued:
        session_state["state"] = STATE_REVIEW
        summary = "\n".join(f"- {n}" for n in notes)
        fix_block = _format_fix_result_block(
            [f"Queued **{queued}** fix(es):", summary, "Review, then Keep All or Undo All."]
        )
        append_bot(history, fix_block)
        yield yield_chat(history, {"session_state": session_state, "show_action_buttons": True})
        return

    fix_block = _format_fix_result_block(notes)
    append_bot(history, fix_block)
    yield yield_chat(history, {"session_state": session_state})
