"""Shared LangGraph state for the codegen agent."""

from __future__ import annotations

import operator
from typing import Annotated, Any, Literal, TypedDict


UnitType = Literal["function", "class", "auto"]
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
    input_type: InputType | None
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
    # When ``input_type`` is unset we only pin the unambiguous java-code case
    # here; the router node (``route_input``) owns full classification so it can
    # fall back to the judge LLM for ambiguous text.
    if input_type is None and java_code.strip() and not nl_prompt.strip():
        input_type = "java"

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
    lower = (text or "").lower()
    markers = (
        "begin",
        "end if",
        "end while",
        "end for",
        "for each",
        "pseudo",
        "algorithm:",
        "procedure ",
        "repeat until",
        "do while",
        "return result",
    )
    return any(m in lower for m in markers)


def _looks_like_java(text: str) -> bool:
    """Heuristic: does the text read as raw Java source (not an NL request)?"""
    raw = text or ""
    lower = raw.lower()
    strong = (
        "public class",
        "private class",
        "public static void main",
        "system.out.print",
        "public static",
        "import java.",
    )
    if any(m in lower for m in strong):
        return True
    # Structural signal: braces plus semicolon-terminated statements.
    has_braces = "{" in raw and "}" in raw
    has_semis = raw.count(";") >= 1
    java_types = any(t in raw for t in ("int ", "void ", "String ", "boolean ", "double "))
    return has_braces and has_semis and java_types


def _detect_pattern(text: str) -> str:
    """Return a recognized design-pattern name mentioned in ``text`` (or "")."""
    from agent.prompts import _first_known_pattern

    lower = (text or "").lower()
    if "pattern" not in lower and "singleton" not in lower:
        # Cheap gate: only treat as a pattern request when the intent is explicit
        # ("... pattern") or a very common standalone keyword (Singleton).
        name = _first_known_pattern(text)
        return name if name and _pattern_intent(lower) else ""
    return _first_known_pattern(text)


def _pattern_intent(lower: str) -> bool:
    verbs = ("implement", "create", "write", "design", "build", "use", "apply")
    return "pattern" in lower or any(v in lower for v in verbs)


def _detect_unit(text: str) -> UnitType:
    """Infer whether a request should produce a ``class`` or a ``function``.

    Uses lightweight keyword cues; defaults to ``function`` when no OOP signals
    are present. Design-pattern requests always imply a class.
    """
    raw = text or ""
    lower = raw.lower()
    if not lower.strip():
        return "function"

    if _detect_pattern(raw) or "class " in raw:
        return "class"

    class_markers = (
        "a class",
        "class named",
        "class that",
        "object-oriented",
        "object oriented",
        " oop",
        "with methods",
        "methods and attributes",
        "attributes and methods",
        "instance of",
        "constructor",
        "getter",
        "setter",
        "inheritance",
        "subclass",
        "encapsulat",
        "singleton",
    )
    if any(m in lower for m in class_markers):
        return "class"
    return "function"
