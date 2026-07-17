"""Compile the LangGraph StateGraph for agentic NL→Java→Python codegen."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from agent.nodes import (
    attach_ast,
    execute_python,
    fix_python,
    java_to_python,
    judge_intent,
    maybe_retrieve,
    nl_to_java,
    pattern_to_java,
    pseudocode_to_java,
    repo_prepare,
    route_after_router,
    route_input,
    should_continue,
)
from agent.state import AgentState, UnitType, initial_state

_compiled = None


def build_agent_graph():
    """Build and compile the codegen agent graph.

    Flow:
      route → retrieve → (text_to_pl | pl_to_pl | pseudocode | pattern | repo)
        → java_to_python (where needed) → execute → judge
        → (fix → attach_ast → execute)* or END
    """
    g: StateGraph = StateGraph(AgentState)

    g.add_node("route", route_input)
    g.add_node("retrieve", maybe_retrieve)
    g.add_node("nl_to_java", nl_to_java)
    g.add_node("pseudocode_to_java", pseudocode_to_java)
    g.add_node("pattern_to_java", pattern_to_java)
    g.add_node("repo_prepare", repo_prepare)
    g.add_node("java_to_python", java_to_python)
    g.add_node("execute", execute_python)
    g.add_node("judge", judge_intent)
    g.add_node("attach_ast", attach_ast)
    g.add_node("fix_python", fix_python)

    g.add_edge(START, "route")
    g.add_edge("route", "retrieve")

    g.add_conditional_edges(
        "retrieve",
        route_after_router,
        {
            "text_to_pl": "nl_to_java",
            "pl_to_pl": "java_to_python",
            "pseudocode_to_fn": "pseudocode_to_java",
            "pattern": "pattern_to_java",
            "repo": "repo_prepare",
        },
    )

    g.add_edge("nl_to_java", "java_to_python")
    g.add_edge("pseudocode_to_java", "java_to_python")
    g.add_edge("pattern_to_java", "java_to_python")
    # Repo path: after listing files, treat nl_prompt as the edit goal → NL→Java→Py
    g.add_edge("repo_prepare", "nl_to_java")

    g.add_edge("java_to_python", "execute")
    g.add_edge("execute", "judge")

    g.add_conditional_edges(
        "judge",
        should_continue,
        {
            "fix": "attach_ast",
            "end": END,
        },
    )
    g.add_edge("attach_ast", "fix_python")
    g.add_edge("fix_python", "execute")

    return g.compile()


def get_agent_graph():
    """Singleton compiled graph for API / eval reuse."""
    global _compiled
    if _compiled is None:
        _compiled = build_agent_graph()
    return _compiled


def reset_agent_graph() -> None:
    """Clear cached graph (tests)."""
    global _compiled
    _compiled = None


def solve(
    nl_prompt: str = "",
    *,
    java_code: str = "",
    unit: UnitType = "function",
    use_rag: bool = False,
    max_retries: int = 3,
    pattern: str = "",
    repo_root: str = "",
    input_type: str | None = None,
) -> dict[str, Any]:
    """Run the agent end-to-end and return final state as a plain dict."""
    graph = get_agent_graph()
    state = initial_state(
        nl_prompt,
        java_code=java_code,
        unit=unit,  # type: ignore[arg-type]
        input_type=input_type,  # type: ignore[arg-type]
        use_rag=use_rag,
        max_retries=max_retries,
        pattern=pattern,
        repo_root=repo_root,
    )
    result = graph.invoke(state)
    return dict(result)
