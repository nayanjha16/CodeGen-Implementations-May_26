# Stage 4 — Polish & Tests

**Feature:** text2sql-ui-tool  
**Date:** 2026-07-16

## Implemented tasks

- T4.1 — Inline status bar + validation label for errors (desktop)
- T4.2 — Ctrl/Cmd+Enter documented in UI and README
- T4.3–T4.8 — Full pytest suite under `tool/tests/` (26 tests)
- T4.9 — Manual test checklist in `tool/README.md`

## Tests

```bash
pytest tool/tests/ -q  # 26 passed
```

## Other fixes

- Renamed `test_database` / `test_fastapi` → `run_database_test` / `run_fastapi_test` (pytest collision)
- Adapter registry: `tool/desktop/registry.py`
- Spec updated: Streamlit → CustomTkinter desktop

## Blockers

- None
