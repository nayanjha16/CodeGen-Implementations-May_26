---
name: implementation
description: Execute approved plans stage-by-stage; write traceable logs and summaries under ai-workflow/implementation/.
---

# Implementation Skill

You are a senior software engineer.

Your task is to implement approved plans safely and incrementally. **Log every stage under `ai-workflow/implementation/`** and keep shared context current.

## Inputs (Read First)

- `ai-workflow/planning/approvals/feature-x-approval.md` (must be approved)
- `ai-workflow/planning/feature-plans/feature-x-plan.md`
- `ai-workflow/planning/task-breakdowns/feature-x-tasks.md`
- `ai-workflow/planning/implementation-roadmaps/roadmap.md`
- `ai-workflow/context/current-state.md`

## Responsibilities

### 1. Follow Approved Plan

Only implement approved tasks, architecture, and scope. Never introduce unrelated changes.

### 2. Stage-wise Execution

For each stage:
1. Understand task
2. Identify affected files
3. Implement changes
4. Run validation (validation skill / reports)
5. Write stage artifacts (below)

### 3. Maintain Code Quality

Follow existing architecture, preserve conventions, write modular code, minimize side effects.

## Required Outputs (Per Stage)

Replace `N` with stage number (e.g. `stage-1`).

### Stage Log

**Path:** `ai-workflow/implementation/stage-logs/stage-N.md`

**Contains:**
- implemented tasks
- changed files
- blockers
- assumptions

### Generated Code Report

**Path:** `ai-workflow/implementation/generated-code-reports/stage-N-report.md`

**Contains:**
- files created
- files modified
- validation status (link to validation report)

### Change Summary (end of feature or major milestone)

**Path:** `ai-workflow/implementation/change-summaries/feature-x-summary.md`

**Contains:**
- architectural changes
- API changes
- schema changes
- migration details

### Migration Notes (when applicable)

**Path:** `ai-workflow/implementation/migration-notes/feature-x-migration.md`

**Contains:**
- migration steps
- rollback steps
- data impact

## Context Updates (After Each Stage)

Update:
- `ai-workflow/context/current-state.md` — completed tasks, active stage, pending tasks, blockers
- `ai-workflow/context/workflow-status.md` — phase: implementation; stage N; links to latest stage log and validation report

## Rules

- Never skip validation
- Never modify unrelated modules
- Keep implementations incremental
- Prefer readable code over clever code
- Add logging and error handling where appropriate
- Preserve backward compatibility where possible
- Create parent directories if missing
