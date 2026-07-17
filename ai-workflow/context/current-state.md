# Current State — CodeGen Studio

> Updated after **text2sql-ui-tool Stages 0–4 complete** (2026-07-16).

## Active Initiative — AI SQL Assistant (Desktop) — 2026-07-16

- **Phase**: Implementation — **Stages 0–4 complete**
- **Spec**: `tool/docs/AI_Text_to_SQL_UI_Specification.md` (v1.1, desktop UI)
- **Plan**: `ai-workflow/planning/feature-plans/text2sql-ui-tool-plan.md`
- **UI**: CustomTkinter desktop app (`python tool/app.py`)
- **Reuse:** `src/text2sql/` for prompts/validation; inference via **hf-deploy FastAPI**

### Implementation stages

| Stage | Work | Status |
|-------|------|--------|
| 0 | Scaffold | ✅ |
| 1 | Core services | ✅ |
| 2 | FastAPI pipeline + adapters | ✅ |
| 3 | Desktop UI + Settings dialog | ✅ |
| 4 | Tests + polish | ✅ |
| 5 | Stub extensibility | ✅ (registry + stub tabs in desktop) |

### Run

```bash
cd /Volumes/Work/CodeGen-Implementations-May_26
pip install -r tool/requirements.txt
python tool/app.py
pytest tool/tests/ -q
```

### Latest artifacts

- Stage logs: `stage-0.md` … `stage-4.md`, `stage-3b-desktop.md`
- Report: `generated-code-reports/stage-4-report.md`

---

## LoRA Fine-Tuning Initiative

- **Phase**: Stage 6 eval integration next

## Validation Status

- text2sql-ui-tool: pytest 26/26 ✅
