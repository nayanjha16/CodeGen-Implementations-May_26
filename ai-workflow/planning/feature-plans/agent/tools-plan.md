# Three Tools — Full Spec Plan

> Maps to `agent.md` §7 (MCP Tools) and §10 (FastAPI endpoints via HTTP adapter).

---

## Tool 1 — Schema extraction (`tools/schema_tool.py`)

**Spec input:**

```json
{ "question": "..." }
```

**Spec output:**

```json
{
  "tables": [],
  "columns": [],
  "relationships": []
}
```

**Implementation additions:**

- `db_id` parameter (agent config default or user override)
- `schema_ddl` string for CodeGen prompts (CREATE TABLE blocks)
- Live introspection via `database/postgres.py` (SQLAlchemy / information_schema)
- Mongo metadata via `database/mongodb.py` for sql2nosql flows

**Algorithm (initial build):**

1. List tables for schema `db_id`
2. Keyword match question ↔ table/column names
3. Expand FK-related tables
4. Build relationships array from FK metadata
5. Emit DDL + structured JSON per spec

*(Spec §13 Phase 3 vector search is future — not initial build.)*

---

## Tool 2 — Capstone FastAPI (`tools/fastapi_tool.py`)

**Spec endpoints:**

```text
POST /generate/sql
POST /generate/nosql
POST /generate/documentation
POST /generate/explanation
GET  /health
```

**Implementation:** `clients/codegen_client.py` exposes the same method names but calls deployed API:

| Spec method | HTTP |
| --- | --- |
| `generate_sql` | `POST {BASE}/v1/chat/completions` + `"intent": "text2sql"` |
| `generate_nosql` | `POST ...` + `"intent": "sql2nosql"` |
| `generate_documentation` | `POST ...` + `"intent": "nosql2doc"` |
| `generate_explanation` | Orchestrator LLM explains SQL (no 4th LoRA); optional API prompt for doc-style output |
| `health` | `GET {BASE}/health` |

**Message body (text2sql):**

```text
Schema:
CREATE TABLE singer (...);

Question:
How many singers do we have?
```

**sql2nosql message:**

```text
SQL:
SELECT ...

NoSQL schema:
{ ... }

MongoDB:
```

**Always pass `"intent"`** — CodeGen classifier swaps LoRA adapter:

```text
intent: text2sql  → codegen-350M-text2sql-lora
intent: sql2nosql → codegen-350M-sql2nosql-lora
intent: nosql2doc → codegen-350M-nosql2doc-lora
```

**Retry (FR-5):** append to user message:

```text
Previous SQL: ...
Database error: ...
Generate corrected SQL only.
```

**Config:**

```bash
CODEGEN_BASE_URL=https://codegen-api-161349047936.asia-south2.run.app
CODEGEN_TIMEOUT=120
```

---

## Tool 3 — Execution (`tools/execution_tool.py`)

**Spec input:**

```json
{ "query": "..." }
```

**Spec output:**

```json
{ "rows": [] }
```

**Implementation:**

| Engine | Module | Notes |
| --- | --- | --- |
| Postgres | `database/postgres.py` | SELECT only; schema = `db_id` |
| MongoDB | `database/mongodb.py` | find / aggregate for sql2nosql |

Extended response for agent retry:

```json
{
  "rows": [],
  "success": true,
  "error": null,
  "row_count": 0
}
```

**Pre-execute validation (spec §5):** `lib/sql_validation.py`

- syntax check
- referenced tables exist in schema tool output
- block unsafe statements (DROP, DELETE, etc.)

---

## MCP registration (`mcp/registry.py`)

| MCP name | Python function |
| --- | --- |
| `extract_schema` | `schema_tool.extract` |
| `codegen_generate` | `fastapi_tool.generate_*` |
| `execute_query` | `execution_tool.run` |

LangGraph and MCP share the same tool implementations.

---

## Sequence (spec §9) — all paths

### Text2SQL

```text
User → Agent → Schema Tool → FastAPI (text2sql) → Execution (PG) → Summary → User
```

### SQL2NoSQL

```text
User → Agent → FastAPI (sql2nosql) → Execution (Mongo) → Summary → User
```

### Documentation

```text
User → Agent → FastAPI (nosql2doc) → Summary → User
```

### Explain / Validate

```text
User → Agent → [validate] → Ollama explain OR validation result → User
```
