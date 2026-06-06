---
name: orchestration
description: Coordinate research, planning, implementation, validation, and optimization workflows with traceable outputs under ai-workflow/.
---

# Orchestration Skill

You coordinate the full AI development workflow. Every phase must produce artifacts under `ai-workflow/` so work is traceable, reviewable, and reusable.

## Workspace Standard

All phase outputs live under the project root:

```
project-root/
├── .cursor/
│   ├── skills/
│   └── rules/
├── ai-workflow/
│   ├── research/
│   ├── planning/
│   ├── implementation/
│   ├── validation/
│   ├── optimization/
│   └── context/
└── src/
```

Never scatter phase deliverables in chat-only form. Write files to the paths defined in each phase skill.

## Shared Context (Always Maintain)

After every phase, update:

| File | Purpose |
|------|---------|
| `ai-workflow/context/workflow-status.md` | Current phase, approvals, next actions, recent decisions |
| `ai-workflow/context/current-state.md` | Completed work, active stage, pending tasks, blockers |
| `ai-workflow/context/project-summary.md` | Stable high-level project overview (sync from research) |
| `ai-workflow/context/architecture-map.md` | Stable architecture reference (sync from research) |

## Workflow

1. **Research** — Run research skill; populate `ai-workflow/research/` and seed `context/`
2. **Planning** — Run planning skill; populate `ai-workflow/planning/`; resolve open questions
3. **Approval gate** — Document in `planning/approvals/`; update `workflow-status.md`
4. **Implementation** — Execute stage-by-stage; log to `ai-workflow/implementation/`
5. **Validation** — After each stage (and at milestones); write to `ai-workflow/validation/`
6. **Optimization** — Optional review; write to `ai-workflow/optimization/`

## Phase Handoff Rules

- **Research → Planning**: Planning must read `research/summaries/project-summary.md`, `research/architecture/architecture-map.md`, `research/requirements/requirements-analysis.md`, and `research/open-questions/questions.md`
- **Planning → Implementation**: Implementation must not start until `planning/approvals/feature-x-approval.md` exists with approved scope
- **Implementation → Validation**: Each stage log must reference its validation report path
- **Any phase → Context**: Always update `current-state.md` and `workflow-status.md` before ending the phase

## Rules

- Never skip phases
- Require explicit approval before implementation (record in `planning/approvals/`)
- Keep context continuity via `ai-workflow/context/`
- Generate phase artifacts on disk, not only in conversation
- Track progress across phases using `workflow-status.md`
- Use consistent naming: `feature-x` for feature-scoped files; `stage-N` for stage-scoped files

## End-of-Phase Checklist

- [ ] All required files for the phase exist under `ai-workflow/<phase>/`
- [ ] `ai-workflow/context/current-state.md` updated
- [ ] `ai-workflow/context/workflow-status.md` updated
- [ ] Next phase inputs are linked (file paths in workflow-status)
