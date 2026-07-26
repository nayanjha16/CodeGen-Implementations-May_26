# Task Breakdown — AI Database Agent

> **Feature:** `database-agent`  
> **Date:** 2026-07-26

Complexity: **S** (< 2h), **M** (2–6h), **L** (6–16h), **XL** (> 16h)

---

## Stage 1 — Config + Database Layer

| ID | Task | Depends on | Complexity | Status |
|----|------|------------|------------|--------|
| A-01 | `agent/config/settings.py` — Postgres, Mongo, CodeGen, Ollama, limits | — | S | ✅ |
| A-02 | `agent/database/postgres.py` — read-only SQL, introspection, DDL | A-01 | M | ✅ |
| A-03 | `agent/database/mongodb.py` + `mongo_shell.py` | A-01 | M | ✅ |
| A-04 | `agent/requirements.txt`, `agent/.env.example` | — | S | ✅ |
| A-05 | `agent/tests/test_database_stage1.py` | A-02, A-03 | S | ✅ |

---

## Stage 1b — Standalone Demo Profile

| ID | Task | Depends on | Complexity | Status |
|----|------|------------|------------|--------|
| B-01 | `agent/database/profiles.py` — `tend` vs `standalone` | A-01 | S | ✅ |
| B-02 | Chinook + Northwind SQL dumps under `agent/data/standalone/` | B-01 | M | ✅ |
| B-03 | Setup/mirror/verify scripts | B-02 | M | ✅ |
| B-04 | `AGENT_DEMO_*` env vars (no hardcoded DB) | B-01 | S | ✅ |

---

## Stage 2 — CodeGen HTTP Client

| ID | Task | Depends on | Complexity | Status |
|----|------|------------|------------|--------|
| C-01 | `agent/clients/codegen_client.py` — `/v1/chat/completions` + `intent` | A-01 | M | ✅ |
| C-02 | Import `src` prompt builders (text2sql, sql2nosql, nosql2doc) | C-01 | S | ✅ |
| C-03 | `generate_sql`, `generate_nosql`, `generate_documentation`, `health` | C-01 | M | ✅ |
| C-04 | `agent/tests/test_codegen_client.py` (mocked HTTP) | C-03 | S | ✅ |

---

## Stage 3 — Three MCP Tools

| ID | Task | Depends on | Complexity | Status |
|----|------|------------|------------|--------|
| T-01 | `agent/tools/schema_tool.py` — Postgres/Mongo introspection | A-02, B-01 | M | ✅ |
| T-02 | `agent/tools/fastapi_tool.py` — wraps codegen_client | C-03 | S | ✅ |
| T-03 | `agent/tools/execution_tool.py` — read-only execute | A-02, A-03 | M | ✅ |
| T-04 | `agent/tests/test_tools_stage3.py` | T-01–T-03 | M | ✅ |

---

## Stage 4 — SQL Validation

| ID | Task | Depends on | Complexity | Status |
|----|------|------------|------------|--------|
| V-01 | `agent/lib/sql_validation.py` — import/wrap `src` validator | — | S | ✅ |
| V-02 | Pre-execution safety checks in runner | V-01, T-03 | S | ✅ |
| V-03 | `agent/tests/test_sql_validation.py` | V-01 | S | ✅ |

---

## Stage 5 — Orchestrator (Ollama)

| ID | Task | Depends on | Complexity | Status |
|----|------|------------|------------|--------|
| O-01 | `agent/orchestrator/intent_detector.py` | A-01 | M | ✅ |
| O-02 | `agent/orchestrator/planner.py` — intent → tool chain | O-01 | M | ✅ |
| O-03 | `agent/orchestrator/prompts.py` — system prompt §11 | — | S | ✅ |
| O-04 | `agent/orchestrator/retry.py` — max 3 attempts | T-02, T-03 | M | ✅ |
| O-05 | `agent/clients/orchestrator_llm.py` — Ollama HTTP | A-01 | S | ✅ |
| O-06 | `agent/tests/test_orchestrator_stage5.py` | O-01–O-05 | M | ✅ |

---

## Stage 6 — LangGraph + CLI

| ID | Task | Depends on | Complexity | Status |
|----|------|------------|------------|--------|
| G-01 | `agent/orchestration/graph.py` — LangGraph nodes/edges | O-02, T-01–T-03 | L | ✅ |
| G-02 | `agent/orchestration/runner.py` — invoke graph, format output | G-01 | M | ✅ |
| G-03 | `agent/main.py` — CLI entry | G-02 | S | ✅ |
| G-04 | `agent/tests/test_graph_stage6.py` | G-01–G-03 | M | ✅ |

---

## Stage 7 — MCP Server

| ID | Task | Depends on | Complexity | Status |
|----|------|------------|------------|--------|
| M-01 | `agent/mcp/registry.py` — tool specs + dispatch | T-01–T-03 | M | ✅ |
| M-02 | `agent/mcp/server.py` — stdio MCP | M-01 | M | ✅ |
| M-03 | `agent/tests/test_mcp_stage7.py` | M-01 | S | ✅ |

---

## Stage 8 — Integration Tests

| ID | Task | Depends on | Complexity | Status |
|----|------|------------|------------|--------|
| I-01 | `agent/tests/conftest.py` — Chinook fixture, Docker skip | B-02 | S | ✅ |
| I-02 | `agent/tests/test_integration_stage8.py` — live DB + MCP | I-01, G-02 | L | ✅ |
| I-03 | Retry bugfix — first SQL failure triggers retry | O-04 | S | ✅ |

---

## Stage 9 — Capstone Demo Polish

| ID | Task | Depends on | Complexity | Status |
|----|------|------------|------------|--------|
| D-01 | `agent/scripts/run_capstone_demo.py` — scripted walkthrough | G-03 | S | ✅ |
| D-02 | `agent/scripts/verify_demo_databases.py` | B-03 | S | ✅ |
| D-03 | Demo question sets (`questions.txt`) for Chinook/Northwind | B-02 | S | ✅ |
| D-04 | `agent/tests/test_capstone_demo_stage9.py` | D-01 | S | ✅ |

---

## Stage 10 — Web UI + Query Quality

| ID | Task | Depends on | Complexity | Status |
|----|------|------------|------------|--------|
| W-01 | `agent/web/app.py` — FastAPI + async runner | G-02 | M | ✅ |
| W-02 | Chat UI (`templates/`, `static/`) + progress/timeout | W-01 | M | ✅ |
| W-03 | `agent/lib/text2sql_hints.py` — DDL hints, listing summaries | T-01 | M | ✅ |
| W-04 | `agent/lib/sql_repair.py` — join SELECT column repair | V-01 | M | ✅ |
| W-05 | `strip_invented_where_filters` in sql_validation | V-01 | S | ✅ |
| W-06 | `agent/tests/test_web_ui.py`, `test_sql_repair.py`, `test_text2sql_hints.py` | W-01–W-05 | M | ✅ |

---

## Deferred (spec §13)

| ID | Task | Reason |
|----|------|--------|
| X-01 | Conversation memory across turns | Out of initial build |
| X-02 | Human approval gate before execute | Out of initial build |
| X-03 | Vector schema retrieval | Out of initial build |
| X-04 | HTTP MCP transport (SSE) | stdio sufficient for capstone |
