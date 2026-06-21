# Task Breakdown — LoRA Fine-Tuning

> **Feature:** `lora-finetuning`  
> **Date:** 2026-06-21

Complexity: **S** (< 2h), **M** (2–6h), **L** (6–16h), **XL** (> 16h, often wall-clock not code)

---

## Stage 0 — Data Preparation

| ID | Task | Depends on | Complexity | Notes |
|----|------|------------|------------|-------|
| D-01 | Run full TEND generation: `python scripts/run_all_tend.py` for train + validation | — | XL | Wall-clock dominated by Qwen doc + judge; run overnight if needed |
| D-02 | Create `data/TEND/manifest.json` recording canonical CSV paths, row counts, timestamp, filter survival rate | D-01 | S | Single source of truth for training scripts |
| D-03 | Profile `overall_correct == True` filter: count surviving rows per split | D-01 | S | If train < 500 rows, escalate before training |
| D-04 | (Optional) Generate text2sql/sql2nosql CSV with `--no-doc`, then doc pass for nosql2doc subset | D-01 | L | Speed optimization if full doc gen is too slow |

---

## Stage 1 — Foundation

| ID | Task | Depends on | Complexity | Notes |
|----|------|------------|------------|-------|
| F-01 | Add `training:` and `lora:` blocks to `configs/default.yaml` per feature plan AD-6 | — | S | Include `max_target_tokens: 256`, task defaults |
| F-02 | Extend `src/utils/config.py` with helpers: `get_training_config()`, `get_lora_config()`, `get_adapter_path(task)` → `models/checkpoints/<task>/` | F-01 | S | Uses `get_checkpoint_path()` from `src/utils/paths.py` |
| F-03 | Create `src/training/__init__.py` and package structure | — | S | Export public API |
| F-04 | Script `scripts/inspect_lora_modules.py`: load codegen-350M, print attention module names, confirm trainable param count with test `LoraConfig` | F-01 | S | **Blocking pre-flight** for F-09 |
| F-05 | Update `.env.example` with `MODEL_ADAPTER` and document adapter dir layout | F-02 | S | |

---

## Stage 2 — SFT Dataset Builder

| ID | Task | Depends on | Complexity | Notes |
|----|------|------------|------------|-------|
| S-01 | `src/training/tasks.py`: `TaskType` enum (`text2sql`, `sql2nosql`, `nosql2doc`); column maps; response template strings | F-03 | S | |
| S-02 | `src/training/filters.py`: `filter_tend_rows(df, overall_correct=True)`; length skip helpers | S-01 | S | Log skip reasons |
| S-03 | `src/training/prompt_factory.py`: map task → existing `PromptBuilder.build(...)` with correct column wiring | S-01 | M | Must match generator call signatures exactly |
| S-04 | `src/training/tend_dataset.py`: `build_sft_dataset(csv_path, task, config) → Dataset` with `text = prompt + target` | S-02, S-03 | M | Apply prompt truncation (left, ≤1792 tokens) |
| S-05 | `src/training/token_stats.py`: log dataset stats (n rows, avg prompt/target tokens, skipped) | S-04 | S | Called at train start |
| S-06 | `tests/training/test_prompt_parity.py`: for each task, compare dataset prompt vs `SQLGenerator`/`NoSQLGenerator`/`DocumentationGenerator` prompt on 3 fixture rows | S-03 | M | **Critical correctness gate** |
| S-07 | `tests/training/test_dataset_filters.py`: verify filter + length skip behaviour | S-02, S-04 | S | |

---

## Stage 3 — LoRA Trainer

| ID | Task | Depends on | Complexity | Notes |
|----|------|------------|------------|-------|
| T-01 | `src/training/lora_config.py`: `build_lora_config(config) → LoraConfig` with `task_type=CAUSAL_LM` | F-04 | S | Use verified target_modules |
| T-02 | `src/training/collator.py`: wrap TRL `DataCollatorForCompletionOnlyLM` with per-task response template | S-01, T-01 | M | |
| T-03 | `src/training/lora_trainer.py`: `train_lora(task, train_csv, eval_csv, output_dir, config)` orchestrating model load, peft wrap, SFTTrainer, save | T-01, T-02, S-04 | L | Call `set_seeds()`; MLflow logging |
| T-04 | `src/training/mlflow_utils.py`: log hyperparams, adapter path, train/eval metrics | T-03 | S | Reuse existing tracker patterns |
| T-05 | `scripts/train_lora.py` CLI: `--task`, `--train-csv`, `--eval-csv`, `--output-dir`, `--max-samples`, `--device`, `--config` | T-03 | M | Default `--output-dir` → `models/checkpoints/<task>/` via `get_checkpoint_path()` |
| T-06 | Overfit smoke test: `tests/training/test_overfit_smoke.py` — 5 rows, 3 epochs, assert loss decreases and adapter files exist | T-03 | M | Mark `@pytest.mark.slow` |
| T-07 | Verify adapter output: `adapter_config.json`, `adapter_model.safetensors`, optional `training_args.bin` | T-03 | S | |

---

## Stage 4 — Adapter-Aware Loading

| ID | Task | Depends on | Complexity | Notes |
|----|------|------------|------------|-------|
| L-01 | Add `is_adapter_dir(path)` helper: check for `adapter_config.json` | — | S | |
| L-02 | Extend `resolve_model_path()` / new `resolve_adapter_path(task)` in `model_loader.py` | L-01, F-02 | M | Do not break existing full-checkpoint path |
| L-03 | Extend `CodeGenModel.load()`: if adapter dir set, `PeftModel.from_pretrained(base, adapter_dir)` | L-02, T-07 | M | Base always from `models/base/` |
| L-04 | Extend `load_model(adapter=..., task=...)` signature; wire config + `MODEL_ADAPTER` env | L-03 | S | |
| L-05 | `tests/training/test_adapter_load.py`: load each task adapter, run one `generate()` call | L-03, T-07 | M | |
| L-06 | Document loading in code docstrings; no README change unless requested | L-04 | S | |

---

## Stage 5 — Full Training Runs

| ID | Task | Depends on | Complexity | Notes |
|----|------|------------|------------|-------|
| R-01 | Re-run baseline eval on full validation set (codegen-350M, no adapter) → `results/spider_codegen-350M-multi_<ts>/` | D-02 | L | Wall-clock; establishes fair comparison |
| R-02 | Train text2sql adapter: `python scripts/train_lora.py --task text2sql ...` | T-05, D-02, R-01 | XL | |
| R-03 | Train sql2nosql adapter | T-05, D-02 | XL | Can parallelize on separate machines |
| R-04 | Train nosql2doc adapter | T-05, D-02 | XL | Most data-dependent on doc column |
| R-05 | Save training logs + MLflow run IDs alongside each adapter dir (`run_metadata.json`) | R-02–R-04 | S | |

---

## Stage 6 — Evaluation Integration

| ID | Task | Depends on | Complexity | Notes |
|----|------|------------|------------|-------|
| E-01 | Extend `BenchmarkRunner` or eval script to accept per-task adapter (load adapter before each task's generator) | L-04 | M | Minimal change: inject `CodeGenModel` with adapter |
| E-02 | Add `--adapter` / `--task` flags to `scripts/run_baseline_eval.py` | E-01 | S | |
| E-03 | Run eval for each trained adapter on frozen validation CSV | R-02–R-04, E-02 | L | |
| E-04 | Produce comparison table: baseline vs LoRA `qwen_correct_rate` per task | E-03, R-01 | S | Write to `ai-workflow/validation/` during validation phase |
| E-05 | Log all eval runs to MLflow with tags: `run_type=lora`, `task=`, `adapter_path=` | E-03 | S | |

---

## Dependency Graph (summary)

```
D-01 → D-02 → S-04 → T-03 → T-07 → L-03 → R-02..R-04 → E-03
F-01 → F-04 → T-01
S-03 → S-06 (prompt parity gate)
T-06 (overfit gate before R-02)
R-01 (baseline before LoRA comparison)
```

---

## Critical Path

1. **D-01** (data) and **F-04** (module names) can run in parallel.
2. **S-06** (prompt parity) must pass before **T-03**.
3. **T-06** (overfit smoke) must pass before **R-02**.
4. **R-01** (full baseline) should complete before **E-04** (comparison).

---

## Estimated Total Effort (implementation only, excluding training wall-clock)

| Stage | Effort |
|-------|--------|
| 0 Data | 0.5 day setup + overnight generation |
| 1 Foundation | 0.5 day |
| 2 Dataset | 1 day |
| 3 Trainer | 1.5 days |
| 4 Loading | 0.5 day |
| 5 Training runs | 1–3 days wall-clock (hardware dependent) |
| 6 Eval | 0.5 day |
| **Total code** | **~4–5 dev days** |
