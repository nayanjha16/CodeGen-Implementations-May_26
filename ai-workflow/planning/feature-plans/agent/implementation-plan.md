# Implementation Plan — Full `agent.md` Spec

> **Source of truth:** [../../../../agent/doc/agent.md](../../../../agent/doc/agent.md)  
> **Constraint:** All code under `agent/` only. Reuse logic via imports or thin wrappers inside `agent/` — do **not** modify `src/` or `fastapi-deploy/`.  
> **Orchestrator LLM:** No GPT-5 — see [llm-alternative.md](llm-alternative.md).

---

## 1. What we are building (full spec, not a cut-down MVP)

| `agent.md` section | Deliverable |
| --- | --- |
| FR-1 User query + intent | `agent/intent_detector.py` |
| FR-2 Schema extraction | `tools/schema_tool.py` |
| FR-3 Query generation | `tools/fastapi_tool.py` → HTTP `/v1/chat/completions` |
| FR-4 Execution | `tools/execution_tool.py` + `database/postgres.py`, `mongodb.py` |
| FR-5 Error recovery (max 3) | `agent/retry.py` + LangGraph loop |
| FR-6 NL response | `agent/planner.py` + orchestrator LLM (Ollama) |
| §5 All capabilities | text2sql, sql2nosql, documentation, explain SQL, validation |
| §7 MCP tools | `mcp/server.py`, `mcp/registry.py` |
| §8 Workflow | LangGraph graph in `agent/main.py` |
| §11 Agent prompt | `agent/prompts.py` |
| §12 Project structure | Nested under `agent/` (see below) |

**Future enhancements (§13)** — conversation memory, human approval, vector schema — are **out of initial build** unless time permits; the initial build matches §1–§12.

---

## 2. Folder layout (spec §12, rooted at `agent/`)

```text
agent/
├── README.md
├── doc/
│   └── agent.md                 # your original spec (unchanged)
├── doc/agent.md                 # spec (planning lives in ai-workflow/planning/feature-plans/agent/)
├── config/
│   └── settings.py
├── agent/
│   ├── main.py                  # CLI + graph entry
│   ├── planner.py               # plan steps per intent
│   ├── prompts.py               # system prompt §11
│   ├── intent_detector.py       # FR-1
│   └── retry.py                 # FR-5
├── mcp/
│   ├── server.py
│   └── registry.py
├── tools/
│   ├── schema_tool.py           # MCP Tool 1
│   ├── fastapi_tool.py          # MCP Tool 2 (HTTP adapter)
│   └── execution_tool.py        # MCP Tool 3
├── database/
│   ├── postgres.py              # SQLAlchemy / psycopg
│   └── mongodb.py               # PyMongo
├── clients/
│   └── codegen_client.py        # maps spec /generate/* → /v1/chat/completions
├── lib/                         # optional: vendored helpers imported from repo patterns
│   └── sql_validation.py        # wrap validation rules (syntax, unsafe)
├── logs/
├── tests/
├── requirements.txt
└── .env.example
```

**Note:** Spec lists `capstone_api/app.py` — that **already exists** as `fastapi-deploy/codegen_api/`. The agent uses **`clients/codegen_client.py`** only (HTTP). No duplicate FastAPI app inside `agent/`.

---

## 3. Capstone API — spec vs deployed (adapter layer)

`agent.md` §10 shows `POST /generate/sql`. Deployed Cloud Run uses OpenAI chat completions.

| Spec method (`fastapi_tool.py`) | HTTP implementation (`codegen_client.py`) |
| --- | --- |
| `generate_sql(question, schema)` | `POST /v1/chat/completions` + `"intent": "text2sql"` |
| `generate_nosql(sql, nosql_schema)` | `POST /v1/chat/completions` + `"intent": "sql2nosql"` |
| `generate_documentation(mongodb_query, ...)` | `POST /v1/chat/completions` + `"intent": "nosql2doc"` |
| `generate_explanation(sql)` | Same HTTP API; user message asks for step-by-step explanation (no separate LoRA — see §5) |
| `health()` | `GET /health` |

User message format (matches training):

```text
Schema:
CREATE TABLE ...

Question:
...
```

Always pass `"intent"` so CodeGen classifier + LoRA routing is deterministic.

---

## 4. Three MCP tools (full spec §7)

### Tool 1 — Schema extraction

**Input:** `{ "question": "...", "db_id": "concert_singer" }`  
**Output:** `{ "tables": [], "columns": [], "relationships": [] }` plus `schema_ddl` for the API.

**Implementation:**

- Live Postgres introspection (`database/postgres.py`) — `information_schema`, FK metadata  
- PyMongo collection listing for NoSQL path (`database/mongodb.py`)  
- Reuse patterns from repo eval/TEND; implement under `agent/database/` (may import shared utilities copied into `agent/lib/` if needed)

### Tool 2 — Capstone FastAPI

**Purpose:** All generative SQL / Mongo / doc tasks via **fine-tuned CodeGen on Cloud Run**.

**Never generates SQL inside the agent process** — only HTTP calls.

### Tool 3 — Execution

**Input:** `{ "query": "...", "db_id": "...", "engine": "postgres" | "mongo" }`  
**Output:** `{ "rows": [], "success": bool, "error": "..." }`

- Postgres: read-only, block DDL/DML  
- Mongo: run aggregation / find for sql2nosql validation path  

---

## 5. Supported capabilities (spec §5) — how each works

| Capability | Agent flow | Generative model |
| --- | --- | --- |
| **Text → SQL** | Schema tool → `generate_sql` → execute Postgres | CodeGen text2sql LoRA |
| **SQL → MongoDB** | Optional SQL input → `generate_nosql` → execute Mongo | CodeGen sql2nosql LoRA |
| **SQL documentation** | SQL or Mongo → `generate_documentation` | CodeGen nosql2doc LoRA |
| **Explain SQL** | User provides SQL → orchestrator LLM **or** doc-style prompt via API | Ollama explains; optional API prompt |
| **Query validation** | Before execute: `lib/sql_validation.py` (syntax, tables, unsafe) | Rule-based — no GPT |

**Explain SQL:** Deployed API has three intents only (`text2sql`, `sql2nosql`, `nosql2doc`). Explanation is handled by the **orchestrator LLM** (Ollama) reading SQL + schema context — it must **not** invent a new query, only explain the given SQL (aligns with §6 “agent never generates SQL” for new queries; explanation is NL only).

---

## 6. Agent workflow (spec §8) — LangGraph

```text
User query
    → detect_intent          (orchestrator LLM or rules + LLM fallback)
    → plan                   (planner.py — which tools for this intent)
    → extract_schema         (if intent needs schema)
    → validate_query         (optional pre-check)
    → call_fastapi           (generate_sql | nosql | doc)
    → execute                (if intent needs execution)
    → on error: retry ≤ 3     (retry.py — error back to FastAPI tool)
    → summarize              (orchestrator LLM — FR-6)
    → return
```

All steps are **tool nodes** exposed to MCP.

---

## 7. Intent detection (FR-1)

| Intent | Triggers | Tool chain |
| --- | --- | --- |
| `text2sql` | NL question about data | schema → generate_sql → execute postgres |
| `sql2nosql` | SQL or “convert to mongo” | generate_nosql → execute mongo |
| `nosql2doc` | “document this query” | generate_documentation |
| `explain_sql` | “explain this SQL” | schema optional → Ollama explanation |
| `validate_sql` | “is this safe / valid” | validation lib only |

**Orchestrator LLM** (Ollama, not GPT) classifies intent with tool-calling or JSON schema output. CodeGen API gets its **own** `"intent"` for LoRA routing separately.

---

## 8. Error recovery (FR-5)

```text
execution error
    → agent/retry.py increments attempt
    → if attempt ≤ 3:
          fastapi_tool.generate_sql(
              question, schema,
              previous_sql=...,
              db_error=...
          )
    → else: return failure summary to user
```

Same pattern for Mongo execution errors on sql2nosql path.

---

## 9. Reuse from repo (inside `agent/` only)

| Need | Approach |
| --- | --- |
| SQL validation rules | Copy or thin-wrap into `agent/lib/sql_validation.py` (from `src/text2sql/sql_validator.py` patterns) |
| Prompt shape | **Import** from `src` prompt builders in `clients/codegen_client.py` |
| DB execution semantics | Implement in `agent/database/` matching TEND connection env |
| Schema DDL formatting | `agent/tools/schema_tool.py` |

User approved importing patterns **into agent folder** — no edits outside `agent/`.

---

## 10. Technology stack (spec §14 — adjusted)

| Component | Spec | Our choice |
| --- | --- | --- |
| Agent framework | LangGraph | **LangGraph** |
| Orchestrator LLM | GPT-5.5 | **Ollama** — see [llm-alternative.md](llm-alternative.md) |
| Generative SQL/Mongo/Docs | Fine-tuned adapters | **Cloud Run CodeGen API** |
| Tool protocol | MCP | **MCP server in agent/mcp/** |
| API | FastAPI | **Existing codegen_api** (HTTP client only) |
| Databases | PostgreSQL, MongoDB | **TEND Docker** + standalone demos (Chinook, Northwind) |
| DB access | SQLAlchemy + PyMongo | **Yes** under `agent/database/` |

---

## Demo databases (Stage 1b — done)

Two **standalone** Postgres+Mongo demos coexist in TEND Docker. Switch with `AGENT_DEMO_*` env vars.

| Demo | Initial? | Path |
| --- | --- | --- |
| **Chinook** | ✅ Yes | `agent/data/standalone/chinook/` |
| **Northwind** | Optional | `agent/data/standalone/northwind/` |

See [status.md](status.md) and `agent/data/standalone/README.md`.

**Not used:** `tool/` Pagila/DVD — reference only.

---

## 11. Build order (full spec)

| Stage | Work | Status |
| --- | --- | --- |
| **1** | `config/`, `database/postgres.py`, `database/mongodb.py` | ✅ |
| **1b** | `database/profiles.py`, demo data scripts, Chinook + Northwind load | ✅ |
| **2** | `clients/codegen_client.py` — import `src` prompt builders | ⏳ Next |
| **3** | `tools/*.py` — three MCP tools | Pending |
| **4** | `lib/sql_validation.py` | Pending |
| **5** | `agent/intent_detector.py`, `prompts.py`, `planner.py`, `retry.py` | Pending |
| **6** | LangGraph in `agent/main.py` — all intents | Pending |
| **7** | `mcp/server.py` + `registry.py` | Pending |
| **8** | `tests/` — unit + Docker integration | Pending |
| **9** | Standalone CLI demo | Pending |

---

## 12. Testing (see testing-strategy.md)

- Gold-set parity: agent on same db_ids as eval  
- All five capabilities (§5) with manual + automated cases  
- MCP tool invocation smoke tests  

---

## 13. Decisions locked

| Topic | Decision |
| --- | --- |
| Codegen API | HTTP adapter to `/v1/chat/completions`, always pass `intent` |
| GPT-5 | **Not used** — Ollama local orchestrator |
| Scope | **Full agent.md §1–§12**, not phased MVP |
| Code location | **`agent/` only** |
| Inference | Cloud Run LoRA **v3** (published) |
| Demo DB | **Chinook** initial; Northwind optional via env |

---

## 14. Code reuse

See [reuse-strategy.md](reuse-strategy.md) — import from `src` where safe; new code in `agent/database/` for DB access.

## 15. Approval

Orchestrator model: decide **after eval** — see [llm-alternative.md](llm-alternative.md) (Qwen 2.5 7B fits 24 GB RAM via Ollama; gemma3:4b fallback). Then implementation starts at Stage 1.
