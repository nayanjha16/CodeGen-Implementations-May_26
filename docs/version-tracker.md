# LoRA Version Tracker

Base model and LoRA adapters under `models/`. Hyperparameters, datasets, training scale, and Spider gold validation metrics for **baseline → v1 → v2 → v3 → v4**.

Sources: `configs/default.yaml`, `models/checkpoints/{v1,v2,v3,v4}/**/{adapter_config.json,run_metadata.json,training_args.bin,training_summary_*.json}`, `results/spider_gold_validation_*/metrics.json`.

Comparison report: [lora-v4-vs-all-versions-comparison.md](lora-v4-vs-all-versions-comparison.md)

---

## Quick comparison

| Version | Type | Train samples | Epochs | LoRA | Scale | Checkpoint path |
|---------|------|---------------|--------|------|-------|-----------------|
| **Baseline** | No LoRA | — | — | — | Zero-shot | `models/base/Salesforce__codegen-350M-multi` |
| **v1** | LoRA | 50 | 10 | `r=16`, attn only | Smoke | `models/checkpoints/v1/` |
| **v2** | LoRA | 500 | 5 | `r=16`, attn only | Mid | `models/checkpoints/v2/` |
| **v3** | LoRA | ~8,040 | 5* | `r=16`, attn only | Full TEND | `models/checkpoints/v3/` |
| **v4** | LoRA | ~8,040 | 5 | **`r=32`, attn + FFN** | Full TEND | `models/checkpoints/v4/` |

\*v3 text2sql best checkpoint is epoch 2 only; sql2nosql / nosql2doc completed 5 epochs. See [v3 notes](#v3--full-scale-lora).

---

## Shared settings

### Unchanged across v1–v4

| Parameter | Value |
|-----------|-------|
| Base model | `Salesforce/codegen-350M-multi` |
| Base cache | `models/base/Salesforce__codegen-350M-multi` |
| PEFT type | LoRA (`lora_dropout=0.05`, `bias=none`) |
| Learning rate | `2e-4`, cosine schedule, warmup ratio `0.05` |
| Weight decay | `0.01` |
| Per-device batch | 8 |
| Grad accumulation | 4 → **effective batch = 32** |
| Optimizer | `adamw_torch_fused` |
| Precision | fp32 (`fp16=false`, `bf16=false`) |
| Seed | 42 |
| Max sequence | 2048 (prompt budget 1792 + target reserve 256) |
| Training data source | Hugging Face [`care2achieve/tend`](https://huggingface.co/datasets/care2achieve/tend) configs `spider` + `bird` |

Config defaults live in `configs/default.yaml`.

### LoRA config by version

| Parameter | v1–v3 | v4 |
|-----------|-------|----|
| Rank (`r`) | 16 | **32** |
| Alpha (`lora_alpha`) | 32 | **64** |
| Target modules | `qkv_proj`, `out_proj` | **`qkv_proj`, `out_proj`, `fc_in`, `fc_out`** |
| Adapter size (per task) | ~7.5 MB | **~40 MB** |
| Device | MPS (local) | CUDA (Kaggle) |

---

## Baseline (no fine-tuning)

| Field | Value |
|-------|-------|
| Adapter | none |
| Dataset (train) | — |
| Eval | `spider_gold_validation` (50 examples/task) |
| Results | `results/spider_gold_validation_codegen-350M-multi_0607_1841/` |

### Gold validation metrics

| Task | Execution acc | Exact match | Structural / Emb / Judge |
|------|---------------|-------------|--------------------------|
| text2sql | 0.12 | 0.00 | struct 0.70 |
| sql2nosql | 0.22 | 0.04 | struct 0.16 |
| documentation | — | 0.00 | emb 0.71, judge 0.086 |

---

## v1 — smoke-scale LoRA

| Field | Value |
|-------|-------|
| Path | `models/checkpoints/v1/` |
| Started | 2026-07-06 (kept summary `training_summary_20260706_210616.json`) |
| `max_samples` | **50** |
| Epochs | **10** |
| Train / eval rows | 50 / 50 per task |
| Dataset pool | TEND spider+bird (8040 available; capped at 50) |
| Best checkpoints | `checkpoint-20` (all tasks) |
| Log | `models/checkpoints/v1/train_all_lora.log` |

### Per-task training

| Task | Train loss | Best eval loss | Runtime (s) |
|------|------------|----------------|-------------|
| text2sql | 0.824 | 0.699 | 116 |
| sql2nosql | 0.755 | 0.791 | 214 |
| nosql2doc | 2.447 | 2.076 | 255 |

### Gold validation metrics

`results/spider_gold_validation_codegen-350M-multi_lora-v1_0607_2108/`

| Task | Execution acc | Exact match | Structural / Emb / Judge |
|------|---------------|-------------|--------------------------|
| text2sql | 0.20 | 0.08 | struct 0.79 |
| sql2nosql | 0.04 | 0.00 | struct 0.55 |
| documentation | — | 0.00 | emb 0.89, judge 1.51 |

---

## v2 — mid-scale LoRA

| Field | Value |
|-------|-------|
| Path | `models/checkpoints/v2/` |
| Started | 2026-07-06 (`training_summary_20260706_222504.json`) |
| `max_samples` | **500** |
| Epochs | **5** |
| Train / eval rows | 500 / 500 per task |
| Dataset pool | TEND spider+bird (capped at 500) |
| Best checkpoints | text2sql `64`, sql2nosql `80`, nosql2doc `64` |
| Log | `models/checkpoints/v2/train_all_lora.log` |

### Per-task training

| Task | Train loss | Best eval loss | Runtime (s) |
|------|------------|----------------|-------------|
| text2sql | 0.403 | 0.325 | 672 |
| sql2nosql | 0.369 | 0.229 | 1192 |
| nosql2doc | 1.631 | 1.497 | 1505 |

### Gold validation metrics

`results/spider_gold_validation_codegen-350M-multi_lora-v2_0607_2226/`

| Task | Execution acc | Exact match | Structural / Emb / Judge |
|------|---------------|-------------|--------------------------|
| text2sql | 0.34 | 0.20 | struct 0.86 |
| sql2nosql | 0.32 | 0.08 | struct 0.79 |
| documentation | — | 0.00 | emb 0.93, judge 3.11 |

---

## v3 — full-scale LoRA

| Field | Value |
|-------|-------|
| Path | `models/checkpoints/v3/` |
| Started | 2026-07-08 (text2sql), resumed sql2nosql/nosql2doc 2026-07-08 evening → finished 2026-07-09 |
| `max_samples` | **none** (full pool) |
| Epochs | **5** planned |
| Train rows | text2sql / nosql2doc **8040**; sql2nosql **7998** (42 dropped: `sequence_too_long`) |
| Eval rows | **1035** (TEND test spider+bird) |
| Dataset | Full combined TEND train (`spider` + `bird`) |
| Best checkpoints | text2sql `504` (epoch **2**), sql2nosql `750` (epoch 3), nosql2doc `756` (epoch 3) |
| Log | `models/checkpoints/v3/train_all_lora.log` |

### Per-task training

| Task | Train loss | Best eval loss | Runtime | Notes |
|------|------------|----------------|---------|-------|
| text2sql | — | **0.252** @ ep2 | incomplete metadata | Missing `run_metadata.json`; verify failed at end of log |
| sql2nosql | 0.074 | **0.045** | ~19,823 s (~5.5 h) | Complete |
| nosql2doc | 0.991 | **1.067** | ~25,454 s (~7.1 h) | Complete |

### Gold validation metrics

`results/spider_gold_validation_codegen-350M-multi_lora-v3_0907_1321/`

| Task | Execution acc | Exact match | Structural / Emb / Judge |
|------|---------------|-------------|--------------------------|
| text2sql | 0.54 | 0.38 | struct 0.91 |
| sql2nosql | 0.74 | 0.58 | struct 0.93 |
| documentation | — | 0.02 | emb 0.96, judge 6.45 |

---

## v4 — full-scale LoRA (wider adapters + FFN targets)

| Field | Value |
|-------|-------|
| Path | `models/checkpoints/v4/` |
| Started | 2026-07-18 08:36 UTC → finished 16:10 UTC (~7h 34m wall clock) |
| Summary | `training_summary_20260718_161004.json` |
| `max_samples` | **none** (full pool) |
| Epochs | **5** (all tasks completed) |
| Train rows | text2sql / nosql2doc **8040**; sql2nosql **7998** |
| Eval rows | **1035** (TEND test spider+bird) |
| Dataset | Full combined TEND train (`spider` + `bird`) |
| LoRA | `r=32`, `lora_alpha=64`, targets: `qkv_proj`, `out_proj`, `fc_in`, `fc_out` |
| Best checkpoints | text2sql `503` (epoch **1**), sql2nosql `1500` (epoch 3), nosql2doc `1006` (epoch 2) |
| Log | `models/checkpoints/v4/train_all_lora.log` |
| Where trained | Kaggle (CUDA) |

### Per-task training

| Task | Train loss | Best eval loss | Runtime (s) |
|------|------------|----------------|-------------|
| text2sql | 0.089 | **0.247** | 8,002 (~2h 13m) |
| sql2nosql | 0.038 | **0.034** | 8,307 (~2h 18m) |
| nosql2doc | 0.568 | **0.994** | 10,531 (~2h 55m) |

**Total GPU training time:** ~26,840 s (~7h 27m)

### Gold validation metrics

`results/spider_gold_validation_codegen-350M-multi_lora-v4_1807_2149/`

| Task | Execution acc | Exact match | Structural / Emb / Judge |
|------|---------------|-------------|--------------------------|
| text2sql | 0.60 | 0.40 | struct 0.92 |
| sql2nosql | 0.88 | 0.80 | struct 0.98 |
| documentation | — | 0.02 | emb 0.96, judge 7.79 |

---

## Metric progression (execution / judge)

| Run | text2sql exec | sql2nosql exec | doc judge |
|-----|---------------|----------------|-----------|
| Baseline | 12% | 22% | 0.09 |
| v1 | 20% | 4% | 1.51 |
| v2 | 34% | 32% | 3.11 |
| v3 | 54% | 74% | 6.45 |
| **v4** | **60%** | **88%** | **7.79** |

---

## What changed in v4 vs prior experiments

These levers were **already applied** in v1–v3:

- Weight decay **0.01**
- Effective batch size **32**
- v2/v3/v4 train **5 epochs** (v1 used 10)
- Full TEND scale (~8k samples) since v3

**New in v4** (from updated `configs/default.yaml` LoRA block):

- LoRA rank **16 → 32**
- LoRA alpha **32 → 64**
- Target modules expanded to include **`fc_in`** and **`fc_out`**
- Training moved to **Kaggle CUDA** (faster, single-session run)

---

## How to update this tracker

After each new checkpoint run:

1. Copy hyperparameters from `adapter_config.json` + `training_args.bin` / CLI flags.
2. Copy row counts and losses from `run_metadata.json` (and `training_summary_*.json`).
3. Add Spider gold metrics from `results/spider_gold_validation_*_lora-vN_*/metrics.json`.
4. Link the new section in the quick comparison table above.
