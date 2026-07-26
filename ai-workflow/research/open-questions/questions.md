# Open Questions — AI Database Agent (`database-agent`)

> **Research date:** 2026-07-19  
> **Status:** **RESOLVED** — see [database-agent-approval.md](../../planning/approvals/database-agent-approval.md) (2026-07-25)

Historical research questions below; all decisions locked at approval time.

## 1. Architecture & API

### Q-1: Capstone API contract — shim or adapter?

**Question:** Should we add `/generate/sql`, `/generate/nosql`, etc. to `codegen_api`, or only build an HTTP client that maps to existing `/v1/chat/completions`?

| Option | Pros | Cons |
|--------|------|------|
| **A. Client adapter only** | No deploy change; faster MVP | Spec diagram differs from implementation |
| **B. Add `/generate/*` routes** | Spec-compliant | Duplicate logic; redeploy Cloud Run |
| **C. Both** | Best of both | Maintenance burden |

**Recommendation for planning:** **Option A** for MVP; optional B later if capstone grading requires exact paths.

---

### Q-2: Where does the agent package live?

**Question:** Follow spec `database-agent/` at repo root, or nest under existing `agent/`?

| Option | Notes |
|--------|-------|
| `agent/` + `tools/` + `mcp/` at repo root | Matches spec §12; `agent/doc/` already exists |
| Separate top-level `database-agent/` | Spec folder name; duplicates `agent/` |

**Recommendation:** Extend **`agent/`** (add Python packages alongside `agent/doc/`) plus top-level `tools/` and `mcp/` — avoids two agent folders.

---

### Q-3: MCP first or LangGraph tools first?

**Question:** Implement LangGraph with native Python tools first, then wrap in MCP — or MCP from day one?

**Recommendation:** LangGraph native tools **first** (Stage 4), MCP wrapper **second** (Stage 5) — reduces debug surface.

---

## 2. Orchestrator LLM

### Q-4: Which LLM powers the agent?

**Question:** Spec says "GPT-5.5 (or compatible)". What is available to the student?

| Option | Cost | Tool calling | Offline |
|--------|------|--------------|---------|
| OpenAI API (gpt-4o-mini / gpt-4.1) | Paid | ✅ Strong | ❌ |
| Azure OpenAI | Paid | ✅ | ❌ |
| Ollama local (llama3, etc.) | Free | ⚠️ Weaker | ✅ |
| No orchestrator — deterministic FSM | Free | N/A | ✅ |

**Impact:** FR-6 (NL summary) and tool selection quality depend on this.

**Planning must decide:** Budget vs demo reliability.

---

### Q-5: Is a local FSM acceptable for capstone if labeled "agent"?

**Question:** Could a deterministic state machine (without LLM orchestrator) satisfy grading if MCP + tools + retry exist?

**Note:** Spec emphasizes LangGraph and tool calling — likely needs at least one LLM for planning/summary.

---

## 3. Schema Tool

### Q-6: Schema source for MVP?

| Option | Description |
|--------|-------------|
| **A. Live Postgres introspection** | `information_schema` via SQLAlchemy/psycopg |
| **B. TEND / Spider gold JSONL** | Static schema from `data/spider_gold_validation.jsonl` per `db_id` |
| **C. Hybrid** | Live PG when connected; fallback to file |

**Recommendation:** **C** for capstone — demo works offline with gold file; live PG when configured.

---

### Q-7: Schema selection algorithm v1?

| Option | Complexity | Quality |
|--------|------------|---------|
| Keyword overlap (table names in question) | Low | OK for Spider |
| Embedding similarity (planned in ui-tool) | Medium | Better |
| LLM-based table picker (orchestrator sub-call) | Medium | Flexible; extra cost |

**Recommendation:** Keyword + FK expansion for MVP; embedding in Phase 2 enhancement.

---

## 4. Execution Tool

### Q-8: Execution backend?

| Option | Pros | Cons |
|--------|------|------|
| **A. Wrap `database_execution.py` / TEND** | Proven eval path | External repo; Windows path |
| **B. Direct psycopg + pymongo** | Self-contained agent | Duplicate TEND logic |
| **C. Reuse `sql_executor.py` SQLite** | Simple | Not Postgres — wrong for capstone demo |

**Recommendation:** **B** for agent MVP (direct psycopg read-only); keep TEND for eval only.

---

### Q-9: Which database for live demo?

**Question:** User's Postgres instance, TEND catalog DB, or SQLite Spider files?

**Needs user input:** Connection string / `db_id` for capstone demo.

---

## 5. Retry & Error Recovery

### Q-10: What gets sent to Capstone API on retry?

**Question:** Format for FR-5 error feedback prompt?

Draft:

```
Previous SQL: <sql>
Database error: <error>
Schema: <subset>
Task: text2sql
Generate corrected SQL only.
```

**Planning must specify** exact prompt template in `agent/prompts.py`.

---

### Q-11: Retry on validation failure vs execution failure?

**Question:** Retry only on DB error, or also on `SQLValidator` syntax failure before execution?

**Recommendation:** Both — syntax fail before DB; counts toward max 3.

---

## 6. Capabilities & Scope

### Q-12: MVP scope — text2sql only or all three tasks?

**Question:** Implement full pipeline (text2sql → sql2nosql → doc) in agent for capstone?

**Recommendation:** **MVP = text2sql only**; stub intent routing for other tasks in graph; Phase 2 adds sql2nosql path.

---

### Q-13: Explain SQL — in or out?

**Question:** Spec lists `/generate/explanation` — not in API or adapters.

**Recommendation:** **Out of MVP**; document as future adapter or orchestrator-only explanation without fine-tuned model.

---

### Q-14: SQL documentation vs nosql2doc naming?

**Question:** Does capstone require SQL doc generation or Mongo query doc?

**Current API:** Only `nosql2doc` adapter.

**Needs alignment** with supervisor / spec interpretation.

---

## 7. Dependencies & Environment

### Q-15: Separate requirements file for agent?

**Question:** Add `agent/requirements.txt` (langgraph, mcp, httpx, openai) vs extend root `requirements.txt`?

**Recommendation:** `agent/requirements.txt` + document install in agent README — keeps ML env separate.

---

### Q-16: Can `tool/` be restored from another machine?

**Question:** text2sql-ui-tool code exists elsewhere but not in this checkout — restore or rewrite?

**Action:** User to confirm if `tool/` exists on Mac/backup before planning reimplementation effort.

---

## 8. Edge Cases

| ID | Edge case | Planning note |
|----|-----------|---------------|
| E-1 | Cloud Run returns `clarify` message | Force `intent` on request |
| E-2 | Empty schema subset | Agent asks user to clarify |
| E-3 | Zero-row result | NL summary must say "no results" |
| E-4 | Large result sets | Row cap + truncation in summary |
| E-5 | Concurrent tool calls | Sequential for MVP |
| E-6 | Invalid JSON from orchestrator tool args | Validate with Pydantic |
| E-7 | Mongo path without SQL intermediate | Multi-step graph state |

---

## 9. Decisions Required Before Implementation

| Priority | Question ID | Decision maker |
|----------|-------------|----------------|
| P0 | Q-1 | Planning (API adapter) |
| P0 | Q-4 | User + planning (orchestrator LLM) |
| P0 | Q-8, Q-9 | User (DB + execution backend) |
| P0 | Q-12 | Planning (MVP scope) |
| P1 | Q-2, Q-3 | Planning (repo layout) |
| P1 | Q-6, Q-7 | Planning (schema tool) |
| P1 | Q-10, Q-11 | Planning (retry prompts) |
| P2 | Q-13, Q-14 | User / supervisor |
| P2 | Q-16 | User (restore tool/) |

---

## 10. Planning Output Expectations

Each open question should appear in `planning/feature-plans/database-agent-plan.md` as either:

- **Decision** (chosen option + rationale), or  
- **Deferred** (post-MVP with tracking ID)

No implementation until `planning/approvals/database-agent-approval.md` is approved.

**Update (2026-07-26):** Approved and implemented through Stage 10.
