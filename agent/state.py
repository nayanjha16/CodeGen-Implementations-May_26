"""Shared LangGraph state for the codegen agent."""

from __future__ import annotations

import operator
from typing import Annotated, Any, Literal, TypedDict


UnitType = Literal["function", "class"]
InputType = Literal["nl", "java", "pseudocode"]
RouteType = Literal["text_to_pl", "pl_to_pl", "pseudocode_to_fn", "pattern", "repo"]


class AgentState(TypedDict, total=False):
    """Mutable graph state passed between LangGraph nodes.

    ``unit`` is ``function`` for Phase 1 and ``class`` when scaling to
    full-class conversion later — all nodes honor this field.
    """

    nl_prompt: str
    java_code: str
    python_code: str
    stdout: str
    stderr: str
    exit_code: int
    judge_yes: bool
    judge_reason: str
    attempts: int
    max_retries: int
    unit: UnitType
    input_type: InputType
    route: RouteType
    use_rag: bool
    rag_context: str
    ast_info: str
    pattern: str
    repo_root: str
    repo_files: list[str]
    trace: Annotated[list[dict[str, Any]], operator.add]


def initial_state(
    nl_prompt: str = "",
    *,
    java_code: str = "",
    unit: UnitType = "function",
    input_type: InputType | None = None,
    use_rag: bool = False,
    max_retries: int = 3,
    pattern: str = "",
    repo_root: str = "",
) -> AgentState:
    """Build a fresh state dict for ``graph.invoke``."""
    if input_type is None:
        if java_code.strip() and not nl_prompt.strip():
            input_type = "java"
        elif _looks_like_pseudocode(nl_prompt):
            input_type = "pseudocode"
        else:
            input_type = "nl"

    return AgentState(
        nl_prompt=nl_prompt.strip(),
        java_code=java_code.strip(),
        python_code="",
        stdout="",
        stderr="",
        exit_code=0,
        judge_yes=False,
        judge_reason="",
        attempts=0,
        max_retries=max_retries,
        unit=unit,
        input_type=input_type,
        route="text_to_pl",
        use_rag=use_rag,
        rag_context="",
        ast_info="",
        pattern=pattern.strip(),
        repo_root=repo_root,
        repo_files=[],
        trace=[],
    )


def _looks_like_pseudocode(text: str) -> bool:
    lower = text.lower()
    markers = ("begin", "end if", "end while", "for each", "pseudo", "algorithm:")
    return any(m in lower for m in markers)
