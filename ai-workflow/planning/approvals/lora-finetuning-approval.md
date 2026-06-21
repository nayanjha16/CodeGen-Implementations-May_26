# Approval Tracking — LoRA Fine-Tuning

> **Feature:** `lora-finetuning`  
> **Date:** 2026-06-21

---

## Approval Status

| Field | Value |
|-------|-------|
| **Status** | **APPROVED** |
| **Approved by** | User |
| **Approved date** | 2026-06-21 |
| **Plan author** | Planning agent (2026-06-21) |
| **Implementation blocked** | No — Stage 0 skipped by user (data prep deferred) |

---

## Approved Scope (proposed)

Pending user sign-off on the following:

- [x] Add `src/training/` package skeleton (Stage 1 — in progress)
- [ ] SFT dataset builder, LoRA trainer, and MLflow logging (Stages 2–3)
- [x] Add `scripts/inspect_lora_modules.py` pre-flight script (Stage 1)
- [ ] Add `scripts/train_lora.py` CLI (Stage 3)
- [x] Extend `configs/default.yaml` with `training:` and `lora:` blocks (Stage 1)
- [ ] Extend `src/models/model_loader.py` for PEFT adapter loading (Stage 4)
- [ ] Extend eval script with `--adapter` / task-aware loading (Stage 6)
- [ ] Add tests under `tests/training/` (Stages 2–4)
- [ ] Regenerate full TEND dataset (Stage 0 — **deferred by user**)
- [ ] Train three task-specific adapters on `Salesforce/codegen-350M-multi` (Stage 5)
- [ ] Evaluate via existing `BenchmarkRunner` + `qwen_correct_rate` primary metric (Stage 6)

---

## Rejected / Out of Scope (confirmed)

- Full fine-tuning (all weights)
- QLoRA / `bitsandbytes`
- T5 / seq2seq training path
- Multi-task or shared LoRA adapter
- BIRD dataset in v1
- Merging adapters into base model
- New metrics or UI

---

## Locked Decisions (from research — included in plan)

| Decision | Choice |
|----------|--------|
| Base model | `Salesforce/codegen-350M-multi` |
| Adapter strategy | One adapter per task |
| LoRA type | Plain LoRA (fp32) |
| Training filter | `overall_correct == True` |
| Sequence budget | max 2048, target reserved 256, prompt ≤ 1792 |
| Adapter storage | **All adapters under `models/checkpoints/<task>/`** (via `get_models_checkpoints_dir()`) |
| Primary metric | `qwen_correct_rate` + structural gates |
| Dependencies | `peft` + `trl` (already in requirements.txt) |

---

## Planning Assumptions Requiring Confirmation

| ID | Assumption | Default if no response |
|----|------------|------------------------|
| Q7 | Doc supervision = Qwen `documentation` column | Use Qwen distillation |
| Q8 | Splits = Spider native train / dev | Use native splits |
| Q19 | Success = ≥ 0.10 absolute lift in `qwen_correct_rate` or ≥ 0.50 absolute | As stated |
| Q23 | Adapters = local artifacts, not git-committed | As stated |
| P-A | Use `trl.SFTTrainer` (not raw HF Trainer) | As stated |
| P-B | Phase A smoke (100 rows) before full corpus | Recommended, not mandatory |

---

## Revision History

| Date | Version | Change |
|------|---------|--------|
| 2026-06-21 | 1.0 | Initial plan created from research deliverables |
| 2026-06-21 | 1.1 | Locked save location: all fine-tuned adapters under `models/checkpoints/<task>/` |

---

## How to Approve

Reply with confirmation to proceed with implementation, optionally noting:

1. Any rejected items from the proposed scope
2. Changes to planning assumptions (Q7, Q8, Q19, Phase A vs full corpus)
3. Whether to start with Phase A (100-row smoke) or full corpus immediately

On approval, update this file:

```
Status: APPROVED
Approved by: <user>
Approved date: <date>
Notes: <any scope adjustments>
```

Then begin **Stage 1 — Foundation** per `implementation-roadmaps/roadmap.md`.

---

## Related Plans

- Feature plan: `ai-workflow/planning/feature-plans/lora-finetuning-plan.md`
- Tasks: `ai-workflow/planning/task-breakdowns/lora-finetuning-tasks.md`
- Roadmap: `ai-workflow/planning/implementation-roadmaps/roadmap.md`
- Dependencies: `ai-workflow/planning/dependency-analysis/lora-finetuning-dependencies.md`
