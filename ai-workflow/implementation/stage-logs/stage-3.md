# Stage 3 — UI Shell & Panels

**Feature:** text2sql-ui-tool  
**Date:** 2026-07-16

## Implemented tasks

- T3.1 — `ui/shell.py` (header, connection label, tab routing, adapter registry)
- T3.2 — `ui/activity_panel.py`
- T3.3 — `ui/query_panel.py` (Execute / Clear)
- T3.4 — `ui/sql_panel.py`
- T3.5 — `ui/output_panel.py`
- T3.6 — `ui/tabs/text2sql_tab.py` (wired to pipeline)
- T3.7 — Settings page: DB connections CRUD + Test Connection
- T3.8 — Settings page: FastAPI config + Test API
- T3.9 — Settings page: schema selection + execution limits
- T5.1–T5.3 (partial) — SQL-to-NoSQL stub tab, Documentation tab, adapter registry

## Changed files

- `tool/ui/**`, `tool/pages/settings.py`, `tool/app.py`

## Blockers

- None

## Assumptions

- Streamlit multipage: Settings auto-listed in sidebar
- `streamlit run tool/app.py` verified (headless smoke test on port 8510)
