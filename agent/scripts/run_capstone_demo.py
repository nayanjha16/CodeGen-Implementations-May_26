#!/usr/bin/env python3
"""Capstone demo walkthrough — Stage 9.

Runs a curated set of Chinook scenarios (text2sql, sql2nosql, nosql2doc).
Use for presentations; does not modify databases.

Examples:
    python agent/scripts/run_capstone_demo.py --list
    python agent/scripts/run_capstone_demo.py
    python agent/scripts/run_capstone_demo.py --ids D1,D3,S1
    python agent/scripts/run_capstone_demo.py --reliable-only
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from typing import Literal

from agent.orchestration import AgentRunner, run_agent_graph

IntentKind = Literal["text2sql", "sql2nosql", "nosql2doc", "explain_sql", "validate_sql"]


@dataclass(frozen=True)
class DemoScenario:
    id: str
    title: str
    intent: IntentKind | None
    question: str = ""
    sql: str = ""
    reliable: bool = True

    def user_message(self) -> str:
        if self.intent == "sql2nosql" and self.sql and not self.question:
            return f"Convert this SQL to MongoDB:\n{self.sql}"
        return self.question


CAPSTONE_SCENARIOS: tuple[DemoScenario, ...] = (
    DemoScenario(
        "D1",
        "Album titles with artist names (2-table join)",
        None,
        question="List album titles with artist names.",
    ),
    DemoScenario(
        "D3",
        "Artist with most albums (aggregation)",
        None,
        question="Which artist has the most albums?",
    ),
    DemoScenario(
        "D6",
        "Tracks per genre (2-table join)",
        None,
        question="How many tracks are in each genre?",
    ),
    DemoScenario(
        "D4",
        "Invoice total by country",
        None,
        question="Total invoice amount by customer country.",
        reliable=False,
    ),
    DemoScenario(
        "D2",
        "Top 5 tracks with album and artist (3-table)",
        None,
        question="List the top 5 tracks by unit price with album title and artist name.",
        reliable=False,
    ),
    DemoScenario(
        "S1",
        "SQL to Mongo — customer count",
        "sql2nosql",
        sql='SELECT COUNT(*) FROM "Customer"',
    ),
    DemoScenario(
        "S2",
        "SQL to Mongo — artist album counts (join)",
        "sql2nosql",
        sql=(
            'SELECT ar."Name" AS artist, COUNT(al."AlbumId") AS album_count '
            'FROM "Artist" ar JOIN "Album" al ON ar."ArtistId" = al."ArtistId" '
            'GROUP BY ar."Name" ORDER BY album_count DESC LIMIT 5'
        ),
    ),
    DemoScenario(
        "N1",
        "Document Mongo query",
        "nosql2doc",
        question="Document this query: db.customer.find({}).limit(10)",
    ),
)

DEFAULT_IDS = ("D1", "D3", "D6", "S1", "N1")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run capstone demo scenarios (Stage 9)")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List scenarios and exit",
    )
    parser.add_argument(
        "--ids",
        help=f"Comma-separated scenario ids (default: {','.join(DEFAULT_IDS)})",
    )
    parser.add_argument(
        "--reliable-only",
        action="store_true",
        help="Run only scenarios marked reliable for live demo",
    )
    parser.add_argument(
        "--db-id",
        help="Override demo database id (default from agent/.env)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print one JSON object per scenario",
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=0.0,
        help="Seconds to pause between scenarios (presentations)",
    )
    return parser


def _select_scenarios(args: argparse.Namespace) -> list[DemoScenario]:
    if args.reliable_only:
        return [s for s in CAPSTONE_SCENARIOS if s.reliable]
    if args.ids:
        wanted = {part.strip().upper() for part in args.ids.split(",") if part.strip()}
        selected = [s for s in CAPSTONE_SCENARIOS if s.id in wanted]
        missing = wanted - {s.id for s in selected}
        if missing:
            raise SystemExit(f"Unknown scenario id(s): {', '.join(sorted(missing))}")
        return selected
    return [s for s in CAPSTONE_SCENARIOS if s.id in DEFAULT_IDS]


def _print_list() -> None:
    print("Capstone demo scenarios (Chinook):\n")
    for scenario in CAPSTONE_SCENARIOS:
        flag = "reliable" if scenario.reliable else "optional"
        intent = scenario.intent or "auto"
        print(f"  {scenario.id:4}  [{flag:8}]  {intent:10}  {scenario.title}")
    print(f"\nDefault walkthrough: {', '.join(DEFAULT_IDS)}")
    print("Run: python agent/scripts/run_capstone_demo.py")


def _run_scenario(
    scenario: DemoScenario,
    *,
    runner: AgentRunner,
    db_id: str | None,
) -> dict:
    started = time.perf_counter()
    result = run_agent_graph(
        scenario.user_message(),
        explicit_intent=scenario.intent,
        db_id=db_id,
        sql=scenario.sql or None,
        runner=runner,
    )
    elapsed = time.perf_counter() - started
    return {
        "id": scenario.id,
        "title": scenario.title,
        "intent": result.intent,
        "ok": result.error is None,
        "elapsed_sec": round(elapsed, 1),
        "answer": result.answer,
        "sql": result.sql,
        "mongo_query": result.mongo_query,
        "row_count": len(result.rows),
        "error": result.error,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        _print_list()
        return 0

    try:
        scenarios = _select_scenarios(args)
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 1

    results: list[dict] = []
    failures = 0

    print(f"Capstone demo — {len(scenarios)} scenario(s)\n")

    with AgentRunner() as runner:
        for index, scenario in enumerate(scenarios, start=1):
            print(f"=== [{scenario.id}] {scenario.title} ===")
            if not scenario.reliable:
                print("(optional — may be slow or model-dependent)")

            try:
                payload = _run_scenario(scenario, runner=runner, db_id=args.db_id)
            except (RuntimeError, ValueError) as exc:
                payload = {
                    "id": scenario.id,
                    "title": scenario.title,
                    "ok": False,
                    "error": str(exc),
                }

            results.append(payload)
            if not payload.get("ok", False):
                failures += 1

            if args.json:
                print(json.dumps(payload, indent=2, default=str))
            else:
                print(payload.get("answer", ""))
                if payload.get("sql"):
                    print(f"\nSQL:\n{payload['sql']}")
                if payload.get("mongo_query"):
                    print(f"\nMongo:\n{payload['mongo_query']}")
                if payload.get("error"):
                    print(f"\nError: {payload['error']}", file=sys.stderr)
                print(f"\n({payload.get('elapsed_sec', '?')}s, rows={payload.get('row_count', 0)})")

            if index < len(scenarios) and args.pause > 0:
                time.sleep(args.pause)
            print()

    passed = len(scenarios) - failures
    print(f"Done: {passed}/{len(scenarios)} completed without error.")
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
