# Current State — CodeGen Studio

> Updated after **Stage 5 implementation** (2026-06-25).

## Active Initiative — TENDv2 (Ollama) — 2026-06-24

- **Phase**: Chunked/resumable pipeline **implemented** (2026-06-24).
- Plan: `feature-plans/tendv2-chunked-pipeline-plan.md`

---

## LoRA Fine-Tuning Initiative

- **Date**: 2026-06-25
- **Phase**: Implementation — **Stage 5 complete**, Stage 6 next
- **Approval**: APPROVED (`lora-finetuning-approval.md`)
- **Base model**: `Salesforce/codegen-350M-multi`

### Stage 1–4 (done)

Foundation, dataset builder, trainer, adapter loading — all complete.

### Stage 5 Deliverables (done)

- `scripts/train_all_lora.py` — batch train + optional baseline + summary JSON
- `scripts/verify_lora_adapters.py` — verify adapter artifacts per run
- `src/training/adapter_verify.py` — verification helpers
- **Trained adapters:** `models/checkpoints/v1/` (text2sql, sql2nosql, nosql2doc)
- Verify: `python scripts/verify_lora_adapters.py --version v1` ✅

### Pending (next stages)

| Stage | Work | Status |
|-------|------|--------|
| 6 | Eval integration + LoRA vs baseline comparison | ⬜ Next |

### Training data (locked)

| Split | Source | Rows |
|-------|--------|------|
| Train | spider train + bird train (HF TEND) | 10,697 |
| Eval | spider test + bird test (HF TEND) | 1,625 |

### Note on full corpus

Run `v1` used a **50-row subset** per task to validate the full pipeline. For full-corpus training:

```bash
python scripts/train_all_lora.py --version 2506-full
```

Expect long wall-clock on MPS (use CUDA for faster runs).

## Validation Status

- Stages 1–4: ✅
- Stage 5 adapter artifacts (`v1`): ✅
- Stage 6 eval comparison: ⬜ Not started

## Environment

- Python 3.11+ (`conda` env `ai`)
- Adapter layout: `models/checkpoints/<run>/<task>/`
