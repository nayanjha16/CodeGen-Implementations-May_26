"""Shared LangGraph state for the Code Agent."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

STATE_INIT = "init"
STATE_ASK_DEPS = "ask_deps"
STATE_CONVERTING = "converting"
STATE_REVIEW = "review"

CodeTask = Literal["gen_python", "gen_java", "migrate"]


class CodeAgentState(TypedDict, total=False):
    user_message: str
    history: list[dict[str, str]]
    session_state: dict[str, Any]
    repo_root: str
    max_files: int
    max_retries: int

    task: CodeTask
    body: str
    route: str

    java_files: list[str]
    convert_index: int

    status: str
    statuses: list[str]
    error: str
    answer: str
    done: bool
    show_action_buttons: bool


def initial_code_state(
    user_message: str,
    history: list[dict[str, str]] | None = None,
    session_state: dict[str, Any] | None = None,
    repo_root: str = "",
    *,
    max_files: int = 20,
    max_retries: int = 3,
) -> CodeAgentState:
    return CodeAgentState(
        user_message=user_message,
        history=list(history or []),
        session_state=dict(session_state or {}),
        repo_root=repo_root,
        max_files=max_files,
        max_retries=max_retries,
        java_files=[],
        convert_index=0,
        statuses=[],
        done=False,
        show_action_buttons=False,
    )
