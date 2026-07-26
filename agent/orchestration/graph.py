"""LangGraph workflow wiring (spec §8)."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from agent.orchestration.runner import AgentRunner
from agent.orchestration.state import AgentResult, AgentState
from agent.orchestrator.intent_detector import IntentDetector
from agent.orchestrator.planner import build_plan


def detect_intent_node(state: AgentState, *, detector: IntentDetector) -> dict[str, Any]:
    result = detector.detect(
        state["user_message"],
        explicit_intent=state.get("explicit_intent"),
    )
    plan = build_plan(result.intent)
    return {
        "intent": result.intent,
        "error": None,
        "_plan_steps": [step.value for step in plan.steps],
    }


def execute_plan_node(state: AgentState, *, runner: AgentRunner) -> dict[str, Any]:
    result = runner.run(
        state["user_message"],
        explicit_intent=state.get("intent") or state.get("explicit_intent"),
        db_id=state.get("db_id"),
        dataset=state.get("dataset"),
        sql=state.get("sql"),
    )
    return _result_to_state(result)


def _result_to_state(result: AgentResult) -> dict[str, Any]:
    return {
        "intent": result.intent,
        "answer": result.answer,
        "sql": result.sql,
        "mongo_query": result.mongo_query,
        "documentation": result.documentation,
        "rows": result.rows,
        "error": result.error,
    }


def build_agent_graph(
    runner: AgentRunner | None = None,
    detector: IntentDetector | None = None,
):
    """Compile LangGraph: detect_intent → execute → END."""
    active_runner = runner or AgentRunner()
    active_detector = detector or active_runner.detector

    graph: StateGraph = StateGraph(AgentState)
    graph.add_node(
        "detect_intent",
        lambda state: detect_intent_node(state, detector=active_detector),
    )
    graph.add_node(
        "execute_plan",
        lambda state: execute_plan_node(state, runner=active_runner),
    )
    graph.add_edge(START, "detect_intent")
    graph.add_edge("detect_intent", "execute_plan")
    graph.add_edge("execute_plan", END)
    return graph.compile()


def run_agent_graph(
    user_message: str,
    *,
    explicit_intent: str | None = None,
    db_id: str | None = None,
    dataset: str | None = None,
    sql: str | None = None,
    runner: AgentRunner | None = None,
) -> AgentResult:
    """Invoke compiled graph and return AgentResult."""
    active_runner = runner or AgentRunner()
    graph = build_agent_graph(runner=active_runner)
    final_state = graph.invoke(
        {
            "user_message": user_message,
            "explicit_intent": explicit_intent,
            "db_id": db_id,
            "dataset": dataset,
            "sql": sql,
        }
    )
    return AgentResult(
        answer=final_state.get("answer", ""),
        intent=final_state.get("intent", "text2sql"),
        sql=final_state.get("sql", ""),
        mongo_query=final_state.get("mongo_query", ""),
        documentation=final_state.get("documentation", ""),
        rows=final_state.get("rows") or [],
        error=final_state.get("error"),
    )
