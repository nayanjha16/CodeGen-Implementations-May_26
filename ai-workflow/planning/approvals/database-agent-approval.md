# Approval Tracking — AI Database Agent

> **Feature:** `database-agent`  
> **Date:** 2026-07-25  
> **Spec:** `agent/doc/agent.md` (full §1–§12)

---

## Approval Status

| Field | Value |
|-------|-------|
| **Status** | **APPROVED** |
| **Approved by** | User |
| **Approved date** | 2026-07-25 |
| **Plan author** | Planning agent |
| **Implementation blocked** | No |

---

## Approved Scope

- [x] Full `agent.md` §1–§12 (not phased MVP)
- [x] All code under `agent/` only — **no edits** to `src/` or `fastapi-deploy/`
- [x] HTTP adapter to Cloud Run `/v1/chat/completions` with explicit `intent`
- [x] Ollama local orchestrator (not GPT-5)
- [x] Three MCP tools + stdio MCP server
- [x] LangGraph workflow + CLI
- [x] TEND + standalone demo profiles (Chinook default, Northwind optional)
- [x] LoRA **v3** on Cloud Run for inference
- [x] Integration tests against live Docker DBs
- [x] Capstone demo scripts (Stage 9)
- [x] Web UI for capstone presentation (Stage 10)
- [x] Query quality helpers (`sql_repair`, `text2sql_hints`, filter stripping)

---

## Rejected / Out of Scope (confirmed)

| Item | Reason |
|------|--------|
| GPT-5 / OpenAI orchestrator | User constraint — Ollama only |
| Local LoRA inference in agent | Cloud Run API only |
| Edits to `src/` or `fastapi-deploy/` | User constraint |
| `/generate/*` shim in codegen_api | Use existing OpenAI-compatible API |
| Conversation memory (§13) | Deferred |
| Human approval gate (§13) | Deferred |
| Vector schema retrieval (§13) | Deferred |
| Retrain LoRA for capstone | Use published v3 |

---

## Locked Decisions

| Topic | Decision |
|-------|----------|
| Orchestrator LLM | Ollama `gemma3:4b` (see `llm-alternative.md`) |
| Demo database | Chinook standalone (`AGENT_DEMO_DB_ID=chinook`) |
| Code reuse | Import `src` prompt builders + sql_validator at runtime |
| API contract | `/v1/chat/completions` + `intent` field |
| Retry limit | Max 3 execution failures |
| Config | Single `agent/.env` (+ root `.env` fallback) |

---

## Open Questions — Resolved

| ID | Question | Resolution |
|----|----------|------------|
| Q-1 | API adapter vs `/generate/*` shim | **Adapter only** — HTTP to Cloud Run |
| Q-4 | Orchestrator LLM | **Ollama** (`gemma3:4b`) |
| Q-9 | Live demo DB | **Chinook** standalone in TEND Docker |
| Q-12 | MVP scope | **Full spec** §1–§12, not text2sql-only |

---

## Sign-off

Implementation complete through Stage 10 (2026-07-26).  
Validation report: `validation/validation-reports/database-agent-validation.md`.
