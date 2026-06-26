# Implementation Roadmap — TENDv2 (Ollama)

> **Feature:** `tendv2-ollama` · **Date:** 2026-06-24
> **Approval:** `approvals/tendv2-ollama-approval.md` (APPROVED)

---

## Implementation Order

| Order | Stage | Key outputs |
|-------|-------|-------------|
| 1 | S1 — Ollama client | `src/llm/ollama_client.py` (sync + async) |
| 2 | S2 — Codegen + judge | `prompts.py`, `code_generator.py`, `judge.py` |
| 3 | S3 — Sources + paths | `spider_source.py`, `paths.py`, `schema_to_sql.py`, `validator.py` |
| 4 | S4 — Async pipeline + CLI | `build_tend_dataset.py`, `run_tend.py`, `README.md` |
| 5 | S5 — BIRD | `bird_source.py`, `--dataset bird` |
| 6 | S6 — Deps + smoke | `requirements.txt`, `.env.example`, smoke checks |

---

## Testing Checkpoints

### CP-1 — Ollama client (after S1)
- [ ] `OllamaClient().chat("qwen3:4b", [...])` returns content against local Ollama
- [ ] Async client runs N concurrent calls bounded by the semaphore

### CP-2 — Codegen + judge units (after S2)
- [ ] Codegen returns non-empty `nosql_schema`, `nosql_query`, `documentation`
- [ ] Combined-call failure triggers per-field fallback
- [ ] Judge returns boolean `evaluation_result` + non-empty summary

### CP-3 — Pipeline smoke (after S4)
- [ ] `python -m TENDv2.run_tend --dataset spider --split validation --max-samples 5 --concurrency 4`
- [ ] CSV has all required columns; `.summary.json` written
- [ ] Rows in input order; partial file persists if interrupted

### CP-4 — Scale check
- [ ] `--max-samples 100 --concurrency 8` completes; throughput > sequential baseline

### CP-5 — BIRD (after S5)
- [ ] `--dataset bird --split validation --max-samples 5` produces valid CSV

---

## Rollout Strategy

- **Phase A:** small `--max-samples` smoke on Spider validation; verify columns + Ollama connectivity.
- **Phase B:** tune `--concurrency` for the local Ollama host; run a 100-row batch.
- **Phase C:** full Spider train/validation, then enable BIRD.

---

## File Index

| Document | Path |
|----------|------|
| Feature plan | `ai-workflow/planning/feature-plans/tendv2-ollama-plan.md` |
| Task breakdown | `ai-workflow/planning/task-breakdowns/tendv2-ollama-tasks.md` |
| Dependencies | `ai-workflow/planning/dependency-analysis/tendv2-ollama-dependencies.md` |
| Approval | `ai-workflow/planning/approvals/tendv2-ollama-approval.md` |
