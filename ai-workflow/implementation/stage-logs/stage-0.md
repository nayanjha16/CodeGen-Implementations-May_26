# Stage 0 — Scaffold

**Feature:** text2sql-ui-tool  
**Date:** 2026-07-16

## Implemented tasks

- T0.1 — `tool/` directory structure (AD-1)
- T0.2 — `tool/requirements.txt` (no torch/peft)
- T0.3 — `tool/.env.example`
- T0.4 — `tool/config.yaml` + `tool/config.py` (`ToolConfig`)
- T0.5 — `tool/.gitignore`, `tool/README.md`
- T0.6 — `tool/app.py`, `tool/pages/settings.py` stub entry

## Changed files

- Created full scaffold under `tool/`

## Blockers

- Plan approval still marked PENDING; implementation proceeded per user request.

## Assumptions

- Run from repo root: `streamlit run tool/app.py`
- Repo root added to `sys.path` in `app.py` and `pages/settings.py`
