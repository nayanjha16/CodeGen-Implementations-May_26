# Feature Plan — LoRA Fine-Tuning for text2sql / sql2nosql / nosql2doc

> **Feature slug:** `lora-finetuning`  
> **Date:** 2026-06-21  
> **Status:** Pending approval (`approvals/lora-finetuning-approval.md`)

## 1. Scope

### In scope

Build a **parameter-efficient fine-tuning (PEFT / LoRA)** pipeline that:

1. Converts TEND CSV rows into supervised `(prompt, target)` pairs for each of three tasks, using the **existing prompt builders** so train-time and eval-time prompts match.
2. Trains **one LoRA adapter per task** on base model **`Salesforce/codegen-350M-multi`** (causal LM only).
3. Saves every fine-tuned adapter under **`models/checkpoints/`** (project root, via
   `get_models_checkpoints_dir()` / `MODELS_CHECKPOINTS_DIR`) — one subdirectory per task
   (`adapter_config.json` + `adapter_model.safetensors`) — **no merge** with the base model.
4. Extends `CodeGenModel` / `load_model()` to load base + adapter by task intent.
5. Reuses `BenchmarkRunner` + MLflow for apples-to-apples comparison against the existing baseline in `results/`.

### Out of scope

- Full fine-tuning (all weights).
- QLoRA / `bitsandbytes` (CUDA-only).
- Seq2seq / T5 training path (causal LM only for v1).
- Multi-task or shared adapter (one adapter per task).
- BIRD dataset (Spider only for v1).
- Web UI, API, or new evaluation metrics.

### Deliverables (code)

| Component | Path |
|-----------|------|
| Training package | `src/training/` |
| Train CLI | `scripts/train_lora.py` |
| Eval CLI extension | `scripts/run_baseline_eval.py` — `--adapter` / `--task` flags |
| Config block | `configs/default.yaml` — `training:` + `lora:` sections |
| Model loader extension | `src/models/model_loader.py` — PEFT adapter detection + load |
| Tests | `tests/training/` — prompt parity, overfit smoke, adapter load |

---

## 2. Architecture Decisions

### AD-1: Trainer — `trl.SFTTrainer` with completion-only loss

**Decision:** Use `trl.SFTTrainer` + `DataCollatorForCompletionOnlyLM` (or TRL's `response_template` / `completion_only_loss` path).

**Rationale:** Handles causal-LM label masking (prompt tokens → `-100`) correctly; avoids hand-rolling a collator. `peft` + `trl` are already in `requirements.txt`.

**Alternative rejected:** Raw HF `Trainer` with a custom collator — more code, same outcome.

### AD-2: SFT text format — prompt + target concatenated

For causal LM, each training example is a single string:

```
{prompt}{target}
```

The collator masks everything before the target boundary. Prompt builders already end with task-specific suffixes (`SQL:`, `MongoDB:`, `Documentation:`) that serve as **response templates** for the collator.

| Task | Response template (suffix marking start of target) |
|------|-----------------------------------------------------|
| text2sql | `\nSQL:\n` (last occurrence in prompt) |
| sql2nosql | `\nMongoDB:\n` |
| nosql2doc | `\nDocumentation:\n` |

### AD-3: Dataset builder reuses runtime prompt builders

| Task | Builder | Input columns | Target column |
|------|---------|---------------|---------------|
| text2sql | `src.text2sql.PromptBuilder` | `question`, `sql_schema` | `sql_query` |
| sql2nosql | `src.sql2nosql.NoSQLPromptBuilder` | `sql_query`, `nosql_schema` | `nosql_query` |
| nosql2doc | `src.documentation.DocumentationPromptBuilder` | `nosql_query`, `nosql_schema`, `question` | `documentation` |

**Filter:** keep rows where `overall_correct == True` (resolved in research).

### AD-4: Sequence-length policy — reserve target first

- `max_length = 2048`, `max_target_tokens = 256` → **prompt budget = 1792 tokens**.
- Tokenize target first; if target > 256 tokens → **skip** row (log count).
- Truncate prompt from the **left** (schema region) to fit within 1792 tokens — never truncate the target.
- Mirrors inference behaviour in `CodeGenModel.generate()` (`truncation_side="left"`).

### AD-5: Adapter storage and loading — **`models/checkpoints/` only**

**All fine-tuned LoRA adapters MUST be written under `models/checkpoints/`** (never under
`models/base/` or ad-hoc paths). Resolved via `src.utils.paths.get_models_checkpoints_dir()`
(default `models/checkpoints/`; override with `MODELS_CHECKPOINTS_DIR` in `.env`).

```
models/checkpoints/
  text2sql/       # adapter_config.json + adapter_model.safetensors + run_metadata.json
  sql2nosql/
  nosql2doc/
```

- **Training default:** `scripts/train_lora.py --task text2sql` saves to
  `models/checkpoints/text2sql/` when `--output-dir` is omitted.
- **Loading default:** `load_model(adapter="text2sql")` resolves
  `get_models_checkpoints_dir() / "text2sql"`.
- Base weights stay in `models/base/`; only adapter files live in `models/checkpoints/`.

Loading flow:

```
ensure_model_cached(base) → AutoModelForCausalLM.from_pretrained(base)
→ PeftModel.from_pretrained(base_model, adapter_dir)
```

Expose via:

- Config: `model.adapter: text2sql` (or path)
- Env: `MODEL_ADAPTER=text2sql` (optional, alongside existing `MODEL_CHECKPOINT`)
- CLI: `--adapter text2sql` on eval script

Base model in `models/base/` stays untouched.

### AD-6: LoRA hyperparameters (from research)

```yaml
lora:
  r: 16
  lora_alpha: 32
  lora_dropout: 0.05
  bias: none
  target_modules: [qkv_proj, out_proj]   # verify on CodeGenForCausalLM before first run

training:
  learning_rate: 2e-4
  weight_decay: 0.01
  epochs: 5
  per_device_train_batch_size: 8
  per_device_eval_batch_size: 8
  gradient_accumulation_steps: 4        # effective batch = 32
  warmup_ratio: 0.05
  lr_scheduler_type: cosine
  max_grad_norm: 1.0
  fp16: false
  bf16: false                           # fp32 for MPS/CPU/CUDA portability
```

**Pre-flight check:** run `model.named_modules()` on codegen-350M-multi; if zero trainable params, fix `target_modules`.

### AD-7: Data corpus and splits

| Split | Source | Use |
|-------|--------|-----|
| Train | Spider **train** → TEND CSV | LoRA training (filtered) |
| Validation | Spider **dev/validation** → TEND CSV | Early stopping + held-out eval |
| Test | Same as validation for v1 | Benchmark comparison |

**Planning assumption (open Q8):** row-level disjointness via Spider's native splits; optionally enforce `db_id` disjointness in a follow-up if leakage is detected.

**Planning assumption (open Q7 — doc supervision):** train nosql2doc against the Qwen-generated `documentation` column (distillation). Report secondary metrics against `ReferenceDocumentationBuilder` output at eval time.

### AD-8: Success criteria

**Primary (per task):** `qwen_correct_rate` from existing `QwenEvaluator` + AST/structural gates (see `open-questions/questions.md` Q18).

**Planning assumption (open Q19 — minimum lift):** adapter run is successful if `qwen_correct_rate` improves by **≥ 0.10 absolute** over the codegen-350M baseline on the same held-out validation set, **or** reaches **≥ 0.50** if baseline is near zero. Revisit after full-dataset baseline is re-established.

**Secondary:** EM, exec acc, token-F1, ROUGE-L, BERTScore — logged to MLflow only.

### AD-9: Reproducibility and tracking

- Call `set_seeds()` before dataset shuffle and training.
- Log to MLflow: task, base model, LoRA config, train/eval loss, hyperparameters, adapter path, `qwen_correct_rate`.
- Same MLflow store as baseline (`sqlite:///mlflow.db`).

---

## 3. Execution Stages

### Stage 0 — Data preparation (prerequisite)

Regenerate full TEND dataset; freeze canonical CSV paths.

```bash
python scripts/run_all_tend.py                    # full train + validation
# or staged: --no-doc for text2sql/sql2nosql first, then doc pass for nosql2doc
```

Record frozen paths in `data/TEND/manifest.json` (new) so training/eval always reference the same files.

**Exit criteria:** train CSV ≥ 1k rows after `overall_correct` filter (expect ~30–60% survival); validation CSV ≥ 100 rows.

### Stage 1 — Foundation

- Add `training:` / `lora:` blocks to `configs/default.yaml`.
- Create `src/training/` package skeleton.
- Verify `peft` / `trl` import and LoRA target module names on codegen-350M.

**Exit criteria:** `python -c "from peft import LoraConfig; from trl import SFTTrainer"` succeeds; target modules confirmed.

### Stage 2 — SFT dataset builder

- `src/training/tend_dataset.py` — CSV → HuggingFace `Dataset` with `text` column.
- `src/training/tasks.py` — task enum, column maps, response templates.
- `src/training/filters.py` — `overall_correct == True` filter + length skip logging.
- `tests/training/test_prompt_parity.py` — assert dataset prompt == generator prompt for sample rows.

**Exit criteria:** prompt parity tests pass; dataset stats logged (rows kept/skipped).

### Stage 3 — LoRA trainer + overfit smoke test

- `src/training/lora_trainer.py` — build `LoraConfig`, wrap model, run `SFTTrainer`.
- `scripts/train_lora.py` — CLI: `--task`, `--train-csv`, `--eval-csv`, `--output-dir`, `--max-samples` (debug).
- Overfit test: 5 rows, 3 epochs → training loss → ~0.

**Exit criteria:** overfit smoke passes; adapter files written to output dir.

### Stage 4 — Adapter-aware model loading

- Extend `resolve_model_path()` / `CodeGenModel.load()` to detect `adapter_config.json`.
- Add `load_model(adapter=...)` parameter and config/env wiring.
- `tests/training/test_adapter_load.py` — load base + adapter, generate one prompt.

**Exit criteria:** adapter load + greedy generation works for each saved adapter.

### Stage 5 — Full training (per task)

Train three adapters sequentially (shared base, separate LoRA weights):

1. text2sql
2. sql2nosql
3. nosql2doc

Each run: 5 epochs, eval each epoch on validation split, save best adapter by eval loss (or final epoch if eval loss unavailable on MPS).

**Exit criteria:** three adapter dirs under `models/checkpoints/{text2sql,sql2nosql,nosql2doc}/`.

### Stage 6 — Evaluation integration

- Extend `scripts/run_baseline_eval.py` with `--adapter` / `--task` to load the correct adapter per pipeline stage (or run single-task eval).
- Run full `BenchmarkRunner` on validation set for each adapter vs baseline.
- Log comparison to MLflow and `results/<run>/metrics.json`.

**Exit criteria:** LoRA metrics JSON exists for all three tasks; primary metric shows lift over baseline.

---

## 4. Assumptions

| # | Assumption | If wrong |
|---|------------|----------|
| A1 | `peft` + `trl` already in `requirements.txt` and installable | Add/fix versions before Stage 1 |
| A2 | codegen-350M `target_modules` are `qkv_proj`, `out_proj` | Adjust config after module inspection |
| A3 | `overall_correct` filter leaves enough rows (~2–4k train) | Relax filter or regenerate with `--no-eval` then filter on structural flags only |
| A4 | Qwen-generated `documentation` is acceptable supervision for nosql2doc v1 | Switch to `ReferenceDocumentationBuilder` targets in Stage 5 if doc task fails |
| A5 | `SFTTrainer` runs on MPS/CPU in fp32 (slow but functional) | Reduce batch size; optional CUDA-only fast path later |
| A6 | Adapters are local artifacts, not committed to git | Document regen instructions in README |
| A7 | Single-task eval per adapter (BenchmarkRunner loads task-specific adapter per stage) | May need per-stage adapter injection in benchmark if end-to-end eval is required |

---

## 5. Open Items Carried into Implementation

Resolve during Stage 0–1; do not block approval unless marked **blocking**:

| ID | Question | Plan default |
|----|----------|--------------|
| Q7 | Doc supervision source | Qwen `documentation` column (distillation) |
| Q8 | Split disjointness | Spider native train/dev splits |
| Q9 | Full vs subset corpus | Full Spider train, quality-filtered |
| Q13 | Loss masking | Completion-only via TRL collator (confirmed in AD-2) |
| Q16 | Trainer choice | `trl.SFTTrainer` (confirmed in AD-1) |
| Q19 | Minimum lift threshold | ≥ 0.10 absolute or ≥ 0.50 absolute (AD-8) |
| Q23 | Adapter versioning | Local artifacts, `.gitignore`d, regen from script |

---

## 6. Related Documents

- Research: `ai-workflow/research/`
- Tasks: `ai-workflow/planning/task-breakdowns/lora-finetuning-tasks.md`
- Roadmap: `ai-workflow/planning/implementation-roadmaps/roadmap.md`
- Dependencies: `ai-workflow/planning/dependency-analysis/lora-finetuning-dependencies.md`
- Approval: `ai-workflow/planning/approvals/lora-finetuning-approval.md`
