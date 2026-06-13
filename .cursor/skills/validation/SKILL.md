---
name: validation
description: Validate implementations against requirements and plans; write reports under ai-workflow/validation/.
---

# Validation Skill

Your task is to verify implementation correctness. **All deliverables must be written to `ai-workflow/validation/`**.

## Inputs (Read First)

- `ai-workflow/planning/feature-plans/feature-x-plan.md`
- `ai-workflow/planning/task-breakdowns/feature-x-tasks.md`
- `ai-workflow/research/requirements/requirements-analysis.md`
- `ai-workflow/implementation/stage-logs/stage-N.md`
- `ai-workflow/implementation/generated-code-reports/stage-N-report.md`

## Responsibilities

Validate:
- functional correctness
- architecture alignment
- requirement coverage
- edge cases
- regressions
- integration behavior

## Required Outputs

Replace `N` with stage number when validating a stage.

### Validation Report

**Path:** `ai-workflow/validation/validation-reports/stage-N-validation.md`

**Contains:**
- passed checks
- failed checks
- regressions
- requirement coverage (map to requirements-analysis.md)

### Regression Checks (when tests or behavior comparisons run)

**Path:** `ai-workflow/validation/regression-checks/stage-N-regression.md`

**Contains:**
- test commands run
- pass/fail summary
- new failures vs baseline

### Test Summary

**Path:** `ai-workflow/validation/test-summaries/stage-N-tests.md`

**Contains:**
- tests executed
- coverage notes
- gaps

### Benchmark Results (when performance is in scope)

**Path:** `ai-workflow/validation/benchmark-results/metrics.md` (or `stage-N-metrics.md` for staged runs)

**Contains:**
- performance metrics
- latency
- memory usage
- benchmark comparisons

## Context Updates (End of Validation)

Update:
- `ai-workflow/context/current-state.md` — validation outcome, blockers if failed
- `ai-workflow/context/workflow-status.md` — link validation report; next action (fix, next stage, or optimization)

## Rules

- Be critical
- Detect hidden issues
- Verify assumptions
- Cross-check implementation against plan and requirements files
- Link failed checks to specific files and requirement items
- Create parent directories if missing
