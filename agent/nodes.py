"""LangGraph node functions for Codegen, Fix, Judge, router, and Phase-2 paths."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "data" / "scripts"))

from agent.llms import codegen_generate, judge_generate
from agent.prompts import (
    format_fix_prompt,
    format_judge_prompt,
    format_pattern_java,
    format_pseudocode_to_java,
    parse_judge_response,
)
from agent.state import AgentState
from agent.tools import list_repo_files, parse_ast, retrieve_examples, run_python_dict

from prompt_templates import (
    format_java2py_inference,
    format_nl2java_inference,
)


def _trace(step: str, detail: str = "") -> list[dict[str, Any]]:
    return [{"step": step, "detail": detail[:500]}]


def route_input(state: AgentState) -> dict[str, Any]:
    """Thin router (problem B): choose text_to_pl | pl_to_pl | pseudocode_to_fn | pattern | repo."""
    if state.get("repo_root"):
        route = "repo"
    elif state.get("pattern"):
        route = "pattern"
    elif state.get("input_type") == "java" or (
        state.get("java_code") and not state.get("nl_prompt")
    ):
        route = "pl_to_pl"
    elif state.get("input_type") == "pseudocode":
        route = "pseudocode_to_fn"
    else:
        route = "text_to_pl"

    return {
        "route": route,
        "trace": _trace("route", route),
    }


def maybe_retrieve(state: AgentState) -> dict[str, Any]:
    """Optional RAG retrieve before codegen (problem C)."""
    if not state.get("use_rag"):
        return {"rag_context": "", "trace": _trace("retrieve", "skipped")}
    query = state.get("nl_prompt") or state.get("java_code") or ""
    task = "java2py" if state.get("route") == "pl_to_pl" else "nl2py"
    ctx = retrieve_examples.invoke({"query": query, "task": task, "top_k": 3})
    return {"rag_context": ctx or "", "trace": _trace("retrieve", f"chars={len(ctx or '')}")}


def nl_to_java(state: AgentState) -> dict[str, Any]:
    """Codegen Agent step 1: natural language → Java."""
    unit = state.get("unit", "function")
    few = (state.get("rag_context") or "") + "\n" if state.get("rag_context") else ""
    prompt = few + format_nl2java_inference(state["nl_prompt"])
    if unit == "class":
        prompt = prompt.replace("Write Java for:", "Write a Java class for:")
    java_code = codegen_generate(prompt)
    return {
        "java_code": java_code,
        "trace": _trace("nl_to_java", java_code[:200]),
    }


def java_to_python(state: AgentState) -> dict[str, Any]:
    """Codegen Agent step 2: Java → Python."""
    few = (state.get("rag_context") or "") + "\n" if state.get("rag_context") else ""
    prompt = few + format_java2py_inference(state["java_code"])
    python_code = codegen_generate(prompt)
    return {
        "python_code": python_code,
        "trace": _trace("java_to_python", python_code[:200]),
    }


def pseudocode_to_java(state: AgentState) -> dict[str, Any]:
    """Problem B/pseudocode path: pseudocode → Java."""
    prompt = format_pseudocode_to_java(state["nl_prompt"], unit=state.get("unit", "function"))
    java_code = codegen_generate(prompt)
    return {
        "java_code": java_code,
        "trace": _trace("pseudocode_to_java", java_code[:200]),
    }


def pattern_to_java(state: AgentState) -> dict[str, Any]:
    """Problem D: design-pattern oriented Java skeleton (defaults to class unit)."""
    unit = state.get("unit") or "class"
    prompt = format_pattern_java(
        state.get("nl_prompt", ""),
        state.get("pattern", ""),
        unit=unit,
    )
    java_code = codegen_generate(prompt)
    return {
        "java_code": java_code,
        "unit": unit,
        "trace": _trace("pattern_to_java", java_code[:200]),
    }


def repo_prepare(state: AgentState) -> dict[str, Any]:
    """Problem F: list toy repo files and seed nl_prompt context."""
    root = state.get("repo_root") or ""
    raw = list_repo_files.invoke({"repo_root": root})
    import json

    try:
        files = json.loads(raw).get("files", [])
    except Exception:
        files = []
    return {
        "repo_files": files,
        "trace": _trace("repo_prepare", f"files={files}"),
    }


def execute_python(state: AgentState) -> dict[str, Any]:
    """Sandbox tool node."""
    code = state.get("python_code") or ""
    result = run_python_dict(code, timeout=10)
    stdout = result.get("stdout") or ""
    stderr = result.get("stderr") or result.get("error") or ""
    exit_ok = bool(result.get("passed") or result.get("exit_ok"))
    return {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": 0 if exit_ok else 1,
        "attempts": int(state.get("attempts") or 0) + 1,
        "trace": _trace("execute", f"exit_ok={exit_ok}"),
    }


def attach_ast(state: AgentState) -> dict[str, Any]:
    """Problem E: attach AST summary before fix (also cheap before judge)."""
    info = parse_ast.invoke({"code": state.get("python_code") or "", "language": "python"})
    return {"ast_info": info, "trace": _trace("parse_ast", info[:200])}


def judge_intent(state: AgentState) -> dict[str, Any]:
    """LLM judge: does runtime output satisfy the original NL request?"""
    nl = state.get("nl_prompt") or "Translate the provided Java correctly and run without errors."
    # If there is no NL (pure java path), judge on clean execution
    if not state.get("nl_prompt") and state.get("route") == "pl_to_pl":
        yes = state.get("exit_code", 1) == 0
        reason = "Clean exit" if yes else (state.get("stderr") or "Runtime error")
        return {
            "judge_yes": yes,
            "judge_reason": reason,
            "trace": _trace("judge", f"{yes}: {reason}"),
        }

    prompt = format_judge_prompt(
        nl,
        state.get("stdout", ""),
        state.get("stderr", ""),
        int(state.get("exit_code", 1)),
    )
    # Hard fail on nonzero exit — judge only grades successful runs against NL.
    if int(state.get("exit_code", 1)) != 0:
        reason = f"Runtime failure: {(state.get('stderr') or state.get('stdout') or 'nonzero exit')[:200]}"
        return {
            "judge_yes": False,
            "judge_reason": reason,
            "trace": _trace("judge", f"False: {reason}"),
        }

    raw = judge_generate(prompt)
    yes, reason = parse_judge_response(raw)
    return {
        "judge_yes": yes,
        "judge_reason": reason,
        "trace": _trace("judge", f"{yes}: {reason}"),
    }


def fix_python(state: AgentState) -> dict[str, Any]:
    """Fix Agent: repair Python only using NL + stderr + optional AST."""
    runtime = "\n".join(
        x for x in [state.get("stdout", ""), state.get("stderr", "")] if x
    )
    # Lower temperature on later retries
    attempts = int(state.get("attempts") or 0)
    temperature = max(0.05, 0.3 - 0.05 * attempts)
    prompt = format_fix_prompt(
        state.get("nl_prompt") or "Fix the Python translation of the Java code.",
        state.get("python_code") or "",
        runtime,
        unit=state.get("unit", "function"),
        ast_info=state.get("ast_info") or "",
    )
    fixed = codegen_generate(prompt, temperature=temperature)
    return {
        "python_code": fixed,
        "trace": _trace("fix_python", fixed[:200]),
    }


def should_continue(state: AgentState) -> str:
    """Conditional edge after judge: end or fix."""
    if state.get("judge_yes"):
        return "end"
    attempts = int(state.get("attempts") or 0)
    max_retries = int(state.get("max_retries") or 3)
    if attempts >= max_retries:
        return "end"
    return "fix"


def route_after_router(state: AgentState) -> str:
    return state.get("route") or "text_to_pl"
