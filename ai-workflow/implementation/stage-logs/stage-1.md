# Stage 1 — Core Services

**Feature:** text2sql-ui-tool  
**Date:** 2026-07-16

## Implemented tasks

- T1.1 — `ActivityEvent` + `ActivityLogger`
- T1.2 — `SettingsStore` (connections, FastAPI, schema selection, execution limits)
- T1.3 — `connection_tester.test_database()` / `test_fastapi()`
- T1.4 — `database.get_active_engine()`
- T1.5 — `schema_loader.load_all_tables()` → `TableSchema`
- T1.6 — `schema_selector.select_tables_for_prompt()` (sentence-transformers)
- T1.7 — `SafetyValidator` (SELECT/WITH only; fixed DML token detection)
- T1.8 — `executor.execute_readonly_sql()` → DataFrame

## Changed files

- `tool/core/*.py`

## Blockers

- None

## Assumptions

- First run seeds settings from `DATABASE_URL` if set
- Embedding model download on first schema selection (cached by sentence-transformers)
