"""Intent detection, planning, prompts, and retry logic."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent.orchestrator.intent_detector import (
        AgentIntent,
        IntentDetector,
        IntentResult,
    )
    from agent.orchestrator.planner import AgentPlan, PlanStep
    from agent.orchestrator.retry import RetryState

__all__ = [
    "AgentIntent",
    "AgentPlan",
    "IntentDetector",
    "IntentResult",
    "PlanStep",
    "RetryState",
    "build_plan",
    "classify_by_heuristic",
    "classify_by_rules",
    "detect_intent",
    "extract_mongo_from_message",
    "extract_sql_from_message",
    "should_retry_sql",
]


def __getattr__(name: str):
    if name in {
        "AgentIntent",
        "IntentDetector",
        "IntentResult",
        "classify_by_heuristic",
        "classify_by_rules",
        "detect_intent",
        "extract_mongo_from_message",
        "extract_sql_from_message",
    }:
        from agent.orchestrator import intent_detector as mod

        return getattr(mod, name)
    if name in {"AgentPlan", "PlanStep", "build_plan"}:
        from agent.orchestrator import planner as mod

        return getattr(mod, name)
    if name in {"RetryState", "should_retry_sql"}:
        from agent.orchestrator import retry as mod

        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
