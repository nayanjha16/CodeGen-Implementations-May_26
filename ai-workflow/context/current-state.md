# Current State — CodeGen Studio

> Updated after **Stage 4 implementation** (2026-06-25).

## Active Initiative — TENDv2 (Ollama) — 2026-06-24

- **Phase**: Chunked/resumable pipeline **implemented** (2026-06-24).
- Plan: `feature-plans/tendv2-chunked-pipeline-plan.md`

---

## LoRA Fine-Tuning Initiative

- **Date**: 2026-06-25
- **Phase**: Implementation — **Stage 4 complete**, Stage 5 next
- **Approval**: APPROVED (`lora-finetuning-approval.md`)
- **Base model**: `Salesforce/codegen-350M-multi`

### Stage 1 Deliverables (done)

- Config, training package skeleton, `inspect_lora_modules.py`

### Stage 2 Deliverables (done)

- SFT dataset builder (HF spider + bird train, 10,697 rows)
- Prompt parity tests green

### Stage 3 Deliverables (done)

- LoRA trainer, `train_lora.py` CLI, overfit smoke test green

### Stage 4 Deliverables (done)

- `is_adapter_dir()`, `resolve_adapter_path()` in `model_loader.py`
- `CodeGenModel.load()` wraps base + PEFT adapter
- `load_model(adapter=..., adapter_path=..., task=...)` + `MODEL_ADAPTER` env
- `tests/training/test_adapter_load.py` — load + generate for all three tasks

### Pending (next stages)

| Stage | Work | Status |
|-------|------|--------|
| 5 | Train three adapters (full runs) | ⬜ Next |
| 6 | Eval integration + comparison | ⬜ |

### Training data (locked)

| Split | Source | Rows |
|-------|--------|------|
| Train | spider train + bird train (HF TEND) | 10,697 |
| Eval | spider test + bird test (HF TEND) | 1,625 |

## Validation Status

- Stage 1 pre-flight: ✅
- Stage 2 prompt parity + dataset builder: ✅
- Stage 3 overfit smoke + adapter output: ✅
- Stage 4 adapter load + generation: ✅
- No full training run yet

## Environment

- Python 3.11+ (`conda` env `ai`)
- TRL 1.6.0, PEFT adapter loading via `PeftModel.from_pretrained`
