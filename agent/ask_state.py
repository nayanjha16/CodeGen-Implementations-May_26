"""Shared LangGraph state for the Ask Agent."""

from __future__ import annotations

from typing import Any, Literal, TypedDict

STATE_INIT = "init"
STATE_QA = "qa"

AskTask = Literal["gen_python", "gen_java", "explain"]
RouteAfterDetect = Literal["gen_code", "no_repo", "validate_repo"]
RouteAfterNoRepo = Literal["repo_error", "answer_direct"]
RouteAfterRetrieval = Literal["end", "generate_answer", "answer_file"]
AnswerMode = Literal["unified", "per_file", "next_file"]


class AskAgentState(TypedDict, total=False):
    user_message: str
    history: list[dict[str, str]]
    session_state: dict[str, Any]
    repo_root: str
    max_files: int
    rag_top_k: int

    task: AskTask
    question: str
    body: str
    plan: dict[str, Any]

    sources: list[dict[str, str]]
    files: list[str]
    from_rag: bool
    overview: bool
    retrieval_refs: list[str]

    route: str
    answer_mode: AnswerMode
    file_index: int
    sections: list[str]

    status: str
    statuses: list[str]
    error: str
    answer: str
    done: bool
    show_action_buttons: bool


def initial_ask_state(
    user_message: str,
    history: list[dict[str, str]] | None = None,
    session_state: dict[str, Any] | None = None,
    repo_root: str = "",
    *,
    max_files: int = 20,
    rag_top_k: int = 5,
) -> AskAgentState:
    return AskAgentState(
        user_message=user_message,
        history=list(history or []),
        session_state=dict(session_state or {}),
        repo_root=repo_root,
        max_files=max_files,
        rag_top_k=rag_top_k,
        sources=[],
        files=[],
        from_rag=False,
        overview=False,
        retrieval_refs=[],
        file_index=0,
        sections=[],
        statuses=[],
        done=False,
        show_action_buttons=False,
    )
