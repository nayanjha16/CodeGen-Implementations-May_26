# Approval — TENDv2 (Ollama)

> **Feature:** `tendv2-ollama` · **Date:** 2026-06-24

## Status: APPROVED

User approved scope and key decisions on 2026-06-24 (interactive confirmation).

## Approved Scope

- New `TENDv2/` pipeline mirroring `TENDv1/` but using local Ollama for
  MongoDB conversion, documentation generation, and evaluation.
- Code generator: `qwen2.5-coder:3b` (Mongo schema, Mongo query, documentation).
- Judge: `qwen3:4b` (evaluation true/false + summary).
- Required CSV columns: question, sql_schema, sql_query, nosql_schema,
  nosql_query, documentation, evaluation_result, evaluation_summary, metadata.
- Async code generation + validation with bounded concurrency.
- Spider first, BIRD second (both train/test splits).

## Approved Decisions

| Decision | Choice |
|----------|--------|
| Codegen request strategy | One combined JSON call **with fallback to per-field calls** to preserve accuracy |
| Ollama util location | `src/llm/ollama_client.py` (shared, reusable) |
| Formal plan files | Written before implementation (this folder) |
| First implementation scope | Full pipeline + Spider, then add BIRD |

## Rejected / Deferred

- Always-separate codegen calls (rejected in favor of combined + fallback).
- Execution-based equivalence checks (deferred).
- Streaming responses (deferred; `stream:false`).

## Revision History

| Date | Change |
|------|--------|
| 2026-06-24 | Initial plan created and approved |
