# Stage 3b — Desktop UI (Streamlit → CustomTkinter)

**Feature:** text2sql-ui-tool  
**Date:** 2026-07-16

## Change

Replaced Streamlit web UI with a **native desktop app** (CustomTkinter) per user requirement.

## Implemented

- `tool/desktop/main_window.py` — main window, tabs, Execute/Clear, Ctrl/Cmd+Enter
- `tool/desktop/settings_window.py` — DB connections, FastAPI, schema selection
- `tool/desktop/widgets/` — activity log, results table (ttk.Treeview)
- `tool/app.py` — launches desktop via `python tool/app.py`

## Removed

- Streamlit UI (`tool/ui/*`, `tool/pages/settings.py`)
- `streamlit` from `tool/requirements.txt`

## Unchanged

- `tool/core/`, `tool/pipeline/`, `tool/adapters/` — same backend pipeline
