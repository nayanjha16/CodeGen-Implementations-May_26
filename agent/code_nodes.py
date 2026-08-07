"""LangGraph node functions for the Code Agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.code_state import STATE_ASK_DEPS, STATE_CONVERTING, STATE_REVIEW
from agent.code_state import CodeAgentState
from agent.repo_migrate import _merge
from agent.repo_utils import (
    add_python_comments,
    build_codegen_few_shot,
    code_task_language_note,
    detect_code_task,
    empty_session,
    queue_write,
    record_migrated_py,
    resolve_active_file_queries,
    resolve_repo_root,
    set_active_files,
    strip_task_prefix,
    suggest_generated_path,
    validate_and_fix_python,
)
from agent.state import initial_state
from agent.tools import find_local_java_dependencies, list_java_files, read_text_file
from data.scripts.prompt_templates import (
    format_java2py_inference,
    format_nl2java_inference,
    format_nl2py_inference,
)

TASK_LABELS = {
    "gen_python": "generating Python",
    "gen_java": "generating Java",
    "migrate": "converting Java to Python",
}


def _codegen_generate(prompt: str, **kwargs: Any) -> str:
    from agent.repo_code_chat import codegen_generate

    return codegen_generate(prompt, **kwargs)


def _validate_and_fix_python(code: str, context: str, max_retries: int) -> str:
    from agent.repo_code_chat import (
        add_python_comments as _add_comments,
        attach_ast,
        fix_python,
        validate_and_fix_python,
    )

    fixed = validate_and_fix_python(
        code,
        context,
        max_retries,
        _merge,
        attach_ast,
        fix_python,
        initial_state,
    )
    return _add_comments(fixed)


def _ensure_session(state: CodeAgentState) -> dict[str, Any]:
    session = state.get("session_state") or {}
    if not session:
        session = empty_session(state.get("repo_root", ""))
    if state.get("repo_root"):
        session["repo_root"] = state["repo_root"]
    return session


def route_session(state: CodeAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    current = session.get("state", "init")
    if current == STATE_CONVERTING:
        return {"done": True, "route": "converting"}
    if current == STATE_ASK_DEPS:
        return {"route": "ask_deps"}
    return {"route": "init"}


def route_session_edge(state: CodeAgentState) -> str:
    route = state.get("route", "init")
    if state.get("done"):
        return "end"
    return route


def handle_deps_reply(state: CodeAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    ans = state.get("user_message", "").strip().lower()
    statuses = ["Preparing conversion..."]
    if ans in ("yes", "y", "sure", "ok", "convert"):
        session["pending_files"].extend(session.get("deps_found", []))
        statuses.append(
            f"Including dependencies. Converting {len(session['pending_files'])} file(s)..."
        )
    else:
        statuses.append(
            f"Skipping dependencies. Converting {len(session['pending_files'])} file(s)..."
        )
    session["state"] = STATE_CONVERTING
    return {
        "session_state": session,
        "statuses": statuses,
        "route": "convert",
        "convert_index": 0,
    }


def check_repo(state: CodeAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = (session.get("repo_root") or "").strip()
    if not root:
        return {
            "done": True,
            "answer": "Set the **Project root** path above, then send a code request.",
        }
    try:
        resolve_repo_root(root)
    except FileNotFoundError:
        return {"done": True, "answer": f"Repo path not found: `{root}`"}
    return {"session_state": session}


def detect_task(state: CodeAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    active_files = session.get("active_files") or []
    root = session.get("repo_root", "")
    user_message = state.get("user_message", "")
    task = detect_code_task(user_message, active_files, repo_root=root)
    body = strip_task_prefix(user_message)
    return {
        "task": task,
        "body": body,
        "session_state": session,
    }


def route_task(state: CodeAgentState) -> str:
    return str(state.get("task", "migrate"))


def generate_python(state: CodeAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = session.get("repo_root", "")
    spec = state.get("body") or state.get("user_message", "")
    max_retries = state.get("max_retries", 3)
    active_files = session.get("active_files") or []
    statuses = ["Generating Python...", "Adding comments..."]

    few_shot = build_codegen_few_shot(
        root, spec, language="python", active_files=active_files
    )
    prompt = format_nl2py_inference(spec, few_shot=few_shot)
    python_code = _codegen_generate(prompt, response_type="code")
    python_code = _validate_and_fix_python(
        python_code, f"Original request: {spec}", max_retries
    )
    python_code = add_python_comments(python_code)

    out_path = suggest_generated_path(
        root, ".py", spec, python_code, active_files=active_files
    )
    queue_write(
        session,
        str(out_path),
        python_code,
        action="create",
        name=out_path.name,
        python=python_code,
        language="python",
    )
    record_migrated_py(session, root, str(out_path))
    session["state"] = STATE_REVIEW
    answer = (
        f"Generated `{out_path.name}`. Click **Review**, then **Keep All** or **Undo All**."
    )
    return {
        "answer": answer,
        "session_state": session,
        "statuses": statuses,
        "done": True,
        "show_action_buttons": True,
        "append_answer": True,
    }


def generate_java(state: CodeAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = session.get("repo_root", "")
    spec = state.get("body") or state.get("user_message", "")
    active_files = session.get("active_files") or []

    few_shot = build_codegen_few_shot(
        root, spec, language="java", active_files=active_files
    )
    prompt = format_nl2java_inference(spec, few_shot=few_shot)
    java_code = _codegen_generate(prompt, response_type="code")
    out_path = suggest_generated_path(
        root, ".java", spec, java_code, active_files=active_files
    )
    queue_write(
        session,
        str(out_path),
        java_code,
        action="create",
        name=out_path.name,
        java=java_code,
        language="java",
    )
    session["state"] = STATE_REVIEW
    answer = (
        f"Generated `{out_path.name}`. Click **Review**, then **Keep All** or **Undo All**."
    )
    return {
        "answer": answer,
        "session_state": session,
        "statuses": ["Generating Java..."],
        "done": True,
        "show_action_buttons": True,
        "append_answer": True,
    }


def _collect_java_files_for_migrate(abs_paths: list[str], max_files: int) -> list[str]:
    java_files: list[str] = []
    seen: set[str] = set()
    for raw in abs_paths:
        path = Path(raw)
        if path.is_file():
            if path.suffix.lower() != ".java":
                continue
            key = str(path.resolve())
            if key not in seen:
                seen.add(key)
                java_files.append(key)
            continue
        list_raw = list_java_files.invoke(
            {"path": str(path), "recursive": True, "max_files": max_files}
        )
        try:
            found = json.loads(list_raw).get("files", [])
        except Exception:
            found = []
        for jf in found:
            if jf not in seen:
                seen.add(jf)
                java_files.append(jf)
    return java_files


def resolve_java_files(state: CodeAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = session.get("repo_root", "")
    max_files = state.get("max_files", 20)
    message = state.get("body") or state.get("user_message", "")
    active_files = session.get("active_files") or []

    abs_paths, err = resolve_active_file_queries(
        root, message, active_files, extensions=".java"
    )
    if err:
        return {"done": True, "answer": err}
    if not abs_paths:
        return {
            "done": True,
            "answer": (
                "Could not resolve a Java file. Mention `@path/to/File.java` or a filename in chat."
            ),
        }

    java_files = _collect_java_files_for_migrate(abs_paths, max_files)
    if not java_files:
        return {"done": True, "answer": "No `.java` files found for the selected context."}

    set_active_files(session, root, java_files)
    session["target_path"] = java_files[0]
    session["pending_files"] = list(java_files)
    session["deps_found"] = []
    return {
        "session_state": session,
        "java_files": java_files,
        "statuses": [f"Found {len(java_files)} Java file(s). Checking dependencies..."],
    }


def check_dependencies(state: CodeAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    root = session.get("repo_root", "")
    java_files = session.get("pending_files") or []
    max_files = state.get("max_files", 20)

    all_deps: set[str] = set()
    repo_scan = str(resolve_repo_root(root))
    for jf in java_files:
        java_code = read_text_file.invoke({"path": jf})
        if java_code.startswith("(missing"):
            continue
        deps_raw = find_local_java_dependencies.invoke(
            {"java_code": java_code, "repo_root": repo_scan}
        )
        deps = json.loads(deps_raw).get("dependencies", [])
        for d in deps:
            if d not in java_files:
                all_deps.add(d)

    session["deps_found"] = list(all_deps)
    if all_deps:
        session["state"] = STATE_ASK_DEPS
        deps_list = "\n".join(f"- `{Path(d).name}`" for d in list(all_deps)[:5])
        if len(all_deps) > 5:
            deps_list += f"\n- ...and {len(all_deps) - 5} more."
        answer = (
            f"Found **{len(all_deps)} dependencies**:\n{deps_list}\n\n"
            "Convert dependencies too? (Yes/No)"
        )
        return {
            "session_state": session,
            "answer": answer,
            "done": True,
        }
    session["state"] = STATE_CONVERTING
    return {"session_state": session, "route": "convert", "convert_index": 0}


def route_after_deps(state: CodeAgentState) -> str:
    if state.get("route") == "convert":
        return "convert"
    return "end"


def convert_one_file(state: CodeAgentState) -> dict[str, Any]:
    session = _ensure_session(state)
    max_retries = state.get("max_retries", 3)
    files = session.get("pending_files") or []
    index = int(state.get("convert_index") or 0)

    if index >= len(files):
        n = len(session.get("pending_writes") or [])
        session["state"] = STATE_REVIEW
        return {
            "session_state": session,
            "answer": (
                f"Conversion complete. **{n}** file(s) pending. "
                "Use Review / Keep All / Undo All."
            ),
            "done": True,
            "show_action_buttons": True,
            "append_answer": True,
        }

    jf_path = files[index]
    jf_p = Path(jf_path)
    prefix = f"**({index + 1}/{len(files)})** `{jf_p.name}`: "
    statuses = [prefix + "Reading...", prefix + "Translating...", prefix + "Adding comments..."]

    java_code = read_text_file.invoke({"path": jf_path})
    if java_code.startswith("(missing"):
        return {
            "convert_index": index + 1,
            "statuses": [prefix + "Skipped (missing)."],
            "session_state": session,
        }

    deps_raw = find_local_java_dependencies.invoke(
        {"java_code": java_code, "repo_root": str(jf_p.parent)}
    )
    deps = json.loads(deps_raw).get("dependencies", [])
    deps_context = ""
    for dep_path in deps:
        if dep_path != jf_path:
            dep_code = read_text_file.invoke({"path": dep_path})
            if not dep_code.startswith("(missing"):
                deps_context += f"\n// {Path(dep_path).name}\n{dep_code}\n"

    prompt = format_java2py_inference(java_code, few_shot=deps_context)
    python_code = _codegen_generate(prompt, response_type="code")
    python_code = _validate_and_fix_python(
        python_code, f"Original java:\n{java_code}", max_retries
    )
    python_code = add_python_comments(python_code)

    out_path = jf_p.with_suffix(".py")
    original = ""
    if out_path.exists():
        original = read_text_file.invoke({"path": str(out_path)})
        if original.startswith("(missing"):
            original = ""

    queue_write(
        session,
        str(out_path),
        python_code,
        action="modify" if original else "create",
        original=original,
        name=jf_p.name,
        java=java_code,
        python=python_code,
        language="python",
    )
    record_migrated_py(session, session.get("repo_root", ""), str(out_path))
    return {
        "session_state": session,
        "convert_index": index + 1,
        "statuses": statuses + [prefix + "Queued for review."],
    }


def route_convert(state: CodeAgentState) -> str:
    if state.get("done"):
        return "end"
    files = (_ensure_session(state).get("pending_files") or [])
    index = int(state.get("convert_index") or 0)
    if index <= len(files):
        return "next"
    return "end"
