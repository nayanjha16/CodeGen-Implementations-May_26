# LoRA Version Tracker

Training runs, eval metrics, and production status for **Salesforce/codegen-350M-multi** on the Spider gold validation set (`data/spider_gold_validation.jsonl`).

**Production today:** LoRA **v3** on Cloud Run (`fastapi-deploy`, `checkpoint_version: v3` in `manifest.yaml`).

**Related docs:** [evaluation-and-deploy-runbook.md](evaluation-and-deploy-runbook.md) · [gold-set-commands.md](gold-set-commands.md) · [lora-v1-v3-vs-baseline-comparison.pptx](lora-v1-v3-vs-baseline-comparison.pptx) · [../project-demo/README.md](../project-demo/README.md)

---

## Quick comparison

| Version | Type | Train scale | Epochs | Eval n | Checkpoint path | Results path |
|---------|------|-------------|--------|--------|-----------------|--------------|
| **Baseline** | Zero-shot | — | — | 50 | `models/base/` | `results/spider_gold_validation_codegen-350M-multi_baseline-v3/` |
| **v1** | LoRA smoke | 50 rows / task | 10 | 5 (smoke) · 50 (extended) | `models/checkpoints/v1/` | `…_lora-v1/` · `…_lora-v1_50samples/` |
| **v2** | LoRA full TEND (r=16) | ~8,040 rows / task | **5** | 50 | `models/checkpoints/v2/` | `results/spider_gold_validation_codegen-350M-multi_lora-v2/` |
| **v3** | LoRA full TEND (r=32 + FFN) | ~8,040 rows / task | **10** | 50 | `models/checkpoints/v3/` | `results/spider_gold_validation_codegen-350M-multi_lora-v3/` |

Checkpoints are gitignored; restore from local disk or re-train. Hub repos (production): `codegenstudio/codegen-350M-{text2sql,sql2nosql,nosql2doc}-lora`.

---

## Training hyperparameters by version

v1 uses the **smoke LoRA recipe** (AD-6, capped samples).  
**v2 and v3 both train on the full TEND pool** (~8k rows / task). Differences: v2 uses AD-6 (r=16, attention only, **5 epochs**); **v3 uses [`configs/default.yaml`](../../configs/default.yaml)** (r=32 + FFN targets, **10 epochs**).

| Parameter | v1 | v2 | v3 |
|-----------|----|----|-----|
| **Config source** | AD-6 (fixed recipe) | AD-6 (same as v1) | **`configs/default.yaml`** |
| LoRA rank (`r`) | 16 | 16 | **32** |
| LoRA alpha | 32 | 32 | **64** |
| Target modules | `qkv_proj`, `out_proj` | `qkv_proj`, `out_proj` | **`qkv_proj`, `out_proj`, `fc_in`, `fc_out`** |
| LoRA dropout | 0.05 | 0.05 | 0.05 |
| Learning rate | 2e-4 | 2e-4 | 2e-4 |
| LR schedule | cosine, warmup 0.05 | cosine, warmup 0.05 | cosine, warmup 0.05 |
| Weight decay | 0.01 | 0.01 | 0.01 |
| Epochs | **10** | **5** | **10** |
| `--max-samples` | **50** / task | **none** (full TEND) | **none** (full TEND) |
| Train rows (typical) | 50 | ~8,040 (sql2nosql ~7,998) | ~8,040 (sql2nosql ~7,998) |
| Per-device batch | 8 | 8 | 8 (2 on Kaggle — see below) |
| Grad accumulation | 4 | 4 | 4 (8 on Kaggle) |
| Effective batch | **32** | **32** | **32** local · **16** on Kaggle GPU |
| Training data | TEND `spider` + `bird` | TEND `spider` + `bird` | TEND `spider` + `bird` |
| Device (typical) | CPU / MPS (local) | CUDA Kaggle or local · [notebook](../../notebooks/kaggle_train_lora_v2.ipynb) | CPU local · CUDA [notebook](../../notebooks/kaggle_train_lora_v3.ipynb) |
| Train command | `train_all_lora.py --version v1 --max-samples 50` | `train_all_lora.py --version v2` | `train_all_lora.py --version v3` |
| Eval judge | Ollama `gemma3:4b` | Ollama `gemma3:4b` | Ollama `gemma3:4b` |
| Gold eval decoding | greedy | greedy | greedy |

**v3 LoRA block in config (authoritative for production v3):**

```yaml
# configs/default.yaml
training:
  epochs: 10
lora:
  r: 32
  lora_alpha: 64
  lora_dropout: 0.05
  target_modules: [qkv_proj, out_proj, fc_in, fc_out]
```

**Kaggle batch override** (both `kaggle_train_lora_v2.ipynb` and `kaggle_train_lora_v3.ipynb` patch the working copy of `configs/default.yaml`):

- `per_device_train_batch_size`: 8 → **2**
- `per_device_eval_batch_size`: 8 → **2**
- `gradient_accumulation_steps`: 4 → **8** → effective batch **16**

---

## Gold validation metrics (n=50, DB execution)

Primary comparison uses **execution accuracy** (text2sql / sql2nosql) and **judge score /10** (documentation). Source: `metrics.json` in each results folder.

| Run | text2sql exec | sql2nosql exec | doc judge |
|-----|---------------|----------------|-----------|
| Baseline v3 | 14% | 22% | 8.33 |
| LoRA v2 | 60% | 74% | 8.41 |
| **LoRA v3 (prod)** | **66%** | **86%** | **8.82** |

Exact match (v3): text2sql 48%, sql2nosql 78%. Structural similarity: text2sql 0.95, sql2nosql 0.98.

---

## v1 — smoke LoRA

| Field | Value |
|-------|-------|
| Path | `models/checkpoints/v1/` |
| LoRA | **r=16**, alpha 32, attention projections only |
| Train | 50 samples / task, **10 epochs** |
| Purpose | Pipeline smoke test before mid/full runs |

**Smoke eval (n=5):** `results/spider_gold_validation_codegen-350M-multi_lora-v1/` — judge correct rate text2sql 40%, sql2nosql 100%, doc 100%.

**Extended eval (n=50, no DB execution):** `results/spider_gold_validation_codegen-350M-multi_lora-v1_50samples/`.

---

## v2 — full TEND LoRA (r=16)

| Field | Value |
|-------|-------|
| Path | `models/checkpoints/v2/` |
| LoRA | **Same as v1** (r=16, `qkv_proj` + `out_proj`) — AD-6 recipe |
| Train | **Full TEND pool** (~8k / task), **5 epochs**, no `--max-samples` cap |
| Results | `results/spider_gold_validation_codegen-350M-multi_lora-v2/` |

**v2 vs v3:** same training scale; v3 adds **wider LoRA** (r=32 + FFN) and **10 epochs** vs v2’s **5**.

Comparison report: [baseline-vs-lora-v2-comparison.md](../../results/spider_gold_validation_codegen-350M-multi_lora-v2/baseline-vs-lora-v2-comparison.md)

---

## v3 — full-scale LoRA (production)

| Field | Value |
|-------|-------|
| Path | `models/checkpoints/v3/` |
| LoRA | **`configs/default.yaml`** — r=32, alpha 64, attn + **FFN** targets |
| Train | Full TEND pool (~8k / task), **10 epochs**, same scale as v2, no `--max-samples` cap |
| Baseline eval | `results/spider_gold_validation_codegen-350M-multi_baseline-v3/` |
| LoRA eval | `results/spider_gold_validation_codegen-350M-multi_lora-v3/` |
| Published | Hub `codegenstudio/*-lora` |
| Deployed | Cloud Run `codegen-api` — see [Multi_Adapter_Deployment_Plan.md](Multi_Adapter_Deployment_Plan.md) |
| Agent | `agent/` calls Cloud Run via `CODEGEN_API_URL` |

Presentation: [lora-v1-v3-vs-baseline-comparison.pptx](lora-v1-v3-vs-baseline-comparison.pptx).

---

## Production deploy checklist

After a new checkpoint version (e.g. **vN** when you re-train):

1. Train with updated `configs/default.yaml`, then eval: `python scripts/run_baseline_eval.py --adapter-run vN --max-samples 50 --output …`
2. Update this tracker from `metrics.json` and `adapter_config.json` under `models/checkpoints/vN/`.
3. Publish: `python fastapi-deploy/publish/push_adapters.py --version vN`
4. Set `checkpoint_version: vN` in `fastapi-deploy/manifest.yaml`
5. Redeploy: `python fastapi-deploy/infra/cloudrun/deploy.py`
6. Verify `/health` shows `"checkpoint_version": "vN"` and adapters loaded.

Full commands: [gold-set-commands.md](gold-set-commands.md) · [evaluation-and-deploy-runbook.md](evaluation-and-deploy-runbook.md).
