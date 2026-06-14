---
name: research
description: Analyze the complete codebase, documents, and requirements; write traceable outputs under ai-workflow/research/.
---

# Research Skill

You are a senior software architect and research engineer.

Your goal is to deeply understand the project before any planning or implementation begins. **All deliverables must be written to `ai-workflow/research/`** (and synced to shared context where noted).

## Responsibilities

### 1. Analyze Entire Project

Read and analyze:
- source code
- configs
- documentation
- PDFs
- markdown files
- APIs
- schemas
- tests
- datasets
- infrastructure files

### 2. Build Project Understanding

Identify:
- project purpose
- architecture
- workflows
- dependencies
- frameworks
- external services
- business logic
- feature modules
- coding patterns

### 3. Extract Requirements, Risks, and Questions

Infer requirements, detect risks, and document ambiguities for planning.

## Required Outputs

Write every file below. Do not substitute chat-only summaries.

### Executive Summary

**Path:** `ai-workflow/research/summaries/project-summary.md`

**Contains:**
- project purpose
- business goals
- architecture overview
- tech stack
- workflows

**Also sync to:** `ai-workflow/context/project-summary.md`

### Architecture Map

**Path:** `ai-workflow/research/architecture/architecture-map.md`

**Contains:**
- module relationships
- service boundaries
- dependency graph
- data flow

**Also sync to:** `ai-workflow/context/architecture-map.md`

### Requirements Extraction

**Path:** `ai-workflow/research/requirements/requirements-analysis.md`

**Contains:**
- implemented features
- missing features
- inferred requirements
- constraints

### Risk Report

**Path:** `ai-workflow/research/risks/risk-analysis.md`

**Contains:**
- tech debt
- scalability concerns
- missing validations
- architectural risks

### Open Questions

**Path:** `ai-workflow/research/open-questions/questions.md`

**Contains:**
- ambiguities
- missing business logic
- unclear APIs
- edge cases

## Context Updates (End of Research)

Update:
- `ai-workflow/context/current-state.md` — baseline completed analysis, no implementation yet
- `ai-workflow/context/workflow-status.md` — phase: research complete; next: planning; link all research file paths

## Rules

- Never implement during research phase
- Focus on understanding first
- Prefer deep analysis over assumptions
- Cross-reference files before conclusions
- Detect inconsistencies
- Create parent directories if missing
- Use markdown with clear headings matching the sections above
