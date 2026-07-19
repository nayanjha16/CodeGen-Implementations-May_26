# Approval — AI SQL Assistant (Streamlit UI)

> **Feature:** `text2sql-ui-tool`  
> **Plan:** `feature-plans/text2sql-ui-tool-plan.md`  
> **Date:** 2026-07-16

---

## Approval Status

| Field | Value |
|-------|-------|
| **Status** | **APPROVED** |
| **Approver** | User (via implementation directive) |
| **Approved date** | 2026-07-16 |

Implementation must **not** begin until status is changed to **APPROVED**.

---

## Approved Scope (proposed)

- **Desktop app** (CustomTkinter) under `tool/` with Text-to-SQL tab (MVP)
- **Settings page** — database connection CRUD, FastAPI endpoint config
- **Test Connection** (PostgreSQL) and **Test API** (FastAPI health check)
- **FastAPI-only inference** — LoRA adapter deployed in hf-deploy, not accessible from tool
- **Prompt-based schema selection** — embedding retrieval of relevant tables before inference
- Single Execute action, structured logs, scrollable view-only results

---

## Rejected / Deferred Items

| Item | Reason |
|------|--------|
| Local model / LoRA loading in tool | LoRA deployed in FastAPI only |
| Direct adapter file access from tool | Not accessible per architecture |
| Result CSV/Excel download | Out of scope per spec v1.1 |
| Separate Generate SQL button | Out of scope per spec v1.1 |
| VS Code extension work | Different product |
| SQL-to-NoSQL full implementation | Deferred to post-MVP |
| Authentication / RBAC | Deferred |

---

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2026-07-16 | FastAPI-only inference; prompt-based schema selection via embeddings | Planning agent |

---

## Sign-off

To approve, update **Status** to `APPROVED`, set approver name and date, then proceed with Stage 0 implementation per `implementation-roadmaps/text2sql-ui-tool-roadmap.md`.
