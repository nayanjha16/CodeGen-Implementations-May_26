# Requirements Analysis — PEFT / LoRA for text2sql, sql2nosql, nosql2doc

> Focus: what exists today vs. what must be built to fine-tune the three tasks with LoRA.

## 1. Implemented Features (verified in code)

### Generation / inference (all three tasks)
- [x] **text2sql**: `PromptBuilder` + `SQLGenerator` (greedy/beam, SQL extraction, stop
  strings). Validation (`SQLValidator`) and SQLite execution (`SQLExecutor`).
- [x] **sql2nosql**: `NoSQLPromptBuilder` + `NoSQLGenerator` (model-based) and
  `SQLToNoSQLTranslator` (rule-based reference). `NoSQLEvaluator`.
- [x] **nosql2doc**: `DocumentationPromptBuilder` + `DocumentationGenerator` (output
  sanitizing, reference fallback). `DocumentationEvaluator`, `ReferenceDocumentationBuilder`.
- [x] Model wrapper supports **causal LM and seq2seq (T5)** via `is_seq2seq_model()`.
- [x] Device auto-resolution **cuda > mps > cpu** (`resolve_device`).

### Model & checkpoint management
- [x] Local model caching (`ensure_model_cached`, `.downloaded` marker).
- [x] `MODEL_CHECKPOINT` env var → `resolve_model_path()` loads a checkpoint dir from
  `models/checkpoints/` instead of the base model (assumes a *full* HF model dir).
- [x] Six base models already cached: codegen-350M-multi, Qwen2.5-Coder-0.5B,
  Qwen2.5-0.5B-Instruct, starcoder2-3b, t5-base, t5-large.

### Dataset
- [x] **TEND dataset builder** produces aligned columns for all three tasks in one CSV
  (`data/TEND/spider_<split>_<ts>.csv`), with structural + Qwen-semantic quality flags.
- [x] Spider/BIRD loaders, preprocessing, statistics.

### Evaluation
- [x] Full metric suite + `BenchmarkRunner` that scores text2sql, sql2nosql, and
  documentation in one pass; per-run JSON under `results/`; MLflow tracking.

## 2. Missing / To-Build for LoRA (the actual work)

- [ ] **`peft` dependency** — not in `requirements.txt`/`environment.yml`. Add `peft`;
  optionally `trl` (for `SFTTrainer`) and `bitsandbytes` (CUDA QLoRA only).
- [ ] **No training code at all** — no `Trainer`, `TrainingArguments`, `train.py`, or
  `src/training/` package. Must build from scratch.
- [ ] **SFT dataset builder** — convert TEND CSV rows → `(prompt, target)` per task using
  the existing prompt builders; tokenize; mask prompt tokens in labels for causal LMs.
- [ ] **LoRA training loop** — `LoraConfig` (rank/alpha/dropout/target_modules per model
  family), `get_peft_model`, train, save adapter to `models/checkpoints/`.
- [ ] **Adapter-aware loading** — extend `CodeGenModel.load()` to detect
  `adapter_config.json` and wrap base with `PeftModel.from_pretrained` (or
  `merge_and_unload`). Current loader only handles full model dirs.
- [ ] **Per-task config** — `configs/default.yaml` needs a `training:`/`lora:` section and
  a way to select task (text2sql / sql2nosql / nosql2doc) + target column.
- [ ] **Full-size training data** — regenerate the complete Spider train split through
  `run_all_tend.py` (current CSVs are 10+10 rows only).
- [ ] **Train/val/test discipline** — define held-out evaluation that is not used for
  training; today only one timestamped CSV per split exists.
- [ ] **Adapter composition strategy** — three separate adapters vs. one multi-task adapter
  vs. shared base; decision not made.

## 3. Inferred / Implicit Requirements

- **Prompt parity**: training must use the *same* prompt builders as inference, or the
  fine-tuned model sees a distribution shift at eval time. This is the single most
  important consistency requirement.
- **Reproducibility**: seeds + config-driven hyperparameters; log every run to MLflow with
  task, base model, LoRA config, and metrics for baseline-vs-LoRA comparison.
- **Resource-aware**: small base models + LoRA chosen specifically so training fits on
  modest hardware (MPS/CPU or a single small GPU). Avoid CUDA-only paths as hard deps.
- **Swappable adapters**: keep base models untouched in `models/base/`; store adapters
  separately so multiple task adapters coexist.
- **Offline-friendly**: base models already cached; training should not require new
  downloads beyond `peft`/`trl` wheels.
- **Apples-to-apples eval**: fine-tuned models scored by the existing `BenchmarkRunner` on
  the same metrics/datasets as the baseline.

## 4. Constraints

- **Python 3.11**; `PYTHONPATH` must include project root for `src.*` / `TEND.*` imports.
- **Hardware**: macOS dev host → **MPS**. `bitsandbytes`/4-bit QLoRA is **CUDA-only**;
  plan plain LoRA (fp16/fp32) for portability, QLoRA only as a CUDA-optional path.
- **Mixed architectures**: causal vs seq2seq need different `task_type`, target modules,
  and label construction.
- **Tokenizer pad token**: causal tokenizers may lack a pad token (`pad_token = eos_token`
  is already set in `load()`); training collator must respect this.
- **Data volume**: only 10+10 TEND rows exist now; Spider train is ~7k examples — must be
  regenerated (Qwen doc generation is slow on CPU/MPS).
- **License**: research/academic; Spider, BIRD, and base-model licenses apply.

## 5. Acceptance-style Expectations (for the LoRA deliverable)

- A `peft`-based training script trains a LoRA adapter for a chosen task and base model,
  saving `adapter_config.json` + adapter weights under `models/checkpoints/<name>/`.
- `CodeGenModel` (or `load_model`) can load base + adapter and generate.
- `BenchmarkRunner` produces a `results/<run>/metrics.json` for the fine-tuned model that
  is directly comparable to the cached baseline runs in `results/`.
- LoRA run shows **measurable improvement** over baseline on at least the primary metric
  per task (e.g. text2sql execution accuracy / exact match; sql2nosql structural
  equivalence / token-F1; documentation ROUGE-L / BERTScore vs the rule-based reference).
- Training is reproducible (seeded) and logged to MLflow.

## 6. Baseline Numbers to Beat — **chosen model: `Salesforce/codegen-350M-multi`**

> **Finalized base model (2026-06-21): `Salesforce/codegen-350M-multi`** (causal LM).
> Baseline below from `results/spider_codegen-350M-multi_2006_1620` (10-sample Spider
> validation, greedy).

| Task | exact_match | exec_acc | token_f1 | rouge_l | bertscore | struct_equiv | qwen_correct |
|------|-------------|----------|----------|---------|-----------|--------------|--------------|
| text2sql | 0.0 | 0.0 | 0.0 | 0.27 | 0.54 | 0.0 | 0.20 |
| sql2nosql | 0.0 | 0.0 | 0.07 | 0.07 | 0.04 | 0.20 | 0.20 |
| documentation | 0.0 | — | 0.03 | 0.02 | 0.03 | 0.0 | 0.0 |

The 350M baseline is weak across all three tasks (esp. sql2nosql and documentation), so
there is **large headroom** for LoRA gains. For reference, Qwen2.5-Coder-0.5B scored
higher zero-shot (text2sql rouge_l 0.60 / bertscore 0.89; sql2nosql token_f1 0.85), but
codegen-350M-multi was selected as the training base. Re-establish a full-dataset baseline
before/after training for a fair comparison.
