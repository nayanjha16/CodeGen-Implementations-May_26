# Dependency Analysis — LoRA Fine-Tuning

> **Feature:** `lora-finetuning`  
> **Date:** 2026-06-21

---

## 1. Cross-Module Dependencies

### New package: `src/training/`

```
src/training/
├── __init__.py
├── tasks.py              → (no src deps)
├── filters.py            → pandas
├── prompt_factory.py     → src.text2sql.prompt_builder
│                         → src.sql2nosql.prompt_builder
│                         → src.documentation.prompt_builder
├── tend_dataset.py       → tasks, filters, prompt_factory, transformers Dataset
├── token_stats.py        → tend_dataset
├── lora_config.py        → peft, src.utils.config
├── collator.py           → trl, tasks
├── lora_trainer.py       → lora_config, collator, tend_dataset
│                         → src.models.model_loader (base model load)
│                         → src.utils.seeds, src.utils.device
│                         → trl.SFTTrainer, peft
├── mlflow_utils.py       → src.evaluation.mlflow_tracker (optional reuse)
└── (no imports from src.evaluation.benchmark — eval stays downstream)
```

### Modified modules

| Module | Change | Depends on |
|--------|--------|------------|
| `src/models/model_loader.py` | PEFT adapter load path | `peft.PeftModel`, existing base load |
| `src/utils/config.py` | Training/lora config helpers | `configs/default.yaml` |
| `configs/default.yaml` | `training:` + `lora:` blocks | research decisions |
| `scripts/train_lora.py` | New CLI | `src/training/lora_trainer` |
| `scripts/run_baseline_eval.py` | `--adapter` flag | `load_model(adapter=...)` |
| `src/evaluation/benchmark.py` | Optional: inject adapter-aware model per task | `model_loader` |

### Unchanged (reuse only)

| Module | Role in training pipeline |
|--------|---------------------------|
| `src/text2sql/prompt_builder.py` | Train + eval prompt for text2sql |
| `src/sql2nosql/prompt_builder.py` | Train + eval prompt for sql2nosql |
| `src/documentation/prompt_builder.py` | Train + eval prompt for nosql2doc |
| `src/evaluation/benchmark.py` | Post-training eval |
| `src/evaluation/qwen_evaluator.py` | Primary success metric |
| `src/utils/seeds.py` | Reproducibility |
| `src/utils/device.py` | cuda > mps > cpu |
| `TEND/*` | Dataset generation only (Stage 0) |

---

## 2. External Dependencies

| Package | Version | Purpose | Required |
|---------|---------|---------|----------|
| `torch` | ≥2.0 | Training + inference | Yes |
| `transformers` | ≥4.36 | Model, tokenizer, Trainer args | Yes |
| `accelerate` | ≥0.25 | Device placement | Yes |
| `peft` | ≥0.11 | LoRA adapters | Yes |
| `trl` | ≥0.9 | SFTTrainer, completion collator | Yes |
| `datasets` | ≥2.16 | HuggingFace Dataset | Yes |
| `pandas` | ≥2.1 | TEND CSV loading | Yes |
| `mlflow` | ≥2.9 | Experiment tracking | Yes |
| `bitsandbytes` | — | QLoRA | **No** (explicitly excluded) |

All required packages are already listed in `requirements.txt`.

---

## 3. Data Dependencies

```
Spider (cached under data/spider/)
    │
    ▼
TEND/build_tend_dataset.py  +  scripts/run_all_tend.py
    │
    ├── src/sql2nosql/translator.py        (nosql_query targets)
    ├── src/utils/schema_conversion.py     (nosql_schema)
    ├── TEND/qwen_doc_generator.py         (documentation targets)
    └── TEND/qwen_evaluator.py             (overall_correct filter)
    │
    ▼
data/TEND/spider_{train,validation}_*.csv
    │
    ▼
src/training/tend_dataset.py  →  SFT Dataset
    │
    ▼
models/checkpoints/{text2sql|sql2nosql|nosql2doc}/
    │
    ▼
src/evaluation/benchmark.py  →  results/ + mlflow.db
```

### Column dependency matrix

| Column | Produced by | Consumed by task |
|--------|-------------|------------------|
| `question`, `sql_schema` | Spider | text2sql |
| `sql_query` | Spider | text2sql (target), sql2nosql (input) |
| `nosql_schema` | schema_conversion | sql2nosql, nosql2doc |
| `nosql_query` | SQLToNoSQLTranslator | sql2nosql (target), nosql2doc (input) |
| `documentation` | Qwen doc generator | nosql2doc (target) |
| `overall_correct` | Qwen evaluator | training filter (all tasks) |

---

## 4. Ordering Constraints

Hard ordering (must be sequential):

1. **TEND CSV exists** before dataset builder runs.
2. **Prompt builders stable** before dataset builder (no train/eval drift).
3. **Base model cached** (`models/base/Salesforce--codegen-350M-multi/`) before any training or adapter load.
4. **LoRA module names verified** before first real training run.
5. **Overfit smoke passes** before full training.
6. **Adapter saved** before adapter-aware load test.
7. **Full baseline eval** before claiming LoRA lift.

Parallelizable:

- M0 data generation and M1 config/scaffold (independent).
- R-02 / R-03 / R-04 adapter training on separate machines.
- Unit tests for filters vs prompt parity (after S-02 / S-03 respectively).

---

## 5. Runtime / Hardware Dependencies

| Backend | Training | Inference | Notes |
|---------|----------|-----------|-------|
| CUDA | Supported | Supported | Fastest; may use larger effective batch |
| MPS (Apple) | Supported (fp32) | Supported | Primary dev host; slower training |
| CPU | Supported (fp32) | Supported | Fallback; reduce batch size |

**No hard CUDA dependency.** Do not import `bitsandbytes`.

Known MPS caveats:

- Some ops slower in fp32 — acceptable for 350M model.
- If OOM: lower `per_device_train_batch_size`, raise `gradient_accumulation_steps`.

---

## 6. Config / Environment Dependencies

| Variable / key | Source | Used by |
|----------------|--------|---------|
| `MODEL_NAME` | `.env` | Base model selection (default codegen-350M-multi) |
| `MODELS_BASE_DIR` | `.env` | Base model cache |
| `MODELS_CHECKPOINTS_DIR` | `.env` | Adapter output root (**must be `models/checkpoints/`**) |
| `MODEL_ADAPTER` | `.env` (new) | Eval: which adapter to load |
| `MODEL_CHECKPOINT` | `.env` | Existing full-model path (unchanged) |
| `training.*` | `configs/default.yaml` | Trainer hyperparameters |
| `lora.*` | `configs/default.yaml` | LoRA rank, alpha, target_modules |
| `seeds.*` | `configs/default.yaml` | Reproducibility |

---

## 7. Integration Contracts

### Training CLI contract

```bash
python scripts/train_lora.py \
  --task {text2sql|sql2nosql|nosql2doc} \
  --train-csv PATH \
  --eval-csv PATH \
  --output-dir PATH \
  [--max-samples N] \
  [--device auto|cuda|mps|cpu] \
  [--config configs/default.yaml]
```

**Output:** adapter dir under `models/checkpoints/<task>/` with `adapter_config.json`,
`adapter_model.safetensors`, `run_metadata.json`. If `--output-dir` is omitted, defaults to
`get_checkpoint_path(<task>)` → `models/checkpoints/<task>/`.

### Model loader contract (extended)

```python
model = load_model(config=config, adapter="text2sql")
# or
model = load_model(config=config, adapter_path=get_checkpoint_path("text2sql"))
# resolves to models/checkpoints/text2sql/
```

**Behaviour:**

- If `adapter_path` contains `adapter_config.json` → wrap base with `PeftModel`.
- If `checkpoint` contains full `config.json` → existing behaviour unchanged.
- Base weights always loaded from `models/base/`, never modified.

### SFT dataset record contract

Each HuggingFace dataset row:

```python
{
    "text": f"{prompt}{target}",       # single string for SFTTrainer
    "prompt": prompt,                  # metadata for debugging
    "target": target,
    "task": "text2sql",
    "db_id": "...",
}
```

---

## 8. Circular Dependency Check

**No circular imports introduced.**

- `src/training` imports prompt builders (leaf modules).
- `src/training` imports `model_loader` for base load only (not adapters during train — uses transformers directly + peft).
- `model_loader` does **not** import `src/training`.
- `benchmark` imports generators → `model_loader`; optional adapter param stays at script level.

---

## 9. Artifact Dependencies

| Artifact | Produced by | Consumed by | Git tracked? |
|----------|-------------|-------------|--------------|
| TEND CSV | `run_all_tend.py` | `tend_dataset.py`, eval | Optional (large) |
| `manifest.json` | Stage 0 | train/eval scripts | Yes |
| Base model | HF cache / `ensure_model_cached` | train + infer | No (`.gitignore`) |
| LoRA adapter | `train_lora.py` | `load_model(adapter=)` | No (`.gitignore`) |
| `results/` metrics | eval scripts | validation report | Optional |
| `mlflow.db` | train + eval | comparison | Optional |
