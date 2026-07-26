# Stage 10 — Web UI + Query Quality

**Date:** 2026-07-26  
**Status:** Complete  
**Plan:** Extension of agent capstone (post §12 demo polish)

## Implemented

- [x] `agent/web/app.py` — FastAPI: `GET /`, `GET /api/health`, `GET /api/examples`, `POST /api/query`
- [x] `agent/web/templates/index.html`, `static/css/style.css`, `static/js/app.js`
- [x] Async query handling (`asyncio.to_thread`) + 3-minute timeout + progress UI
- [x] `agent/lib/text2sql_hints.py` — DDL hints, `format_listing_summary()` deterministic summaries
- [x] `agent/lib/sql_repair.py` — auto-repair join SELECTs (e.g. album + artist columns)
- [x] `strip_invented_where_filters` in `sql_validation.py` — remove hallucinated WHERE clauses
- [x] DDL comment hints in `database/postgres.py` — reduce PascalCase filter invention
- [x] `agent/tests/test_web_ui.py`, `test_sql_repair.py`, `test_text2sql_hints.py`
- [x] `agent/.env.example` — `AGENT_WEB_HOST`, `AGENT_WEB_PORT`

## Run

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m agent.web
# → http://127.0.0.1:8080
```

## Bugfixes addressed

| Issue | Fix |
|-------|-----|
| Web UI "Thinking…" hang | Async runner + timeout + progress messages |
| Invented `WHERE Name = 'PascalCase'` filters | Hint stripping + DDL comments |
| Ollama hallucinated artist names in summaries | Deterministic `format_listing_summary` |
| Incomplete SELECT for D1 join | `sql_repair.py` column expansion |

## Validation

- `python -m pytest agent/tests/ -q` — **88 passed**

## Blockers

None.

## Known limitations

- End-to-end latency 30–90s (CodeGen + Ollama + Postgres)
- D2 (3-table joins) still unreliable for live demo
