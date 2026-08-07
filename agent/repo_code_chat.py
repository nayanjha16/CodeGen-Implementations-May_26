"""Code Agent — migrate, NL→Java/Python, comments, pending writes."""

from __future__ import annotations

from typing import Any, Generator

from agent.code_graph import get_code_graph
from agent.code_state import initial_code_state
from agent.llms import codegen_generate
from agent.nodes import attach_ast, fix_python
from agent.repo_utils import (
    add_python_comments,
    append_bot,
    append_user,
    code_task_language_note,
    detect_code_task,
    empty_session,
    strip_task_prefix,
    update_last_bot,
    validate_and_fix_python,
    yield_chat,
)

TASK_LABELS = {
    "gen_python": "generating Python",
    "gen_java": "generating Java",
    "migrate": "converting Java to Python",
}


def _apply_graph_update(
    history: list[dict[str, str]],
    session_state: dict[str, Any],
    update: dict[str, Any],
) -> list[dict[str, Any]]:
    if update.get("session_state") is not None:
        session_state.clear()
        session_state.update(update["session_state"])

    extras: dict[str, Any] = {"session_state": session_state}
    if update.get("show_action_buttons"):
        extras["show_action_buttons"] = True

    chunks: list[dict[str, Any]] = []
    for status in update.get("statuses") or []:
        if status:
            update_last_bot(history, status)
            chunks.append(yield_chat(history, extras))

    status = update.get("status")
    if status:
        update_last_bot(history, status)
        chunks.append(yield_chat(history, extras))

    answer = update.get("answer")
    if answer and update.get("done"):
        if update.get("show_action_buttons"):
            append_bot(history, answer)
        else:
            update_last_bot(history, answer)
        chunks.append(yield_chat(history, extras))
    elif update.get("done") and update.get("error"):
        update_last_bot(history, update["error"])
        chunks.append(yield_chat(history, extras))

    return chunks


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

    current = session_state.get("state", "init")
    if current == "converting":
        return

    append_user(history, user_message)
    if current == "ask_deps":
        append_bot(history, "Preparing conversion...")
    else:
        active_files = session_state.get("active_files") or []
        task = detect_code_task(user_message, active_files, repo_root=root)
        lang_note = code_task_language_note(task, root)
        label = TASK_LABELS.get(task, "working")
        append_bot(history, f"Code Agent — {label}{lang_note}...")
    yield yield_chat(history, {"session_state": session_state})

    graph = get_code_graph()
    state = initial_code_state(
        user_message,
        history,
        session_state,
        repo_root,
        max_files=max_files,
        max_retries=max_retries,
    )

    for event in graph.stream(state, stream_mode="updates"):
        for update in event.values():
            for chunk in _apply_graph_update(history, session_state, update):
                yield chunk

    if not history or history[-1].get("role") != "assistant":
        result = graph.invoke(state)
        for chunk in _apply_graph_update(history, session_state, result):
            yield chunk
