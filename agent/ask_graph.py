"""Compile the LangGraph StateGraph for the Ask Agent."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from agent.ask_nodes import (
    answer_direct,
    answer_one_file,
    check_no_repo,
    detect_task,
    finalize_per_file_answer,
    generate_code,
    generate_unified_answer,
    init_per_file_answer,
    load_file_sources,
    plan_query,
    prepare_answer,
    retrieve_sources,
    route_after_detect,
    route_after_file,
    route_after_no_repo,
    route_after_plan,
    route_after_prepare,
    validate_repo,
)
from agent.ask_state import AskAgentState, initial_ask_state

_compiled = None


def build_ask_graph():
    g: StateGraph = StateGraph(AskAgentState)

    g.add_node("detect_task", detect_task)
    g.add_node("generate_code", generate_code)
    g.add_node("check_no_repo", check_no_repo)
    g.add_node("answer_direct", answer_direct)
    g.add_node("validate_repo", validate_repo)
    g.add_node("plan_query", plan_query)
    g.add_node("load_file_sources", load_file_sources)
    g.add_node("retrieve_sources", retrieve_sources)
    g.add_node("prepare_answer", prepare_answer)
    g.add_node("generate_unified_answer", generate_unified_answer)
    g.add_node("init_per_file_answer", init_per_file_answer)
    g.add_node("answer_one_file", answer_one_file)
    g.add_node("finalize_per_file_answer", finalize_per_file_answer)

    g.add_edge(START, "detect_task")
    g.add_conditional_edges(
        "detect_task",
        route_after_detect,
        {
            "gen_code": "generate_code",
            "no_repo": "check_no_repo",
            "validate_repo": "validate_repo",
        },
    )
    g.add_edge("generate_code", END)

    g.add_conditional_edges(
        "check_no_repo",
        route_after_no_repo,
        {
            "repo_error": END,
            "answer_direct": "answer_direct",
            "validate_repo": "validate_repo",
        },
    )
    g.add_edge("answer_direct", END)

    g.add_conditional_edges(
        "validate_repo",
        lambda s: "end" if s.get("done") else "plan",
        {"end": END, "plan": "plan_query"},
    )

    g.add_conditional_edges(
        "plan_query",
        route_after_plan,
        {
            "file_sources": "load_file_sources",
            "retrieve": "retrieve_sources",
        },
    )

    g.add_edge("load_file_sources", "prepare_answer")
    g.add_conditional_edges(
        "retrieve_sources",
        lambda s: "end" if s.get("done") else "prepare",
        {"end": END, "prepare": "prepare_answer"},
    )

    g.add_conditional_edges(
        "prepare_answer",
        route_after_prepare,
        {
            "end": END,
            "unified": "generate_unified_answer",
            "per_file": "init_per_file_answer",
        },
    )
    g.add_edge("generate_unified_answer", END)
    g.add_edge("init_per_file_answer", "answer_one_file")
    g.add_conditional_edges(
        "answer_one_file",
        route_after_file,
        {
            "next_file": "answer_one_file",
            "finalize": "finalize_per_file_answer",
        },
    )
    g.add_edge("finalize_per_file_answer", END)

    return g.compile()


def get_ask_graph():
    global _compiled
    if _compiled is None:
        _compiled = build_ask_graph()
    return _compiled


def reset_ask_graph() -> None:
    global _compiled
    _compiled = None


def ask_turn(
    user_message: str,
    history: list[dict[str, str]] | None = None,
    session_state: dict[str, Any] | None = None,
    repo_root: str = "",
    *,
    max_files: int = 20,
    rag_top_k: int = 5,
) -> dict[str, Any]:
    graph = get_ask_graph()
    state = initial_ask_state(
        user_message,
        history,
        session_state,
        repo_root,
        max_files=max_files,
        rag_top_k=rag_top_k,
    )
    return dict(graph.invoke(state))
