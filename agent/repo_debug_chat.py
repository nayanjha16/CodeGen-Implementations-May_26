"""Debug Agent — diagnose and fix Python issues in a repo workspace."""

from __future__ import annotations

from typing import Any, Generator

from agent.debug_graph import get_debug_graph
from agent.debug_state import initial_debug_state
from agent.debug_nodes import _extract_debug_context
from agent.llms import codegen_generate
from agent.nodes import attach_ast, fix_python
from agent.repo_utils import (
    append_bot,
    append_user,
    empty_session,
    update_last_bot,
    validate_run_and_fix_python,
    yield_chat,
)

# Re-export for tests
__all__ = [
    "chat_debug_generator",
    "codegen_generate",
    "validate_run_and_fix_python",
    "_extract_debug_context",
]


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
    if answer and update.get("route") == "fix" and not update.get("done"):
        append_bot(history, answer)
        chunks.append(yield_chat(history, extras))

    if answer and update.get("done"):
        if update.get("append_answer"):
            append_bot(history, answer)
        else:
            update_last_bot(history, answer)
        followup = update.get("followup_prompt")
        if followup:
            append_bot(history, followup)
        chunks.append(yield_chat(history, extras))
    elif update.get("done") and update.get("error"):
        update_last_bot(history, update["error"])
        chunks.append(yield_chat(history, extras))

    return chunks


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

    append_user(history, user_message)

    graph = get_debug_graph()
    state = initial_debug_state(
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
