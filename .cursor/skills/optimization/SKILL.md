---
name: optimization
description: Improve performance and maintainability; write analysis and suggestions under ai-workflow/optimization/.
---

# Optimization Skill

Focus on improving performance, scalability, readability, maintainability, and developer productivity. **All deliverables must be written to `ai-workflow/optimization/`**.

## Inputs (Read First)

- `ai-workflow/validation/benchmark-results/` (if present)
- `ai-workflow/research/risks/risk-analysis.md`
- `ai-workflow/context/architecture-map.md`
- `ai-workflow/implementation/change-summaries/`
- Current codebase and profiling data

## Analyze

- bottlenecks
- duplicated logic
- memory usage
- slow operations
- architectural inefficiencies

## Required Outputs

### Profiling Notes (when profiling was run)

**Path:** `ai-workflow/optimization/profiling/profile-report.md`

**Contains:**
- tools used
- hotspots
- raw observations

### Bottleneck Analysis

**Path:** `ai-workflow/optimization/bottleneck-analysis/report.md`

**Contains:**
- slow paths
- memory issues
- scaling concerns

### Refactor Suggestions

**Path:** `ai-workflow/optimization/refactor-suggestions/refactor-plan.md`

**Contains:**
- cleanup recommendations
- modularization ideas
- maintainability improvements

### Performance Report (summary)

**Path:** `ai-workflow/optimization/performance-reports/summary.md`

**Contains:**
- before/after expectations
- prioritized recommendations
- risk of each change

## Context Updates (End of Optimization)

Update:
- `ai-workflow/context/current-state.md` — optimization findings, optional follow-up tasks
- `ai-workflow/context/workflow-status.md` — phase: optimization review complete; recommended next actions

## Rules

- Preserve functionality
- Avoid premature optimization
- Prioritize maintainability
- Tie recommendations to evidence (profiling, validation metrics, code references)
- Create parent directories if missing
