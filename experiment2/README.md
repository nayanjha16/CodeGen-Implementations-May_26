# Natural Language to Database Query Translation

Fine-tuning small language models to translate plain-English questions into SQL and MongoDB queries, with Schema Pruning RAG and Teacher-Student Knowledge Distillation.

**Group 52 Capstone Project — PG Certification in AI & ML (TalentSprint | IIIT Hyderabad)**

> For full design details, dataset analysis, prompt formats, and configuration reference see [`Updated_plan_v2.md`](Updated_plan_v2.md).

---

## Overview

This project trains a small language model to perform three database query translation tasks simultaneously:

| Task | Input | Output | Dataset |
|---|---|---|---|
| Text → SQL | Natural language question + schema | SQL query | Spider |
| SQL → NoSQL | SQL query + schema | MongoDB MQL | DocSpider |
| Text → NoSQL | Natural language question + schema | MongoDB MQL | DocSpider |

A single LoRA adapter handles all three tasks — task identity is embedded in a prompt tag (`[Task: NL-to-SQL]`, `[Task: SQL-to-MQL]`, `[Task: NL-to-MQL]`).

---

## Datasets

| Dataset | Split | Queries | Databases | Evaluation |
|---|---|---|---|---|
| Spider | Train / Dev | 7,000 / 1,034 | 166 | Spider exact-match evaluator |
| DocSpider | Train / Dev | 4,043 / 620 | 159 | MQL execution against live MongoDB |

Each DocSpider entry produces two training samples (SQL-to-NoSQL and Text-to-NoSQL), giving a total of ~21,000 training samples per run.

**Schema noise:** Across both dev sets, 67% of schema tables per query are irrelevant (3 out of avg 4.5 tables). Schema Pruning RAG (see below) addresses this directly.

---

## Model

Primary model: `Salesforce/codegen-350M-multi`

| Property | Value |
|---|---|
| Architecture | Decoder-only Transformer (causal LM) |
| Fine-tuning | LoRA via Hugging Face `peft` |
| LoRA rank (r) | 16 |
| LoRA alpha | 32 |
| Trainable parameters | ~5.2M (1.45% of 357M total) |
| Max context window | 2,048 tokens |

Training hyperparameters (from `src/config.py`):

| Setting | Value |
|---|---|
| Epochs | 7 |
| Effective batch size | 16 (batch 1 × grad accum 16) |
| Learning rate | 2e-4 |
| Checkpoint selection | Best `eval_exact_match` on 5% held-out split |
| Inference | Beam search, 4 beams, max 150 new tokens |

---

## Key Techniques

### 1. LoRA Fine-Tuning
Base model weights are frozen. LoRA injects small trainable rank-decomposition matrices into the attention and MLP layers. Only ~1.45% of parameters are updated, making training feasible on a single GPU.

### 2. Schema Pruning RAG
Full database schemas contain ~67% irrelevant tables per query. Before building each prompt, only the most relevant tables are kept:

| Task | Pruning method |
|---|---|
| SQL → NoSQL | Parse `FROM`/`JOIN` from the input SQL (deterministic) |
| Text → SQL | BGE-small cosine similarity + FK-neighbor expansion, top-3 tables |
| Text → NoSQL | BGE-small cosine similarity, top-3 collections |

Table embeddings are pre-built once (`scripts/build_retrieval_index.py --task schema`, ~5 sec) and reused at every training and inference step. Applied identically during training and inference — no mismatch.

### 3. Teacher-Student Knowledge Distillation
A larger teacher model reviews failed student predictions and writes a one-sentence diagnosis explaining why each query was wrong. The student retrains on these annotated failures — learning the reasoning, not just the correct answer.

```
Pass 1 training → Pass 1 inference → Extract failures
    → Teacher annotation → Pass 2 training → Pass 2 inference → Compare
```

---

## Results — CodeGen-350M Text-to-SQL

All experiments evaluated on Spider dev set (1,034 queries) using the official Spider exact-match evaluator.

### Progression of experiments

| Experiment | Easy | Medium | Hard | Extra | **All** |
|---|---|---|---|---|---|
| Zero-shot (no training) | 17.3% | 1.1% | 0.0% | 0.0% | **4.6%** |
| LoRA fine-tuning | 44.8% | 19.5% | 10.9% | 3.0% | **21.5%** |
| LoRA + RAG reference examples | 38.7% | 21.7% | 16.2% | 11.4% | **23.2%** |
| **LoRA + RAG schema pruning** | **54.8%** | **28.5%** | **20.1%** | **14.5%** | **31.1%** |

Schema pruning added +9.6 points over plain LoRA — the largest single improvement in the CodeGen-350M experiments.

Full evaluation reports: `FinalResults/codegen/Text2SQL/`

---

## Additional Models

Two further models were evaluated to explore whether architecture and scale affect results.

### CodeT5-250M — Transfer Learning (last 3 layers unfrozen)

Despite having fewer parameters than CodeGen-350M, CodeT5's encoder-decoder architecture is better suited to translation tasks.

- Text-to-SQL exact match: **49.7%** vs CodeGen-350M's 31.1%

### Qwen2.5-Coder-1.5B — LoRA + Knowledge Distillation

A Qwen-14B teacher model annotated failed student predictions. The student retrained on teacher diagnoses across all three tasks. Results measured by execution accuracy (generated queries run against real databases — stricter than string match):

| Task | Without Teacher | With Teacher | Improvement |
|---|---|---|---|
| Text → SQL | 67.6% | **72.2%** | +4.6% |
| SQL → NoSQL | 77.4% | **81.1%** | +3.7% |
| Text → NoSQL | 63.7% | **65.8%** | +2.1% |

---

## How to Run

### Prerequisites

```bash
# Build schema pruning index (run once before first training)
python scripts/build_retrieval_index.py --task schema

# Build all indices (schema pruning + reference-example RAG)
python scripts/build_retrieval_index.py
```

### Full pipeline (all 7 stages)

```bash
python run_codegen.py
```

### Resume from a specific stage

```bash
python run_codegen.py --start_from inference     # skip Pass 1 training
python run_codegen.py --start_from teacher       # skip to teacher annotation
python run_codegen.py --start_from pass2         # skip to Pass 2 fine-tuning
python run_codegen.py --start_from pass2_infer   # skip to Pass 2 inference
python run_codegen.py --start_from compare       # skip to final comparison
```

### Quick options

```bash
python run_codegen.py --sanity      # 3-sample smoke test, teacher mocked
python run_codegen.py --skip_rag    # disable reference-example RAG (faster)
```

> `--skip_rag` disables reference-example RAG only. Schema pruning is always active.

### Teacher provider

```bash
# Default: Groq (set GROQ_API_KEY)
python generate_teacher_data.py

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
python generate_teacher_data.py --provider anthropic --model_id claude-haiku-4-5-20251001
```

---

## Pipeline Stage Reference

| # | Stage | Script | Output |
|---|---|---|---|
| 1 | Pass 1 training | `finetune_unified.py` | `models/codegen_pass1/` |
| 2 | Pass 1 inference | `run_multi_task_inference.py` ×3 | `outputs/codegen/pass1/*/predictions.json` |
| 3 | Extract failures | `extract_failures.py` | `*_failures.json` |
| 4 | Teacher annotation | `generate_teacher_data.py` | `*_augmented_train.json` |
| 5 | Pass 2 training | `finetune_unified.py` | `models/codegen_pass2/` |
| 6 | Pass 2 inference | `run_multi_task_inference.py` ×3 | `outputs/codegen/pass2/*/predictions*.json` |
| 7 | Compare results | `compare_results.py` | `outputs/comparison_report.txt` |

---

## Repository Layout

```
experiment2/
├── src/                        # Core library
│   ├── config.py               # All hyperparameters, paths, teacher config
│   ├── schema_pruner.py        # Per-query schema trimming (v2)
│   ├── prompt_builder.py       # Prompt construction for all 3 tasks
│   ├── retriever.py            # BM25 + dense hybrid retriever
│   ├── loader.py               # Dataset and schema loaders
│   └── ...
├── scripts/
│   └── build_retrieval_index.py
├── data/spider/                # Spider dataset
├── docspider/                  # DocSpider dataset
├── models/                     # LoRA checkpoints (gitignored)
├── outputs/                    # Predictions and reports (gitignored)
├── retrieval_index/            # Pre-built embeddings (gitignored)
├── logs/                       # Per-run log files (gitignored)
├── FinalResults/               # Archived evaluation reports
│   └── codegen/Text2SQL/       # CodeGen-350M results by experiment
├── run_codegen.py              # Pipeline orchestrator
├── finetune_unified.py         # Multi-task fine-tuning
├── run_multi_task_inference.py # Inference
├── extract_failures.py         # Failure mining
├── generate_teacher_data.py    # Teacher annotation
├── compare_results.py          # Pass 1 vs Pass 2 comparison
└── Updated_plan_v2.md          # Full design document
```
