# Salesforce/codegen-350M-multi — Model Reference

Detailed technical reference for the base causal language model used in this project. Values below come from the published [Hugging Face config](https://huggingface.co/Salesforce/codegen-350M-multi/blob/main/config.json), the [CodeGen paper (ICLR 2023)](https://arxiv.org/abs/2203.13474), and the [Transformers `CodeGenAttention` implementation](https://github.com/huggingface/transformers/blob/main/src/transformers/models/codegen/modeling_codegen.py).

---

## Overview

| Property | Value |
|----------|-------|
| **Model ID** | `Salesforce/codegen-350M-multi` |
| **Variant** | CodeGen-Multi 350M |
| **Architecture** | Decoder-only autoregressive Transformer (GPT-J–style parallel block) |
| **Task** | Causal language modeling (`CodeGenForCausalLM`) |
| **Parameters** | ~350M trainable (356.6M counted from config; see [Parameter budget](#parameter-budget)) |
| **Context length** | 2,048 tokens |
| **Pre-training lineage** | Initialized from CodeGen-NL 350M, then trained on **BIGQUERY** (multi-language code) |
| **License** | BSD-3-Clause |
| **Default in this repo** | `MODEL_NAME` in `.env` |

**Multi** means the checkpoint was further pre-trained on a large multi-language code corpus (BIGQUERY), not natural language alone. **350M** is the approximate parameter count of the full model.

---

## Architecture

CodeGen-350M-multi is a left-to-right (causal) decoder stack. Each layer uses a **parallel residual block** (GPT-J style):

```
x_{t+1} = x_t + attn(LN(x_t)) + mlp(LN(x_t))
```

Attention and feed-forward branches read the same layer-normalized input in parallel (unlike the classic GPT-2 ordering `x + attn(LN(x + attn(...)))`).

Key design choices:

- **Rotary Position Embedding (RoPE)** on the first `rotary_dim` dimensions of each head (partial RoPE; remaining head dimensions are unrotated).
- **Fused QKV projection** — one linear layer `qkv_proj` maps hidden states to query, key, and value.
- **No bias** in attention or MLP linear layers.
- **Activation:** `gelu_new` (GPT-2 variant of GELU).
- **Weight tying:** disabled (`tie_word_embeddings: false`); token embedding and LM head are separate matrices.

### Block diagram (one layer)

```
hidden [B, L, 1024]
        │
        ├─ LN ──► qkv_proj ──► split Q,K,V ──► RoPE ──► softmax(QKᵀ/√d) V ──► out_proj ──┐
        │                                                                                  │
        └─ LN ──► fc_in(1024→4096) ──► GELU ──► fc_out(4096→1024) ───────────────────────┤
                                                                                           │
                                              residual add ◄───────────────────────────────┘
```

---

## Hyperparameters (from `config.json`)

These are the values Hugging Face loads when you call `AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-multi")`.

### Model dimensions

| Config key | Value | Description |
|------------|-------|-------------|
| `n_layer` | **20** | Transformer decoder blocks |
| `n_head` | **16** | Attention heads per layer |
| `n_embd` | **1024** | Hidden size / embedding dimension |
| `head_dim` | **64** | `n_embd / n_head` (not stored; derived) |
| `n_inner` | **4096** | FFN inner dim (`4 × n_embd`; `null` in config → default 4096) |
| `n_positions` / `n_ctx` | **2048** | Maximum sequence length |
| `rotary_dim` | **32** | Head dimensions that receive RoPE (of 64 total per head) |
| `vocab_size` | **51200** | Token vocabulary size |

### Regularization & initialization

| Config key | Value |
|------------|-------|
| `attn_pdrop` | 0.0 |
| `embd_pdrop` | 0.0 |
| `resid_pdrop` | 0.0 |
| `layer_norm_epsilon` | 1e-5 |
| `initializer_range` | 0.02 |
| `scale_attn_weights` | true |

### Tokens & dtype

| Config key | Value |
|------------|-------|
| `bos_token_id` | 1 |
| `eos_token_id` | 50256 |
| `tokenizer_class` | `GPT2Tokenizer` |
| `torch_dtype` | `float16` (checkpoint storage; can load in fp32/bf16) |
| `use_cache` | true (KV cache supported for generation) |

---

## Attention: matrix sizes and tensor shapes

Understanding attention shapes is important for memory planning, LoRA targeting, and debugging generation.

### Per-head geometry

| Quantity | Size |
|----------|------|
| Hidden size (`d_model`) | 1024 |
| Number of heads (`H`) | 16 |
| Head dimension (`d_head`) | 64 |
| RoPE-applied dims | 32 (first 32 of 64 per head) |
| Max sequence length (`L_max`) | 2048 |

### Projection weight shapes (each of 20 layers)

| Module | Weight shape | Params per layer |
|--------|--------------|------------------|
| `qkv_proj` | `[3072, 1024]` | 3,145,728 |
| `out_proj` | `[1024, 1024]` | 1,048,576 |

`qkv_proj` output size is `3 × n_embd = 3072`, split into Q, K, V each of size `n_embd = 1024`.

### Forward-pass tensor shapes (batch size `B`, sequence length `L ≤ 2048`)

After `qkv_proj` and head splitting:

| Tensor | Shape |
|--------|-------|
| Query `Q` | `[B, 16, L, 64]` |
| Key `K` | `[B, 16, L, 64]` |
| Value `V` | `[B, 16, L, 64]` |

**Attention score matrix** (before softmax):

```
scores = Q @ Kᵀ / √64     →   shape [B, 16, L, L]
weights = softmax(scores) →   shape [B, 16, L, L]
output  = weights @ V     →   shape [B, 16, L, 64]
```

### Attention matrix size at full context

For a single layer, one sequence at `L = 2048`:

| Matrix | Dimensions | Elements | fp32 memory (approx.) |
|--------|------------|----------|------------------------|
| Per-head score matrix | 2048 × 2048 | 4,194,304 | ~16 MB |
| All heads (16) | 16 × 2048 × 2048 | 67,108,864 | ~256 MB |
| All 20 layers (if materialized) | 20 × 16 × 2048 × 2048 | 1,342,177,280 | ~5.1 GB |

In practice, frameworks compute scores per layer during the forward pass and do not keep all 20 layers in memory unless `output_attentions=True`.

### KV cache (autoregressive inference)

When `use_cache=True`, each layer stores key and value tensors for past tokens:

```
K_cache, V_cache: each [B, 16, L, 64]
```

At full context (`L = 2048`), KV cache per layer:

- Elements per tensor: `16 × 2048 × 64 = 2,097,152`
- Both K and V: ~4.2M elements/layer
- All 20 layers (fp16): ~168 MB per batch item

Scaling is **O(L × n_layer × n_head × head_dim)** for cache size and **O(L² × n_head)** per layer for attention compute during prefilling.

---

## Parameter budget

Approximate parameter count derived from architecture (matches ~350M naming):

| Component | Calculation | Parameters |
|-----------|-------------|------------|
| Token embedding `wte` | 51,200 × 1,024 | 52,428,800 |
| Per layer: `qkv_proj` | 1,024 × 3,072 × 20 | 62,914,560 |
| Per layer: `out_proj` | 1,024 × 1,024 × 20 | 20,971,520 |
| Per layer: `fc_in` | 1,024 × 4,096 × 20 | 83,886,080 |
| Per layer: `fc_out` | 4,096 × 1,024 × 20 | 83,886,080 |
| Layer norms | negligible | ~42,000 |
| LM head | 51,200 × 1,024 | 52,428,800 |
| **Total** | | **~356.6M** |

Checkpoint size on disk (fp16 weights): ~706 MB (`pytorch_model.bin`).

---

## Pre-training (original CodeGen-Multi 350M)

From Table 6 of the CodeGen paper (Appendix A). These are **pre-training** settings, not this repo's LoRA fine-tuning config.

### Architecture (350M row)

| Hyperparameter | Value |
|----------------|-------|
| Layers | 20 |
| Heads | 16 |
| Dimensions per head | 64 |
| Context length | 2,048 |

### Optimization — CODEGEN-MULTI on BIGQUERY

| Hyperparameter | 350M value |
|----------------|------------|
| Dataset | BIGQUERY (multi-language GitHub code) |
| Initialization | CodeGen-NL 350M weights |
| Learning rate | 1.8e-4 |
| Warm-up steps | 3,000 |
| Total steps | 150,000 |
| Batch size (tokens) | 500k |
| Weight decay | 0.1 |
| Optimizer | Adam (β₁=0.9, β₂=0.999, ε=1e-8) |
| Gradient clipping | global norm 1.0 |
| LR schedule | Warm-up + cosine decay (GPT-3 style) |

### Training data (BIGQUERY)

- **119.2B tokens** of multi-language source code from GitHub (via Google BigQuery public dataset).
- Languages include **C, C++, Go, Java, JavaScript, and Python**.
- Files filtered by extension; deduplication and whitespace normalization applied.

### Training stack

- Trained on **Google TPU v4-512** pods using **JAX** (JAXFORMER library).
- Data and model parallelism with SPMD / `pjit()`.
- Objective: standard causal **cross-entropy** (next-token prediction).

---

## Usage in this project

This repository uses `codegen-350M-multi` as the **shared frozen base** for three task-specific LoRA adapters (text2sql, sql2nosql, nosql2doc). Production serves **LoRA v3** via `fastapi-deploy/codegen_api` on Cloud Run.

**Version summary** — full table: [version-tracker.md](version-tracker.md)

| Version | Train scale | LoRA | Epochs | Role |
|---------|-------------|------|--------|------|
| v1 | 50 rows / task | r=16, attn only | 10 | Pipeline smoke test |
| v2 | Full TEND (~8k) | r=16, attn only | **5** | First full-corpus run |
| **v3 (prod)** | Full TEND (~8k) | r=32 + FFN | **10** | Published to Hub + Cloud Run |

### Project defaults (`configs/default.yaml`) — production v3

| Setting | Value | Notes |
|---------|-------|-------|
| `model.max_length` | 2048 | Matches model context |
| `generation.max_new_tokens` | 256 | Evaluation generation cap |
| `training.epochs` | **10** | v2 runs used **5** (`--epochs 5`) |
| LoRA `target_modules` | `qkv_proj`, `out_proj`, **`fc_in`**, **`fc_out`** | v1/v2 used attention only |
| LoRA `r` / `lora_alpha` | **32** / **64** | v1/v2 used 16 / 32 (AD-6) |

Pre-flight verification:

```bash
python scripts/inspect_lora_modules.py --model Salesforce/codegen-350M-multi
```

### Why these LoRA targets?

**v3 (production):** `qkv_proj`, `out_proj`, `fc_in`, and `fc_out` — attention plus FFN layers. Wider rank (r=32) gives more capacity for structured outputs (SQL, MongoDB shell, documentation).

**v1 / v2 (AD-6 recipe):** `qkv_proj` and `out_proj` only — attention projections; MLP layers frozen. Same full TEND scale for v2 as v3; v3 adds FFN targets and 10 epochs vs v2’s 5.

### Loading the model

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Salesforce/codegen-350M-multi"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
```

With PEFT adapter (this project):

```python
from peft import PeftModel

model = PeftModel.from_pretrained(base_model, "models/checkpoints/v3/text2sql/")
```

Checkpoints: `models/checkpoints/v{1,2,3}/<task>/`. Production manifest: `fastapi-deploy/manifest.yaml` → `checkpoint_version: v3`.

---

## Comparison with other CodeGen 350M variants

Salesforce released three 350M pre-training variants:

| Checkpoint | Pre-training data | Use case |
|------------|-------------------|----------|
| `codegen-350M-nl` | THEPILE (natural language + code) | General text/code |
| **`codegen-350M-multi`** | BIGQUERY (multi-language code) | **Multi-language program synthesis** |
| `codegen-350M-mono` | BIGPYTHON (Python only) | Python-focused synthesis |

This project chose **multi** because database query tasks involve structured code-like outputs across SQL and MongoDB shell syntax, and the multi checkpoint generalizes better across programming languages than the mono variant.

---

## References

- Hugging Face model card: [Salesforce/codegen-350M-multi](https://huggingface.co/Salesforce/codegen-350M-multi)
- Paper: Nijkamp et al., *A Conversational Paradigm for Program Synthesis*, ICLR 2023 — [arXiv:2203.13474](https://arxiv.org/abs/2203.13474)
- Original codebase: [salesforce/CodeGen](https://github.com/salesforce/CodeGen)
- Transformers implementation: [`modeling_codegen.py`](https://github.com/huggingface/transformers/blob/main/src/transformers/models/codegen/modeling_codegen.py)

### Related docs in this repo

- [evaluation-and-training.md](evaluation-and-training.md) — `run_baseline_eval.py` and `train_all_lora.py` flows
- [evaluation-and-deploy-runbook.md](evaluation-and-deploy-runbook.md) — eval → publish → Cloud Run redeploy
- [version-tracker.md](version-tracker.md) — LoRA v1–v3 hyperparameters and gold-set metrics
- [Multi_Adapter_Deployment_Plan.md](Multi_Adapter_Deployment_Plan.md) — Cloud Run multi-adapter API
- [agent/README.md](../../agent/README.md) — AI Database Agent (calls Cloud Run v3 API)
