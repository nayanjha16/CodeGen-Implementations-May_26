# Open Questions — PEFT / LoRA Initiative

Resolve before/early in planning. Each notes why it matters and the current assumption.

---

## ✅ Resolved Decisions (2026-06-21)

| # | Decision | Choice |
|---|----------|--------|
| Base model | Training base | **`Salesforce/codegen-350M-multi`** (causal LM) |
| Q1 | Adapter strategy | **One LoRA adapter per task** (text2sql / sql2nosql / nosql2doc) |
| Q3 | LoRA vs QLoRA | **Plain LoRA only** (no QLoRA / bitsandbytes) |
| Q4 | Full FT vs LoRA | **LoRA only — no full fine-tuning** |
| Q5 | Training corpus | **Full Spider train + held-out validation; BIRD later** |
| Q6 | Quality-flag filter | **Train only on rows where `overall_correct == True`** |
| Q10/Q11 | Hyperparameters & target modules | **Finalized — see config block below** |
| Q12 | Sequence-length budget | **Reserve target first: `max_length=2048`, `max_target_tokens=256` → prompt budget = 1792** |
| Q14 | Adapter storage & loading | **Do NOT merge — keep adapters separate, load by task intent** |
| Q18 | Primary metric per task | **LLM judge + AST/structural gates** — headline `qwen_correct_rate`; see per-task detail below |
| Q21 | Target training hardware | **Auto-detect at runtime** — CUDA → MPS → CPU via `resolve_device()`; must run on any machine |
| Q22 | Dependency additions | **`peft` + `trl`** in `requirements.txt` (installed via `environment.yml`); no `bitsandbytes` |

### Q18 — Primary success metric (per task)

Composite evaluation via existing `QwenEvaluator` + syntax/structural checks (not EM, exec acc,
ROUGE-L, or BERTScore as pass/fail criteria):

| Task | Headline metric | LLM judge field | AST / structural gates |
|------|-----------------|-----------------|------------------------|
| text2sql | `qwen_correct_rate` | `sql_correct` (Qwen) | `SQLValidator` syntax + completeness; exact-match short-circuit; table-mismatch rejection |
| sql2nosql | `qwen_correct_rate` | `query_correct` (Qwen) | MongoDB shell syntax validity; parsed `structural_equivalence` (filter/projection/collection) as diagnostic |
| nosql2doc | `qwen_correct_rate` | `doc_correct` (Qwen) | Empty/invalid output rejection; doc structural validity checks |

Secondary metrics (BLEU, ROUGE-L, BERTScore, token-F1, exec acc) remain logged for analysis
but do **not** define run success.

### Q21 — Target training hardware

**No fixed hardware target.** Training and inference pick the best available backend at
runtime and must remain runnable on any machine:

1. **`device: auto`** (default in `configs/default.yaml`) → `src/utils/device.resolve_device()`
2. **Priority:** CUDA (if available) → MPS (Apple Silicon) → CPU (universal fallback)
3. **Override:** optional config / CLI `--device cuda|mps|cpu` for forced runs or debugging
4. **Precision:** keep fp32 (no bf16/fp16 flags in training config) for cross-device compatibility;
   CUDA may still benefit from larger effective batch sizes; CPU runs may need a smaller
   `per_device_train_batch_size` if OOM — tune at runtime, not baked into the plan

LoRA on `codegen-350M-multi` is feasible on all three backends; wall-clock varies by device.

### Finalized `configs/default.yaml` block

```yaml
model:
  name: Salesforce/codegen-350M-multi

training:
  task_type: CAUSAL_LM

  learning_rate: 2e-4
  weight_decay: 0.01

  epochs: 5

  per_device_train_batch_size: 8
  per_device_eval_batch_size: 8

  gradient_accumulation_steps: 4   # effective batch size = 32

  warmup_ratio: 0.05

  lr_scheduler_type: cosine

  max_grad_norm: 1.0

  fp16: false
  bf16: false                      # full-precision (fp32) — MPS/CPU friendly

lora:
  enabled: true

  r: 16
  lora_alpha: 32
  lora_dropout: 0.05

  bias: none

  target_modules:
    - qkv_proj
    - out_proj

evaluation:
  max_new_tokens: 256
```

> **Verify before first run:** confirm `qkv_proj` and `out_proj` are the actual attention
> module names in `CodeGenForCausalLM` via `model.named_modules()`. If LoRA reports zero
> trainable params, the names are wrong.

---

## Still Open

## 1. Scope & Strategy

*(All resolved — see table above.)*

## 2. Data

6. ~~**Filter on quality flags?**~~ **RESOLVED:** keep only rows where
   **`overall_correct == True`** (Qwen judged both schema and query equivalence correct).
   This is the single training filter; it implicitly requires `conversion_success` too.
   *Caveat: tighter filter = fewer rows, and `overall_correct` is a 0.5B-model judgment —
   monitor surviving row count after regenerating the full Spider train split.*
7. **Documentation supervision source** — train against the Qwen-generated `documentation`
   column (distillation) or the rule-based `ReferenceDocumentationBuilder` output, or both?
8. **Train/validation/test split definition** — how to guarantee disjointness (row-level
   vs `db_id`-level) and freeze it for reproducible comparison? (Spider train → train;
   Spider dev/validation → held-out eval.)
9. **Dataset size target** — full ~7k, or a curated high-quality subset? Trade-off between
   coverage and generation cost/quality (Qwen doc generation is the bottleneck).

## 3. Training Configuration

12. ~~**Sequence length budget**~~ **RESOLVED — reserve target space first:**
    `max_length = 2048`, `max_target_tokens = 256` → **prompt budget = 2048 − 256 =
    1792 tokens**. Truncate the *prompt* (schema region) to ≤1792 tokens; never truncate
    the target. Skip/log any example whose target exceeds 256 tokens.
13. **Loss masking** — confirm prompt tokens masked to `-100` so loss is computed on the
    target completion only.

## 4. Integration & Tooling

14. ~~**Adapter storage & loading**~~ **RESOLVED — do NOT merge.** Keep each task's LoRA
    adapter separate under `models/checkpoints/<task>/` (`adapter_config.json` +
    `adapter_model.safetensors`) and **load by intent (task)** via
    `PeftModel.from_pretrained(base, adapter_dir)`. Requires an adapter-aware path in
    `model_loader` that detects `adapter_config.json` and wraps the cached base model
    (see Q17). Preserves swappability; base model stays untouched in `models/base/`.
15. **CLI / entry point** — new `scripts/train_lora.py` and `src/training/` package; args
    for task, data path, output adapter dir (base model + hyperparameters come from config).
16. **Trainer choice** — HF `Trainer` (manual collator) vs `trl.SFTTrainer` (adds `trl`
    dep, handles packing/masking).
17. **Eval integration** — reuse `BenchmarkRunner` with the fine-tuned model; need a way to
    point it at a per-task adapter (likely an adapter-aware path in `model_loader`).

## 5. Success Criteria

18. ~~**Primary metric per task**~~ **RESOLVED:** **LLM judge + AST/structural gates** —
    headline metric is **`qwen_correct_rate`** per task (see resolved table above). Reuses
    `src/evaluation/qwen_evaluator.py` and existing evaluators; EM / exec acc / ROUGE-L /
    BERTScore are secondary diagnostics only.
19. **Minimum acceptable lift** over baseline to call a run successful?
20. **Comparison protocol** — same eval set, same decoding strategy, logged to the same
    MLflow store as the baseline runs in `results/`.

## 6. Environment

21. ~~**Target training hardware**~~ **RESOLVED:** **auto-detect CUDA → MPS → CPU** via
    existing `resolve_device()` (`device: auto` in config); optional override; must run on
    any machine (see Q21 detail above).
22. ~~**Dependency additions**~~ **RESOLVED:** add **`peft>=0.11.0`** and **`trl>=0.9.0`**
    to `requirements.txt` (pulled in by `environment.yml` pip install). **`bitsandbytes`**
    not added — plain LoRA only (Q3).
23. **Adapter versioning** — should trained adapters be committed/shared, or treated as
    regenerable artifacts (current `.gitignore` ignores most of `models/`)?
