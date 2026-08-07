"""Compile the LangGraph StateGraph for the Code Agent."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from agent.code_nodes import (
    check_dependencies,
    check_repo,
    convert_one_file,
    detect_task,
    generate_java,
    generate_python,
    handle_deps_reply,
    resolve_java_files,
    route_after_deps,
    route_convert,
    route_session,
    route_session_edge,
    route_task,
)
from agent.code_state import CodeAgentState, initial_code_state

_compiled = None


def build_code_graph():
    g: StateGraph = StateGraph(CodeAgentState)

    g.add_node("route_session", route_session)
    g.add_node("handle_deps_reply", handle_deps_reply)
    g.add_node("check_repo", check_repo)
    g.add_node("detect_task", detect_task)
    g.add_node("generate_python", generate_python)
    g.add_node("generate_java", generate_java)
    g.add_node("resolve_java_files", resolve_java_files)
    g.add_node("check_dependencies", check_dependencies)
    g.add_node("convert_one_file", convert_one_file)

    g.add_edge(START, "route_session")
    g.add_conditional_edges(
        "route_session",
        route_session_edge,
        {
            "end": END,
            "ask_deps": "handle_deps_reply",
            "init": "check_repo",
        },
    )
    g.add_edge("handle_deps_reply", "convert_one_file")
    g.add_conditional_edges(
        "check_repo",
        lambda s: "end" if s.get("done") else "detect",
        {"end": END, "detect": "detect_task"},
    )
    g.add_conditional_edges(
        "detect_task",
        route_task,
        {
            "gen_python": "generate_python",
            "gen_java": "generate_java",
            "migrate": "resolve_java_files",
        },
    )
    g.add_edge("generate_python", END)
    g.add_edge("generate_java", END)
    g.add_conditional_edges(
        "resolve_java_files",
        lambda s: "end" if s.get("done") else "deps",
        {"end": END, "deps": "check_dependencies"},
    )
    g.add_conditional_edges(
        "check_dependencies",
        route_after_deps,
        {"end": END, "convert": "convert_one_file"},
    )
    g.add_conditional_edges(
        "convert_one_file",
        route_convert,
        {"next": "convert_one_file", "end": END},
    )

    return g.compile()


def get_code_graph():
    global _compiled
    if _compiled is None:
        _compiled = build_code_graph()
    return _compiled


def reset_code_graph() -> None:
    global _compiled
    _compiled = None


def code_turn(
    user_message: str,
    history: list[dict[str, str]] | None = None,
    session_state: dict[str, Any] | None = None,
    repo_root: str = "",
    *,
    max_files: int = 20,
    max_retries: int = 3,
) -> dict[str, Any]:
    graph = get_code_graph()
    state = initial_code_state(
        user_message,
        history,
        session_state,
        repo_root,
        max_files=max_files,
        max_retries=max_retries,
    )
    return dict(graph.invoke(state))
