"""Code Agent — migrate, NL→Java/Python, comments, pending writes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Generator

from agent.llms import codegen_generate
from agent.nodes import attach_ast, fix_python
from agent.repo_migrate import _merge
from agent.repo_utils import (
    add_python_comments,
    append_bot,
    append_user,
    detect_code_task,
    empty_session,
    next_generated_name,
    queue_write,
    record_migrated_py,
    resolve_active_file_queries,
    resolve_repo_root,
    set_active_files,
    strip_task_prefix,
    update_last_bot,
    validate_and_fix_python,
    yield_chat,
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
STATE_INIT = "init"
STATE_ASK_DEPS = "ask_deps"
STATE_CONVERTING = "converting"
STATE_REVIEW = "review"


def chat_code_generator(
    user_message: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    repo_root: str,
    max_retries: int = 3,
    max_files: int = 20,
) -> Generator[dict[str, Any], None, None]:
    if not session_state:
        session_state = empty_session(repo_root)

    if repo_root:
        session_state["repo_root"] = repo_root

    root = (session_state.get("repo_root") or "").strip()
    if not root:
        append_user(history, user_message)
        append_bot(history, "Set the **Project root** path above, then send a code request.")
        yield yield_chat(history, {"session_state": session_state})
        return

    current = session_state.get("state", STATE_INIT)

    if current == STATE_ASK_DEPS:
        yield from _handle_deps_reply(user_message, history, session_state, max_retries)
        return

    if current == STATE_CONVERTING:
        return

    active_files = session_state.get("active_files") or []
    task = detect_code_task(user_message, active_files)
    body = strip_task_prefix(user_message)

    append_user(history, user_message)
    append_bot(history, f"Code Agent — {TASK_LABELS.get(task, 'working')}...")
    yield yield_chat(history, {"session_state": session_state})

    try:
        resolve_repo_root(root)
    except FileNotFoundError:
        update_last_bot(history, f"Repo path not found: `{root}`")
        yield yield_chat(history, {"session_state": session_state})
        return

    if task == "gen_python":
        yield from _generate_python(body or user_message, history, session_state, root, max_retries)
        return

    if task == "gen_java":
        yield from _generate_java(body or user_message, history, session_state, root)
        return

    yield from _start_migrate(
        body or user_message,
        history,
        session_state,
        root,
        max_files,
        max_retries,
        active_files,
    )


def _generate_python(
    spec: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    repo_root: str,
    max_retries: int,
) -> Generator[dict[str, Any], None, None]:
    update_last_bot(history, "Generating Python...")
    yield yield_chat(history, {"session_state": session_state})

    prompt = format_nl2py_inference(spec)
    python_code = codegen_generate(prompt, response_type="code")
    python_code = validate_and_fix_python(
        python_code,
        f"Original request: {spec}",
        max_retries,
        _merge,
        attach_ast,
        fix_python,
        initial_state,
    )
    update_last_bot(history, "Adding comments...")
    yield yield_chat(history, {"session_state": session_state})
    python_code = add_python_comments(python_code)

    out_path = next_generated_name(repo_root, ".py")
    queue_write(
        session_state,
        str(out_path),
        python_code,
        action="create",
        name=out_path.name,
        python=python_code,
        language="python",
    )
    record_migrated_py(session_state, repo_root, str(out_path))
    session_state["state"] = STATE_REVIEW
    append_bot(
        history,
        f"Generated `{out_path.name}`. Click **Review**, then **Keep All** or **Undo All**.",
    )
    yield yield_chat(history, {"session_state": session_state, "show_action_buttons": True})


def _generate_java(
    spec: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    repo_root: str,
) -> Generator[dict[str, Any], None, None]:
    update_last_bot(history, "Generating Java...")
    yield yield_chat(history, {"session_state": session_state})

    prompt = format_nl2java_inference(spec)
    java_code = codegen_generate(prompt, response_type="code")

    out_path = next_generated_name(repo_root, ".java")
    queue_write(
        session_state,
        str(out_path),
        java_code,
        action="create",
        name=out_path.name,
        java=java_code,
        language="java",
    )
    session_state["state"] = STATE_REVIEW
    append_bot(
        history,
        f"Generated `{out_path.name}`. Click **Review**, then **Keep All** or **Undo All**.",
    )
    yield yield_chat(history, {"session_state": session_state, "show_action_buttons": True})


def _collect_java_files_for_migrate(abs_paths: list[str], max_files: int) -> list[str]:
    """Expand resolved paths to a deduplicated list of Java files."""
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


def _start_migrate(
    message: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    repo_root: str,
    max_files: int,
    max_retries: int,
    active_files: list[str],
) -> Generator[dict[str, Any], None, None]:
    abs_paths, err = resolve_active_file_queries(
        repo_root, message, active_files, extensions=".java"
    )
    if err:
        update_last_bot(history, err)
        yield yield_chat(history, {"session_state": session_state})
        return
    if not abs_paths:
        update_last_bot(
            history,
            "Could not resolve a Java file. Mention `@path/to/File.java` or a filename in chat.",
        )
        yield yield_chat(history, {"session_state": session_state})
        return

    java_files = _collect_java_files_for_migrate(abs_paths, max_files)
    if not java_files:
        update_last_bot(history, "No `.java` files found for the selected context.")
        yield yield_chat(history, {"session_state": session_state})
        return

    set_active_files(session_state, repo_root, java_files)
    session_state["target_path"] = java_files[0]
    session_state["pending_files"] = []
    session_state["deps_found"] = []

    session_state["pending_files"] = java_files
    update_last_bot(
        history, f"Found {len(java_files)} Java file(s). Checking dependencies..."
    )
    yield yield_chat(history, {"session_state": session_state})

    all_deps: set[str] = set()
    root = resolve_repo_root(repo_root)
    repo_scan = str(root)

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

    session_state["deps_found"] = list(all_deps)
    if all_deps:
        session_state["state"] = STATE_ASK_DEPS
        deps_list = "\n".join(f"- `{Path(d).name}`" for d in list(all_deps)[:5])
        if len(all_deps) > 5:
            deps_list += f"\n- ...and {len(all_deps) - 5} more."
        update_last_bot(
            history,
            f"Found **{len(all_deps)} dependencies**:\n{deps_list}\n\nConvert dependencies too? (Yes/No)",
        )
        yield yield_chat(history, {"session_state": session_state})
        return

    session_state["state"] = STATE_CONVERTING
    yield from _convert_files(history, session_state, max_retries)


def _handle_deps_reply(
    user_message: str,
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    max_retries: int,
) -> Generator[dict[str, Any], None, None]:
    ans = user_message.strip().lower()
    append_user(history, user_message)
    append_bot(history, "Preparing conversion...")
    yield yield_chat(history, {"session_state": session_state})

    if ans in ("yes", "y", "sure", "ok", "convert"):
        session_state["pending_files"].extend(session_state.get("deps_found", []))
        update_last_bot(
            history,
            f"Including dependencies. Converting {len(session_state['pending_files'])} file(s)...",
        )
    else:
        update_last_bot(
            history,
            f"Skipping dependencies. Converting {len(session_state['pending_files'])} file(s)...",
        )

    session_state["state"] = STATE_CONVERTING
    yield yield_chat(history, {"session_state": session_state})
    yield from _convert_files(history, session_state, max_retries)


def _convert_files(
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    max_retries: int,
) -> Generator[dict[str, Any], None, None]:
    files = session_state.get("pending_files", [])
    for i, jf_path in enumerate(files):
        jf_p = Path(jf_path)
        prefix = f"**({i + 1}/{len(files)})** `{jf_p.name}`: "
        append_bot(history, prefix + "Reading...")
        yield yield_chat(history, {"session_state": session_state})

        java_code = read_text_file.invoke({"path": jf_path})
        if java_code.startswith("(missing"):
            update_last_bot(history, prefix + "Skipped (missing).")
            yield yield_chat(history, {"session_state": session_state})
            continue

        update_last_bot(history, prefix + "Translating...")
        yield yield_chat(history, {"session_state": session_state})

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
        python_code = codegen_generate(prompt, response_type="code")
        python_code = validate_and_fix_python(
            python_code,
            f"Original java:\n{java_code}",
            max_retries,
            _merge,
            attach_ast,
            fix_python,
            initial_state,
        )

        update_last_bot(history, prefix + "Adding comments...")
        yield yield_chat(history, {"session_state": session_state})
        python_code = add_python_comments(python_code)

        out_path = jf_p.with_suffix(".py")
        original = ""
        if out_path.exists():
            original = read_text_file.invoke({"path": str(out_path)})
            if original.startswith("(missing"):
                original = ""

        queue_write(
            session_state,
            str(out_path),
            python_code,
            action="modify" if original else "create",
            original=original,
            name=jf_p.name,
            java=java_code,
            python=python_code,
            language="python",
        )
        record_migrated_py(session_state, session_state.get("repo_root", ""), str(out_path))
        update_last_bot(history, prefix + "Queued for review.")
        yield yield_chat(history, {"session_state": session_state})

    session_state["state"] = STATE_REVIEW
    n = len(session_state.get("pending_writes") or [])
    append_bot(
        history,
        f"Conversion complete. **{n}** file(s) pending. Use Review / Keep All / Undo All.",
    )
    yield yield_chat(history, {"session_state": session_state, "show_action_buttons": True})
