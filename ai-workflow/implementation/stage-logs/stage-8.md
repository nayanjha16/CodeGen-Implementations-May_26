# Stage 8 — Integration Tests

**Date:** 2026-07-26  
**Status:** Complete

## Implemented

- `agent/tests/conftest.py` — Chinook env fixture + Docker availability skip
- `agent/tests/test_integration_stage8.py` — 10 live integration tests
- `agent/pytest.ini` — `integration` / `docker` markers
- `agent/scripts/run_integration_tests.py` — convenience runner
- **Bugfix:** `agent/retry.py` — first SQL failure now triggers retry (was blocked by `can_retry()` guard)

## Tests cover

- Chinook Postgres (11 tables, 59 customers)
- Chinook Mongo (`countDocuments`)
- Schema tool selects `Customer` only
- MCP `extract_schema` / `execute_query` parity with direct tools
- Runner `validate_sql` against live DB
- Runner retry after execution error (mocked CodeGen + live Postgres)

## Validation

- `python -m pytest agent/tests/ -q` — **65 passed**

## Blockers

None when TEND Docker is running; tests skip gracefully otherwise.
