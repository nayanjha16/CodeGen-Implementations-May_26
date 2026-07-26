"""Deterministic intent → tool step plans."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from agent.orchestrator.intent_detector import AgentIntent

PlanStepKind = Literal[
    "extract_schema",
    "generate_sql",
    "generate_nosql",
    "generate_documentation",
    "validate_sql",
    "execute_postgres",
    "execute_mongo",
    "explain_sql",
    "summarize",
]


class PlanStep(StrEnum):
    EXTRACT_SCHEMA = "extract_schema"
    GENERATE_SQL = "generate_sql"
    GENERATE_NOSQL = "generate_nosql"
    GENERATE_DOCUMENTATION = "generate_documentation"
    VALIDATE_SQL = "validate_sql"
    EXECUTE_POSTGRES = "execute_postgres"
    EXECUTE_MONGO = "execute_mongo"
    EXPLAIN_SQL = "explain_sql"
    SUMMARIZE = "summarize"


_INTENT_PLANS: dict[AgentIntent, tuple[PlanStep, ...]] = {
    "text2sql": (
        PlanStep.EXTRACT_SCHEMA,
        PlanStep.GENERATE_SQL,
        PlanStep.VALIDATE_SQL,
        PlanStep.EXECUTE_POSTGRES,
        PlanStep.SUMMARIZE,
    ),
    "sql2nosql": (
        PlanStep.GENERATE_NOSQL,
        PlanStep.EXECUTE_MONGO,
        PlanStep.SUMMARIZE,
    ),
    "nosql2doc": (
        PlanStep.GENERATE_DOCUMENTATION,
        PlanStep.SUMMARIZE,
    ),
    "explain_sql": (
        PlanStep.EXTRACT_SCHEMA,
        PlanStep.EXPLAIN_SQL,
        PlanStep.SUMMARIZE,
    ),
    "validate_sql": (
        PlanStep.VALIDATE_SQL,
        PlanStep.SUMMARIZE,
    ),
}


@dataclass(frozen=True)
class AgentPlan:
    intent: AgentIntent
    steps: tuple[PlanStep, ...]

    def requires_schema(self) -> bool:
        return PlanStep.EXTRACT_SCHEMA in self.steps

    def requires_postgres_execution(self) -> bool:
        return PlanStep.EXECUTE_POSTGRES in self.steps

    def requires_mongo_execution(self) -> bool:
        return PlanStep.EXECUTE_MONGO in self.steps


def build_plan(intent: AgentIntent) -> AgentPlan:
    steps = _INTENT_PLANS.get(intent)
    if steps is None:
        raise ValueError(f"No plan for intent: {intent!r}")
    return AgentPlan(intent=intent, steps=steps)
