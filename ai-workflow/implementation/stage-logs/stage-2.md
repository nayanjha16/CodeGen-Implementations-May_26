# Stage 2 — FastAPI Inference & Pipeline

**Feature:** text2sql-ui-tool  
**Date:** 2026-07-16

## Implemented tasks

- T2.1 — `InferenceClient` protocol
- T2.2 — `FastApiInferenceClient` (POST `/v1/chat/completions`)
- T2.3 — `sql_extractor.py` (SQLGenerator patterns, no model load)
- T2.4 — `QueryAdapter` + `ExecuteResult`
- T2.5 — `Text2SqlAdapter`
- T2.6 — `Text2SqlPipeline` with structured log events
- T2.7 — `Sql2NoSqlAdapter` stub

## Changed files

- `tool/core/inference/`, `tool/core/sql_extractor.py`
- `tool/adapters/`, `tool/pipeline/text2sql_pipeline.py`

## Blockers

- None (E2E requires running hf-deploy API)

## Assumptions

- Reuses `src.text2sql.prompt_builder.PromptBuilder` and `SQLValidator` for syntax
