"""CLI entry point for the database agent (Stage 6)."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from agent.orchestration import AgentRunner, run_agent_graph


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AI Database Agent — LangGraph orchestrator + CodeGen tools",
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="Natural language question or instruction",
    )
    parser.add_argument(
        "--intent",
        choices=["text2sql", "sql2nosql", "nosql2doc", "explain_sql", "validate_sql"],
        help="Force intent instead of auto-detection",
    )
    parser.add_argument("--db-id", help="Database id (TEND schema or standalone demo id)")
    parser.add_argument("--dataset", help="TEND dataset catalog (default: spider)")
    parser.add_argument("--sql", help="SQL input for sql2nosql / explain / validate")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full result as JSON",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run capstone walkthrough (same as: python agent/scripts/run_capstone_demo.py)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.demo:
        from agent.scripts.run_capstone_demo import main as run_capstone_demo

        return run_capstone_demo([])

    if not args.question and not args.sql:
        parser.error("Provide a question or --sql")

    user_message = args.question or args.sql or ""
    if args.intent == "sql2nosql" and args.sql and not args.question:
        user_message = f"Convert this SQL to MongoDB:\n{args.sql}"

    try:
        with AgentRunner() as runner:
            result = run_agent_graph(
                user_message,
                explicit_intent=args.intent,
                db_id=args.db_id,
                dataset=args.dataset,
                sql=args.sql,
                runner=runner,
            )
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        payload: dict[str, Any] = result.to_dict()
        print(json.dumps(payload, indent=2, default=str))
    else:
        print(result.answer)
        if result.sql and args.intent != "explain_sql":
            print(f"\nSQL:\n{result.sql}")
        if result.mongo_query:
            print(f"\nMongo:\n{result.mongo_query}")

    return 0 if not result.error else 2


if __name__ == "__main__":
    raise SystemExit(main())
