# Workflow Status

> Updated: 2026-07-26

## Active feature: `database-agent`

| Field | Value |
|-------|-------|
| **Phase** | Implementation — Stages 1–8 complete |
| **Next phase** | Stage 9 — CLI demo polish |
| **Spec** | `agent/doc/agent.md` |
| **Agent plan (status)** | [status.md](../planning/feature-plans/agent/status.md) |

## Research deliverables

| Artifact | Path | Status |
|----------|------|--------|
| Executive summary | [project-summary.md](../research/summaries/project-summary.md) | ✅ |
| Architecture map | [architecture-map.md](../research/architecture/architecture-map.md) | ✅ |
| Requirements analysis | [requirements-analysis.md](../research/requirements/requirements-analysis.md) | ✅ |
| Risk analysis | [risk-analysis.md](../research/risks/risk-analysis.md) | ✅ |
| Open questions | [questions.md](../research/open-questions/questions.md) | ✅ |

## Context sync

| File | Status |
|------|--------|
| [context/project-summary.md](project-summary.md) | ✅ Synced |
| [context/architecture-map.md](architecture-map.md) | ✅ Synced |
| [context/current-state.md](current-state.md) | ✅ Updated |

## Planning inputs (next)

Planning skill must read:

1. `research/summaries/project-summary.md`
2. `research/architecture/architecture-map.md`
3. `research/requirements/requirements-analysis.md`
4. `research/risks/risk-analysis.md`
5. `research/open-questions/questions.md`

## Planning outputs

| Artifact | Path | Status |
|----------|------|--------|
| Agent feature plan | [planning/feature-plans/agent/](../planning/feature-plans/agent/) | ✅ (status, implementation-plan, decisions, …) |
| Task breakdown | `planning/task-breakdowns/database-agent-tasks.md` | — |
| Roadmap | `planning/implementation-roadmaps/database-agent-roadmap.md` | — |
| Dependencies | `planning/dependency-analysis/database-agent-dependencies.md` | — |
| Approval | `planning/approvals/database-agent-approval.md` | — |

## Decisions needed before planning completes

- **Q-4:** Orchestrator LLM (OpenAI vs Ollama vs other)
- **Q-9:** Live demo database connection
- **Q-12:** Confirm MVP = text2sql-only path
- **Q-1:** API adapter-only vs `/generate/*` shim

## Prior feature: `text2sql-ui-tool`

| Field | Value |
|-------|-------|
| **Phase** | Implementation complete (per ai-workflow logs) |
| **Note** | `tool/` not on disk in current checkout |

## Infrastructure ready for agent

- Cloud Run URL: `https://codegen-api-161349047936.asia-south2.run.app`
- OpenAI base for agent tools: `<url>/v1`
- Model IDs: `codegen-text2sql`, `codegen-sql2nosql`, `codegen-nosql2doc`, `codegen-multi-adapter`

---

**Next action:** Run Planning skill — `"Start Planning for database-agent"`
