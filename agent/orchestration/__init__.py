"""LangGraph workflow, runner, and shared run state."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent.orchestration.graph import build_agent_graph, run_agent_graph
    from agent.orchestration.runner import AgentRunner
    from agent.orchestration.state import AgentResult, AgentState, RunContext

__all__ = [
    "AgentResult",
    "AgentRunner",
    "AgentState",
    "RunContext",
    "build_agent_graph",
    "run_agent_graph",
]


def __getattr__(name: str):
    if name in {"build_agent_graph", "run_agent_graph"}:
        from agent.orchestration import graph as mod

        return getattr(mod, name)
    if name == "AgentRunner":
        from agent.orchestration import runner as mod

        return mod.AgentRunner
    if name in {"AgentResult", "AgentState", "RunContext"}:
        from agent.orchestration import state as mod

        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
