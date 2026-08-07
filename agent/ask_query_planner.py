"""Lightweight intent + retrieval query planning for Ask Agent."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from agent.repo_utils import (
    extract_doc_file_refs,
    extract_file_refs,
    format_chat_history_block,
)

ANSWER_MODE_DIRECT = "direct_qa"
ANSWER_MODE_PER_FILE = "per_file_docs"
ANSWER_MODE_CLARIFY = "clarify_previous"
ANSWER_MODE_INVENTORY = "inventory"

_VALID_MODES = {
    ANSWER_MODE_DIRECT,
    ANSWER_MODE_PER_FILE,
    ANSWER_MODE_CLARIFY,
    ANSWER_MODE_INVENTORY,
}

PLANNER_PROMPT = """You plan repository Q&A. Given the user message and recent chat, output ONLY valid JSON with these keys:
- intent_summary: one sentence describing what the user wants to know
- retrieval_query: search query to find relevant code/docs in the repo (concrete keywords, class names, commands)
- answer_mode: one of direct_qa | per_file_docs | clarify_previous | inventory
- needs_repo_inventory: true ONLY if the user explicitly asks for repo contents, file lists, or what else exists
- is_follow_up: true if this refers to a prior assistant answer

Use per_file_docs ONLY when the user explicitly asks to explain/document selected or listed files individually.
Use clarify_previous when the user did not understand the prior answer and wants it restated.
Use inventory ONLY when the user explicitly asks what files exist, for a file list, or what else is in the repo.
Do NOT use inventory for "how does X work", architecture, workflow, or implementation questions — use direct_qa.
Do NOT set needs_repo_inventory for conceptual or architecture questions.

{chat_section}User message: {question}

JSON:"""

_ARCHITECTURE_PATTERNS = (
    re.compile(r"\bhow does .+ work\b"),
    re.compile(r"\bhow .+ works\b"),
    re.compile(r"\bexplain how\b"),
    re.compile(r"\barchitecture\b"),
    re.compile(r"\bwalk me through\b"),
    re.compile(r"\bhow is .+ implemented\b"),
    re.compile(r"\bhow (does|do) (this|the) (repo|project|system|app)\b"),
)

_EXPLICIT_INVENTORY_PATTERNS = (
    re.compile(r"\bwhat files\b"),
    re.compile(r"\bfile list\b"),
    re.compile(r"\bwhich files\b"),
    re.compile(r"\blist (the )?files\b"),
    re.compile(r"\bwhat else (is )?(in|does)\b"),
    re.compile(r"\bwhat (else )?(is )?in (the )?repo\b"),
    re.compile(r"\bwhat does (this|the) repo contain\b"),
    re.compile(r"\brepo contents\b"),
    re.compile(r"\ball files\b"),
    re.compile(r"\bwhat else does (this|the) repo have\b"),
)

_OVERVIEW_PATTERNS = (
    re.compile(r"\b(summarize|summarise|summary)\b"),
    re.compile(r"\bkey points\b"),
    re.compile(r"\bkey concepts\b"),
    re.compile(r"\boverview\b"),
    re.compile(r"\bmain functionality\b"),
    re.compile(r"\bwhat is (this|the) repo\b"),
    re.compile(r"\bhigh[- ]level\b"),
)

OVERVIEW_RETRIEVAL_QUERY = (
    "repository overview README architecture main components key concepts"
)


@dataclass
class AskPlan:
    intent_summary: str = ""
    retrieval_query: str = ""
    answer_mode: str = ANSWER_MODE_DIRECT
    needs_repo_inventory: bool = False
    is_follow_up: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any], question: str) -> AskPlan:
        mode = str(data.get("answer_mode", ANSWER_MODE_DIRECT)).strip()
        if mode not in _VALID_MODES:
            mode = ANSWER_MODE_DIRECT
        intent = str(data.get("intent_summary", "")).strip() or question.strip()
        retrieval = str(data.get("retrieval_query", "")).strip() or intent
        return cls(
            intent_summary=intent,
            retrieval_query=retrieval,
            answer_mode=mode,
            needs_repo_inventory=bool(data.get("needs_repo_inventory", False)),
            is_follow_up=bool(data.get("is_follow_up", False)),
        )


def _extract_json_object(text: str) -> dict[str, Any] | None:
    raw = (text or "").strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def is_overview_question(question: str) -> bool:
    """True when the user asks for a repo summary or high-level overview."""
    lower = question.strip().lower()
    if not lower:
        return False
    return any(p.search(lower) for p in _OVERVIEW_PATTERNS)


def mentions_specific_file(question: str) -> bool:
    """True when the question names a concrete source or documentation file."""
    q = question.strip()
    if not q:
        return False
    return bool(extract_file_refs(q) or extract_doc_file_refs(q))


def is_architecture_question(question: str) -> bool:
    """True when the user asks how something works, not what files exist."""
    lower = question.strip().lower()
    if not lower:
        return False
    return any(p.search(lower) for p in _ARCHITECTURE_PATTERNS)


def is_explicit_inventory_request(question: str) -> bool:
    """True when the user explicitly asks for a file list or repo contents."""
    lower = question.strip().lower()
    if not lower:
        return False
    return any(p.search(lower) for p in _EXPLICIT_INVENTORY_PATTERNS)


def apply_plan_heuristics(plan: AskPlan, question: str) -> AskPlan:
    """Correct common planner misclassifications using deterministic rules."""
    q = question.strip()
    if not q:
        return plan

    if is_overview_question(q):
        # "overview of readme.md" is still a question about one file: replacing
        # the query with the generic repo-overview text would discard the target.
        return AskPlan(
            intent_summary=plan.intent_summary or q,
            retrieval_query=q if mentions_specific_file(q) else OVERVIEW_RETRIEVAL_QUERY,
            answer_mode=ANSWER_MODE_DIRECT,
            needs_repo_inventory=False,
            is_follow_up=plan.is_follow_up,
        )

    if is_architecture_question(q):
        return AskPlan(
            intent_summary=plan.intent_summary or q,
            retrieval_query=plan.retrieval_query or q,
            answer_mode=ANSWER_MODE_DIRECT,
            needs_repo_inventory=False,
            is_follow_up=plan.is_follow_up,
        )

    if (
        plan.answer_mode == ANSWER_MODE_INVENTORY or plan.needs_repo_inventory
    ) and not is_explicit_inventory_request(q):
        return AskPlan(
            intent_summary=plan.intent_summary or q,
            retrieval_query=plan.retrieval_query or q,
            answer_mode=ANSWER_MODE_DIRECT,
            needs_repo_inventory=False,
            is_follow_up=plan.is_follow_up,
        )

    return plan


def build_retrieval_query(
    question: str,
    history: list[dict[str, str]],
    plan: AskPlan | None = None,
) -> str:
    """Compose a search query from planner output or conversation context."""
    if plan and plan.retrieval_query.strip():
        return plan.retrieval_query.strip()
    recent = format_chat_history_block(history, max_turns=2)
    if recent:
        return f"Given this conversation:\n{recent}\n\nFind code relevant to: {question.strip()}"
    return question.strip()


def fallback_plan(question: str, history: list[dict[str, str]]) -> AskPlan:
    """Heuristic plan when the Instruct planner is unavailable."""
    q = question.strip()
    recent = format_chat_history_block(history, max_turns=2)
    lower = q.lower()
    is_follow_up = bool(recent) and any(
        phrase in lower
        for phrase in (
            "didn't get",
            "didnt get",
            "don't understand",
            "dont understand",
            "what do you mean",
            "explain again",
            "say that simpler",
            "can you clarify",
            "not clear",
        )
    )
    if is_follow_up:
        return apply_plan_heuristics(
            AskPlan(
                intent_summary=f"Restate the previous answer more simply: {q}",
                retrieval_query=build_retrieval_query(q, history),
                answer_mode=ANSWER_MODE_CLARIFY,
                is_follow_up=True,
            ),
            q,
        )
    return apply_plan_heuristics(
        AskPlan(
            intent_summary=q,
            retrieval_query=build_retrieval_query(q, history),
            answer_mode=ANSWER_MODE_DIRECT,
        ),
        q,
    )


def plan_ask_query(
    question: str,
    history: list[dict[str, str]],
    *,
    use_llm: bool = True,
) -> AskPlan:
    """Plan intent and retrieval query for an Ask Agent turn."""
    q = question.strip()
    if not q:
        return AskPlan(
            intent_summary="Summarize the repository and its main functionality.",
            retrieval_query=OVERVIEW_RETRIEVAL_QUERY,
            answer_mode=ANSWER_MODE_DIRECT,
        )

    if not use_llm:
        return fallback_plan(q, history)

    chat_section = ""
    recent = format_chat_history_block(history, max_turns=2)
    if recent:
        chat_section = f"Recent conversation:\n{recent}\n\n"

    prompt = PLANNER_PROMPT.format(chat_section=chat_section, question=q)
    try:
        from agent.llms import planner_generate

        raw = planner_generate(prompt)
        parsed = _extract_json_object(raw)
        if parsed:
            return apply_plan_heuristics(AskPlan.from_dict(parsed, q), q)
    except Exception:
        pass

    return fallback_plan(q, history)
