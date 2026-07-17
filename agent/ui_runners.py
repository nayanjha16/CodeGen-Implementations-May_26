"""Standalone Generate / Fix agent runners for UI and API (no full loop)."""

from __future__ import annotations

from typing import Any

from agent.nodes import attach_ast, fix_python, java_to_python, maybe_retrieve, nl_to_java
from agent.state import UnitType, initial_state


def _merge(state: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    """Merge node output into state, appending trace entries."""
    traces = list(state.get("trace") or []) + list(update.get("trace") or [])
    merged = {**state, **update, "trace": traces}
    return merged


def run_generate_agent(
    nl_prompt: str,
    *,
    unit: UnitType = "function",
    use_rag: bool = False,
) -> dict[str, Any]:
    """Generate Agent only: NL → Java → Python (no execute / judge / fix)."""
    if not (nl_prompt or "").strip():
        raise ValueError("nl_prompt is required for Generate Agent")

    state: dict[str, Any] = dict(initial_state(nl_prompt, unit=unit, use_rag=use_rag))
    if use_rag:
        state = _merge(state, maybe_retrieve(state))

    state = _merge(state, nl_to_java(state))
    state = _merge(state, java_to_python(state))

    return {
        "prompt": state.get("nl_prompt") or nl_prompt,
        "java_code": state.get("java_code") or "",
        "python_code": state.get("python_code") or "",
        "unit": state.get("unit") or unit,
        "route": "text_to_pl",
        "trace": list(state.get("trace") or []),
        "task": "agent_generate",
    }


def run_fix_agent(
    nl_prompt: str,
    python_code: str,
    *,
    runtime: str = "",
    unit: UnitType = "function",
) -> dict[str, Any]:
    """Fix Agent only: repair Python given NL + code + runtime/error."""
    if not (python_code or "").strip():
        raise ValueError("python_code is required for Fix Agent")

    state: dict[str, Any] = dict(initial_state(nl_prompt or "Fix the Python code.", unit=unit))
    state["python_code"] = python_code
    state["stderr"] = runtime or ""
    state["stdout"] = ""

    state = _merge(state, attach_ast(state))
    before_ast = state.get("ast_info") or ""
    state = _merge(state, fix_python(state))
    # Re-parse after repair so the UI shows diagnosis of the input, not a failure.
    after = attach_ast(state)
    after_ast = after.get("ast_info") or ""
    state = _merge(state, after)
    ast_info = f"Before fix: {before_ast}\nAfter fix: {after_ast}"

    return {
        "prompt": state.get("nl_prompt") or nl_prompt,
        "python_code": state.get("python_code") or "",
        "ast_info": ast_info,
        "unit": state.get("unit") or unit,
        "runtime": runtime,
        "trace": list(state.get("trace") or []),
        "task": "agent_fix",
    }
