# Dependency Analysis — TENDv2 (Ollama)

> **Feature:** `tendv2-ollama` · **Date:** 2026-06-24

## External Services

| Dependency | Notes |
|------------|-------|
| Ollama daemon | Local at `OLLAMA_BASE_URL` (default `http://localhost:11434`); `/api/chat` with `stream:false` |
| Model `qwen2.5-coder:3b` | Must be pulled (`ollama pull qwen2.5-coder:3b`) — code generator |
| Model `qwen3:4b` | Must be pulled (`ollama pull qwen3:4b`) — judge (reasoning model; `think:false`) |

## New Python Packages

| Package | Reason |
|---------|--------|
| `httpx>=0.27` | Async + sync HTTP for the Ollama client |

> `requests` (already present) could power the sync path, but `httpx` provides a
> unified sync/async API and is preferred for the async pipeline.

## Internal Module Dependencies

```
src/llm/ollama_client.py        (no project deps; httpx + env)
        │
        ├── TENDv2/code_generator.py ──┐
        ├── TENDv2/judge.py ───────────┤
        │                              ▼
TENDv2/schema_to_sql.py ──► TENDv2/build_tend_dataset.py ──► TENDv2/run_tend.py
TENDv2/spider_source.py ──►        ▲
TENDv2/bird_source.py ────►        │
TENDv2/validator.py ──────►        │
TENDv2/paths.py ──────────►────────┘
```

## Reused Existing Code

| Reused | From | Purpose |
|--------|------|---------|
| `generate_sql_schema` | `TENDv1/schema_to_sql.py` | SQL DDL from tables.json |
| structural checks | `TENDv1/validator.py` | schema/query shape gates |
| `SpiderSource` pattern | `TENDv1/spider_source.py` | read Spider splits |
| `BirdLoader` | `src/datasets/bird_loader.py` | BIRD splits + schema |
| path helpers | `src/utils/paths.py` | data dir resolution |

## Ordering Constraints

1. `src/llm/ollama_client.py` must exist before codegen/judge.
2. Codegen + judge before the pipeline.
3. Spider source + schema_to_sql + paths before the pipeline.
4. Pipeline before CLI.
5. BIRD (S5) only after Spider end-to-end works.

## Risks

| Risk | Mitigation |
|------|------------|
| Ollama not running / model missing | Clear connection error + preflight check message in client |
| Combined codegen JSON malformed | Per-field fallback calls (AD-3) |
| `qwen3:4b` emits `<think>` noise | `think:false` + defensive strip |
| Concurrency overwhelms host | Bounded semaphore; configurable `--concurrency` |
| Large run memory/interrupt loss | Incremental ordered CSV writes (AD-6) |
