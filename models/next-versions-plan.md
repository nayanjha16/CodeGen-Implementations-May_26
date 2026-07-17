# Next Versions Plan (v4+)

Prioritized experiments for improving beyond LoRA **v3**, derived from the experiment priority list (rank ↑, MLP targets, LR, data quality, batch, regularization).

Baseline for comparisons: **v3** settings in [`version-tracker.md`](./version-tracker.md).

---

## Current v3 baseline (do not regress casually)

| Knob | v3 value |
|------|----------|
| LoRA rank `r` | 16 |
| `lora_alpha` | 32 |
| Target modules | `qkv_proj`, `out_proj` |
| Learning rate | `2e-4` |
| Weight decay | `0.01` (already set) |
| Dropout | `0.05` |
| Effective batch | 32 |
| Epochs | 5 |
| Dataset | Full TEND spider+bird (~8040 train) |

**Housekeeping before new runs:** restore/complete `v3/text2sql/run_metadata.json` (or re-verify adapters) so future comparisons have clean artifacts.

---

## Priority ranking (from experiment list)

| Priority | Change | Expected impact | Suggested version |
|----------|--------|-----------------|-------------------|
| ★★★★★ | Increase LoRA rank to **32** | High | **v4** (paired with modules) |
| ★★★★★ | Include **`fc_in`** and **`fc_out`** | High | **v4** |
| ★★★★ | Reduce LR to **1e-4** | Medium–High | **v5** (or v4b ablate) |
| ★★★★ | Improve dataset quality | High | **v6** / parallel data work |
| ★★★ | Increase effective batch size | Medium | **v5** or v7 |
| ★★★ | Add weight decay **0.01** | Medium | *Already in v1–v3 — skip as a change* |
| ★★ | Increase dropout to **0.1** | Low–Medium | **v7** / late ablate |
| ★ | Train for more than **5** epochs | Low | Only if loss still falling; low ROI |

---

## Recommended version roadmap

### v4 — Capacity unlock (highest ROI)

**Goal:** Give adapters more expressive power on the same full TEND data.

| Parameter | v3 → v4 |
|-----------|---------|
| `lora.r` | 16 → **32** |
| `lora.lora_alpha` | Keep **32**, or raise to **64** to preserve α/r ≈ 2 (recommended) |
| `lora.target_modules` | `qkv_proj`, `out_proj` → add **`fc_in`**, **`fc_out`** |
| Learning rate | Keep `2e-4` first (one change-set at a time) |
| Dataset / epochs / batch | Same as v3 |

**Why:** Attention-only LoRA may underfit CodeGen MLP layers that move representations into/out of the FFN. Rank 32 increases adapter capacity; MLP targets usually matter most for generation quality.

**Config sketch** (`configs/default.yaml` or CLI overrides):

```yaml
lora:
  r: 32
  lora_alpha: 64
  lora_dropout: 0.05
  target_modules:
    - qkv_proj
    - out_proj
    - fc_in
    - fc_out
```

**Success criteria (Spider gold, 50):** beat v3 on text2sql exec (≥54%), sql2nosql exec (≥74%), doc judge (≥6.45). Also watch eval_loss vs train_loss for overfitting.

**Risks:** Larger adapters (~2–4× params); slightly slower train/infer. Confirm `fc_in`/`fc_out` names with `scripts/inspect_lora_modules.py` (CodeGen naming).

**Optional ablations (same data):**
- **v4a:** rank 32 only, same modules as v3  
- **v4b:** add `fc_in`/`fc_out` only, rank 16  

Prefer one combined **v4** if compute is limited; use ablations if results are mixed.

---

### v5 — Stabilization (after v4)

**Goal:** If v4 overfits or learning curves are noisy, quiet training.

| Parameter | Change |
|-----------|--------|
| `training.learning_rate` | `2e-4` → **`1e-4`** |
| Effective batch | Optional: 32 → **64** (e.g. `gradient_accumulation_steps: 8`) |
| Everything else | Carry forward winning v4 LoRA layout |

**Why:** Lower LR with higher capacity is a common PEFT pattern. Larger effective batch can smooth gradients on ~8k rows.

**Success criteria:** Same or better gold metrics as v4 with flatter eval_loss after mid epochs; less mid-run loss spike.

**Skip if:** v4 already improves metrics with healthy train/eval gap — then jump to data quality (**v6**).

---

### v6 — Dataset quality (high impact, parallel track)

**Goal:** Raise ceiling beyond hyperparameter tweaks.

Workstreams (can run while v4 trains):

1. Filter/repair silver TEND rows with bad SQL↔NoSQL↔doc alignment.
2. Revisit the 42 sql2nosql `sequence_too_long` drops (truncate strategy / max_length / shorter prompts).
3. Prefer gold-validated or execution-checked subsets for text2sql / sql2nosql.
4. Deduplicate near-identical questions; balance Spider vs BIRD difficulty.

**Train:** Same LoRA as best of v4/v5; only data changes → label run **v6**.

**Success criteria:** Gains concentrated on hard queries (low structural similarity failures in `*_details.csv`), not just easy exact match.

---

### v7 — Regularization polish (lower priority)

Only after capacity + LR/data are settled:

| Parameter | Change | When to try |
|-----------|--------|-------------|
| `lora_dropout` | 0.05 → **0.1** | Train loss ≪ eval loss on v4/v5 |
| Epochs | 5 → **6–8** | Eval still improving at epoch 5 |
| Weight decay | Already **0.01** | No change unless sweeping `0` / `0.05` |

**Success criteria:** Better generalization on gold validation without large train-loss rise; extra epochs only if epoch-5 eval_loss is still trending down.

---

## Suggested experiment order

```text
1. Confirm CodeGen module names (fc_in / fc_out)
2. v4  — rank 32 + MLP modules on full TEND
3. Eval v4 on spider_gold_validation (compare to v3)
4. If unstable / overfit → v5 (lr 1e-4, maybe batch 64)
   Else → start v6 data work with v4 adapters as baseline
5. v7 only if still under-regularized or under-trained
```

One primary change (or one tight change-set) per version so gains are attributable.

---

## Tracking checklist per new version

After each run under `models/checkpoints/vN/`:

- [ ] `adapter_config.json` + `run_metadata.json` per task  
- [ ] `training_summary_*.json` + `train_all_lora.log`  
- [ ] Spider gold eval folder under `results/`  
- [ ] Row in [`version-tracker.md`](./version-tracker.md)  
- [ ] Short note here under “Results log” below  

---

## Results log

| Version | Date | Key deltas vs prior | text2sql exec | sql2nosql exec | doc judge | Keep? |
|---------|------|---------------------|---------------|----------------|-----------|-------|
| v3 | 2026-07-09 | Full TEND, r=16, attn only | 54% | 74% | 6.45 | Yes (baseline) |
| v4 | *TBD* | r=32 + fc_in/fc_out | | | | |
| v5 | *TBD* | lr 1e-4 (± larger batch) | | | | |
| v6 | *TBD* | dataset quality | | | | |
| v7 | *TBD* | dropout / epochs | | | | |

---

## Notes on priorities already satisfied

- **Weight decay 0.01** — present in `configs/default.yaml` and all of v1–v3 `training_args.bin`. Do not treat as a new experiment unless ablating off.  
- **>5 epochs** — lowest priority; full-data v3 already uses 5; text2sql did not finish 5 cleanly — fix completeness/eval first before pushing epochs.
