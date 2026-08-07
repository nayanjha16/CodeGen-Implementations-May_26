"""Compile the LangGraph StateGraph for the Debug Agent."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from agent.debug_nodes import (
    check_repo,
    diagnose_node,
    fix_all_node,
    fix_node,
    followup_node,
    route_after_diagnose,
    route_command,
    route_command_edge,
    route_followup_edge,
    scan_repo_node,
)
from agent.debug_state import DebugAgentState, initial_debug_state

_compiled = None


def build_debug_graph():
    g: StateGraph = StateGraph(DebugAgentState)

    g.add_node("check_repo", check_repo)
    g.add_node("route_command", route_command)
    g.add_node("scan_repo", scan_repo_node)
    g.add_node("fix_all", fix_all_node)
    g.add_node("followup", followup_node)
    g.add_node("diagnose", diagnose_node)
    g.add_node("fix", fix_node)

    g.add_edge(START, "check_repo")
    g.add_conditional_edges(
        "check_repo",
        lambda s: "end" if s.get("done") else "route",
        {"end": END, "route": "route_command"},
    )
    g.add_conditional_edges(
        "route_command",
        route_command_edge,
        {
            "end": END,
            "scan": "scan_repo",
            "fix_all": "fix_all",
            "followup": "followup",
            "diagnose": "diagnose",
        },
    )
    g.add_edge("scan_repo", END)
    g.add_edge("fix_all", END)
    g.add_conditional_edges(
        "followup",
        route_followup_edge,
        {"fix": "fix", "end": END},
    )
    g.add_conditional_edges(
        "diagnose",
        route_after_diagnose,
        {"fix": "fix", "end": END},
    )
    g.add_edge("fix", END)

    return g.compile()


def get_debug_graph():
    global _compiled
    if _compiled is None:
        _compiled = build_debug_graph()
    return _compiled


def reset_debug_graph() -> None:
    global _compiled
    _compiled = None


def debug_turn(
    user_message: str,
    history: list[dict[str, str]] | None = None,
    session_state: dict[str, Any] | None = None,
    repo_root: str = "",
    *,
    max_files: int = 20,
    max_retries: int = 3,
) -> dict[str, Any]:
    graph = get_debug_graph()
    state = initial_debug_state(
        user_message,
        history,
        session_state,
        repo_root,
        max_files=max_files,
        max_retries=max_retries,
    )
    return dict(graph.invoke(state))
