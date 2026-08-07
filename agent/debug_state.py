"""Shared LangGraph state for the Debug Agent."""

from __future__ import annotations

from typing import Any, TypedDict

STATE_INIT = "init"
STATE_REVIEW = "review"
STATE_DEBUG_QA = "debug_qa"


class DebugAgentState(TypedDict, total=False):
    user_message: str
    history: list[dict[str, str]]
    session_state: dict[str, Any]
    repo_root: str
    max_files: int
    max_retries: int

    route: str
    target_paths: list[str]
    evidence_by_path: dict[str, dict[str, str]]
    debug_context: str
    diagnosis_text: str
    allow_behavioral_fix: bool
    any_mechanical: bool

    status: str
    statuses: list[str]
    error: str
    answer: str
    done: bool
    show_action_buttons: bool
    append_answer: bool
    followup_prompt: str


def initial_debug_state(
    user_message: str,
    history: list[dict[str, str]] | None = None,
    session_state: dict[str, Any] | None = None,
    repo_root: str = "",
    *,
    max_files: int = 20,
    max_retries: int = 3,
) -> DebugAgentState:
    return DebugAgentState(
        user_message=user_message,
        history=list(history or []),
        session_state=dict(session_state or {}),
        repo_root=repo_root,
        max_files=max_files,
        max_retries=max_retries,
        target_paths=[],
        evidence_by_path={},
        statuses=[],
        done=False,
        show_action_buttons=False,
        append_answer=False,
    )
