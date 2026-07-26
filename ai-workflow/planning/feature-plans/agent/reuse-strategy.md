# Reuse vs Separate Code — Agent Folder

> **Rule:** All **new** agent code lives under `agent/`. We do **not** edit `src/` or `fastapi-deploy/`.

## Short answer

| Component | Reuse or separate? | Why |
| --- | --- | --- |
| **CodeGen inference** | **Reuse via HTTP** | Cloud Run / local `codegen_api` already deployed — `agent/clients/codegen_client.py` only |
| **SQL validation rules** | **Reuse import** from `src` | Stable, tested; read-only import, no edits to `src/` |
| **Prompt format / constants** | **Reuse import** from `src` | Keeps agent prompts aligned with training |
| **Postgres / Mongo execution** | **Separate in `agent/database/`** | TEND import path conflicts with repo `src` package name |
| **Schema introspection** | **Separate in `agent/tools/schema_tool.py`** | Agent-specific JSON shape per spec §7 |
| **LangGraph / MCP / planner** | **Separate** | Greenfield under `agent/agent/`, `agent/mcp/` |
| **Orchestrator LLM** | **Separate config** | Ollama client in `agent/`; not part of `src/llm/` |

**Principle:** Reuse **libraries and patterns**; duplicate only where **import boundaries** or **spec I/O** differ.

---

## Reuse via import (recommended)

Run agent with repo root on `PYTHONPATH`:

```powershell
cd C:\Users\Bhavani\Documents\Codegen\Latest\CodeGen-Implementations-May_26
$env:PYTHONPATH = (Get-Location).Path
python -m agent.main ...
```

Thin wrappers in `agent/lib/`:

```text
agent/lib/validation.py   → from src.text2sql.sql_validator import ...
agent/lib/prompts.py      → from src.text2sql.prompt_builder import ... (format only)
```

**Pros:** One source of truth; eval and agent stay aligned.  
**Cons:** Agent depends on repo checkout (fine for capstone).

---

## Separate copy in `agent/lib/` (when import fails)

Copy **small** modules into `agent/lib/` if:

- Circular or `src` package name clash (TEND loader imports external `src`)
- You package agent as standalone folder later

Example: execution against TEND — reimplement ~100 lines in `agent/database/postgres.py` using same env vars, not `database_execution.py` import.

**Pros:** Agent folder self-contained.  
**Cons:** Must sync manually if validation rules change.

---

## Never duplicate

| Do not copy | Use instead |
| --- | --- |
| `fastapi-deploy/codegen_api/` | HTTP client |
| LoRA weights / model loader | Cloud Run API |
| Full `src/evaluation/` | Agent has its own tests |

---

## Decision for implementation

| Module | Plan |
| --- | --- |
| `codegen_client.py` | New — HTTP only |
| `sql_validation` | **Import** from `src.text2sql.sql_validator` |
| Prompt DDL layout | **Import** helpers from `src` prompt builders |
| `postgres.py` / `mongodb.py` | **New** under `agent/database/` (same connection env as TEND) |
| `schema_tool.py` | **New** — spec JSON output |
| `fastapi_tool.py` | **New** — wraps client |
| `execution_tool.py` | **New** — calls `agent/database/` |

This matches “code in agent folder, reuse where sensible.”
