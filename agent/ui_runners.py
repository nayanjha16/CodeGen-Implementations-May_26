"""Standalone Generate / Fix agent runners for UI and API (no full loop)."""

from __future__ import annotations

from typing import Any

from agent.nodes import (
    attach_ast,
    fix_python,
    java_to_python,
    maybe_retrieve,
    nl_to_java,
    pattern_to_java,
    pseudocode_to_java,
    route_input,
)
from agent.state import InputType, UnitType, _detect_unit, initial_state


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
    input_type: InputType | None = None,
    pattern: str = "",
) -> dict[str, Any]:
    """Generate Agent: NL / pseudocode / pattern → Java → Python (no execute/judge/fix).

    ``input_type`` defaults to ``None`` so the router auto-classifies the input
    (and extracts a design-pattern name) unless a caller forces a specific type.
    """
    if not (nl_prompt or "").strip():
        raise ValueError("nl_prompt is required for Generate Agent")

    state: dict[str, Any] = dict(
        initial_state(
            nl_prompt,
            unit=unit,
            use_rag=use_rag,
            input_type=input_type,
            pattern=pattern or "",
        )
    )
    state = _merge(state, route_input(state))
    if use_rag:
        state = _merge(state, maybe_retrieve(state))

    route = state.get("route") or "text_to_pl"
    if route == "pattern":
        state = _merge(state, pattern_to_java(state))
    elif route == "pseudocode_to_fn":
        state = _merge(state, pseudocode_to_java(state))
    else:
        state = _merge(state, nl_to_java(state))

    state = _merge(state, java_to_python(state))

    return {
        "prompt": state.get("nl_prompt") or nl_prompt,
        "java_code": state.get("java_code") or "",
        "python_code": state.get("python_code") or "",
        "unit": state.get("unit") or unit,
        "route": state.get("route") or "text_to_pl",
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

    # Auto-detect the unit from the code (and request) unless explicitly set.
    if unit == "auto":
        unit = _detect_unit(f"{python_code}\n{nl_prompt or ''}")

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
