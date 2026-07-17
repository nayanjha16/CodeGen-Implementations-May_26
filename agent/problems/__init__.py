"""Phase-2 problem pack: scenarios that exercise LangGraph / LangChain features."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROBLEMS_DIR = Path(__file__).resolve().parent
REPO_TOY_DIR = PROBLEMS_DIR / "repo_toy"
PROJECT_ROOT = PROBLEMS_DIR.parent.parent


def load_problem_pack() -> list[dict[str, Any]]:
    """Load curated problems from problems/pack.json."""
    path = PROBLEMS_DIR / "pack.json"
    if not path.exists():
        return list_builtin_problems()
    problems = json.loads(path.read_text(encoding="utf-8"))
    return [_normalize_problem(p) for p in problems]


def _normalize_problem(p: dict[str, Any]) -> dict[str, Any]:
    out = dict(p)
    repo = out.get("repo_root")
    if repo and not Path(repo).is_absolute():
        candidate = PROJECT_ROOT / repo
        out["repo_root"] = str(candidate if candidate.exists() else REPO_TOY_DIR)
    return out


def list_builtin_problems() -> list[dict[str, Any]]:
    """Fallback inline pack (A–F)."""
    return [
        {
            "id": "A_add_two_numbers",
            "type": "function_synthesis",
            "unit": "function",
            "nl_prompt": "Write a program that prints the sum of 2 and 3.",
            "features": ["codegen", "execute", "judge", "fix"],
        },
        {
            "id": "B_router_java_input",
            "type": "task_router",
            "unit": "function",
            "input_type": "java",
            "java_code": (
                "public class Main {\n"
                "  public static void main(String[] args) {\n"
                "    System.out.println(2 + 3);\n"
                "  }\n"
                "}"
            ),
            "nl_prompt": "",
            "features": ["router", "pl_to_pl"],
        },
        {
            "id": "B_pseudocode_factorial",
            "type": "pseudocode_to_fn",
            "unit": "function",
            "input_type": "pseudocode",
            "nl_prompt": (
                "Algorithm: Factorial\n"
                "Begin\n"
                "  Set n = 5\n"
                "  Set result = 1\n"
                "  For i from 1 to n\n"
                "    result = result * i\n"
                "  End for\n"
                "  Print result\n"
                "End"
            ),
            "features": ["router", "pseudocode"],
        },
        {
            "id": "C_rag_assisted",
            "type": "rag_assisted",
            "unit": "function",
            "use_rag": True,
            "nl_prompt": "Print whether 7 is a prime number as true or false.",
            "features": ["rag", "retrieve"],
        },
        {
            "id": "D_singleton_logger",
            "type": "design_pattern",
            "unit": "class",
            "pattern": "Singleton",
            "nl_prompt": (
                "Create a Singleton Logger class with a getInstance method "
                "and a log(message) method that prints the message."
            ),
            "features": ["pattern", "class"],
        },
        {
            "id": "E_ast_fix_hint",
            "type": "ast_side_info",
            "unit": "function",
            "nl_prompt": "Print the maximum of 10 and 20.",
            "features": ["ast", "fix"],
            "notes": "AST is attached automatically before each Fix Agent call.",
        },
        {
            "id": "F_repo_aware_helper",
            "type": "repo_aware",
            "unit": "function",
            "repo_root": str(REPO_TOY_DIR),
            "nl_prompt": (
                "Add a helper function add(a, b) that returns a+b and print add(2, 3)."
            ),
            "features": ["repo", "list_files"],
        },
    ]


def get_problem(problem_id: str) -> dict[str, Any]:
    for p in load_problem_pack():
        if p["id"] == problem_id:
            return p
    raise KeyError(f"Unknown problem id: {problem_id}")
