# Presentation Guide

Slide outline and talking points for the capstone defense.

---

## 1. Recommended Slide Deck (~15 minutes)

### Slide 1: Title

- **CodeGen Fine-Tuning with PEFT & LoRA**
- Your name, program, date
- Base model: `codegen-350M-multi` | Method: LoRA (PEFT) — one adapter per task

### Slide 2: Problem Statement

- Developers work across SQL and NoSQL databases
- Three sequential tasks: NL→SQL, SQL→MongoDB, Query→Documentation
- Full fine-tuning of large models is expensive; small models need PEFT

### Slide 3: Objectives

- Build reproducible 3-task LoRA pipeline
- Baseline evaluation on fixed benchmark
- LoRA fine-tuning per task with PEFT
- Compare baseline vs fine-tuned with automated + semantic metrics

### Slide 4: System Architecture (use diagram)

Copy from [02-system-architecture.md](02-system-architecture.md) —  **Section 3 (Three-Task Pipeline)**

### Slide 5: Three Tasks


| Task      | Input              | Output        |
| --------- | ------------------ | ------------- |
| Text2SQL  | Question + schema  | SQL           |
| SQL2NoSQL | Gold SQL + schemas | MongoDB query |
| NoSQL2Doc | Gold MongoDB query | Documentation |


Emphasize: **independent evaluation** — gold inputs, not chained predictions

### Slide 6: Dataset

- TEND (Spider + BIRD): ~10,697 train, ~1,625 test
- Frozen 50-example gold validation for smoke-run benchmark
- Diagram from [04-data-and-datasets.md](04-data-and-datasets.md) Section 3

### Slide 7: Training Methodology

- LoRA (PEFT): r=16, frozen base, ~few MB per adapter
- TRL SFTTrainer, completion-only loss
- Prompt parity: same prompts at train and inference
- Diagram from [02-system-architecture.md](02-system-architecture.md) Section 4

### Slide 8: Evaluation Methodology

- 8 automated metrics + Ollama semantic judge
- Dual metric layers: fast deterministic + semantic
- Diagram from [02-system-architecture.md](02-system-architecture.md) Section 5

### Slide 9: Validation & Testing Strategy

- Unit tests → training smoke → adapter verify → benchmark eval
- Table from [03-methodology.md](03-methodology.md) Section 6

### Slide 10: Baseline vs LoRA v1 Comparison

Source: [docs/lora-v1-vs-baseline-comparison.md](../lora-v1-vs-baseline-comparison.md)

**Context:** Smoke run — 50 training samples, 10 epochs; evaluated on 50-example Spider gold validation set.


| Task              | Key metric             | Baseline | LoRA v1   | Change    |
| ----------------- | ---------------------- | -------- | --------- | --------- |
| **Text2SQL**      | Judge correct rate     | 4%       | **14%**   | **+250%** |
| **Text2SQL**      | Syntax validity        | 98%      | **100%**  | +2 pp     |
| **SQL2NoSQL**     | Syntax validity        | 26%      | **98%**   | +72 pp    |
| **SQL2NoSQL**     | Structural equivalence | 44%      | **76%**   | +32 pp    |
| **Documentation** | CodeBLEU               | 0.030    | **0.244** | +705%     |
| **Documentation** | Syntax validity        | 28%      | **76%**   | +48 pp    |


**Talking points:**

- LoRA v1 improves **every task** on similarity and validity metrics
- Clearest win: **Text2SQL judge accuracy** (4% → 14%, 3.5×)
- SQL2NoSQL and documentation: large output-quality gains; judge scores flat (8% / 0%)
- Execution accuracy and exact match still 0% — expected at smoke scale without execution DBs
- **Takeaway:** Even 50 samples × 10 epochs shows meaningful PEFT gains over unfine-tuned baseline

### Slide 11: Key Findings & Limitations

- LoRA helps even at smoke scale (50 samples)
- Syntax validity dramatically improved for sql2nosql and documentation
- Execution accuracy 0% (no bundled DBs in this repo)
- Judge scores lag automated metrics for documentation and sql2nosql

### Slide 12: Future Work

Source: [04-data-and-datasets.md](04-data-and-datasets.md) Section 4, TEND project (`/Volumes/Work/TEND`)

**1. Execution-verified gold datasets (TEND project)**

- Generate bronze rows: SQL DDL → MongoDB schema → query candidates → LLM judge
- **Execute** SQL and MongoDB queries against live databases; keep rows where results match
- Filter bronze → **silver** (execution-verified) → **gold** (sampled validation set)
- This gold data feeds training and validation for the next project phase

**2. Replace LLM judge with query execution**

- Today: Ollama semantic judge scores predicted SQL/MongoDB/docs (`judge_correct_rate`)
- Future: execute generated queries against live PostgreSQL/MongoDB and compare result sets — same approach as TEND (`in-progress`)
- More objective than LLM judging; aligns eval with how gold data is verified

**3. Next step: full-scale training and validation**

- Train all three LoRA adapters on complete TEND train split (~10,697 rows)
- Validate on TEND test split (~1,625 rows) and refreshed gold validation sets
- Re-run baseline vs LoRA comparison at full scale with execution-based metrics

### Slide 13: Q&A

---

## 2. Anticipated Questions & Answers

### "Why LoRA instead of full fine-tuning?"

LoRA trains only ~0.1–1% of parameters. Adapters are a few MB each, swappable per task, and the base model stays frozen — reducing overfitting risk and storage.

### "Why evaluate tasks independently instead of chaining?"

Chaining would confound errors — a bad SQL prediction would ruin sql2nosql metrics. Independent evaluation with gold inputs isolates each task's capability.

### "Why only 50 benchmark examples?"

Speed and reproducibility for the smoke run. The frozen set enables fair before/after comparison. Full TEND test (~1,625 rows) is available via `--full-split`.

### "Why is execution accuracy 0%?"

Spider SQLite database files are not bundled with the evaluation set. The TEND companion project executes queries against live PostgreSQL/MongoDB to build execution-verified silver and gold datasets.

### "Why is the documentation judge still 0%?"

The Ollama LLM judge applies strict semantic criteria and often lags automated metrics. This is an interim approach — the plan is to replace LLM judging with query execution validation (same as TEND): run generated queries and compare result sets.

### "How do you ensure training prompts match inference?"

Unit test `test_prompt_parity.py` verifies that `build_training_prompt()` produces identical strings to runtime `PromptBuilder.build()`.

### "Can this run on a Mac?"

Yes. Device auto-resolution selects MPS (Apple GPU). Training takes ~10–15 hours per task on MPS; smoke runs with 50 samples finish in minutes.

### "What would you do with more time?"

Build execution-verified gold data via the TEND pipeline, replace the LLM judge with query execution for eval, then run full-scale LoRA training and validation on the complete ~10,697-row train split.

---

## 3. Poster Layout (Alternative Format)

If presenting as a poster instead of slides:

```
┌─────────────────────────────────────────────────────────┐
│  TITLE + AUTHORS                                        │
├──────────────┬──────────────────────────────────────────┤
│  PROBLEM     │  ARCHITECTURE DIAGRAM                    │
│  & OBJECTIVES│  (Section 3 from architecture doc)     │
├──────────────┼──────────────────────────────────────────┤
│  METHODOLOGY │  LoRA v1 vs BASELINE TABLE               │
│  LoRA, data, │  (from lora-v1-vs-baseline-comparison)   │
│  metrics     │                                          │
├──────────────┴──────────────────────────────────────────┤
│  GITHUB LINK                 │  FUTURE WORK (TEND gold) │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Files to Have Open During Defense


| File                                      | Why                          |
| ----------------------------------------- | ---------------------------- |
| `docs/capstone/02-system-architecture.md` | Architecture diagrams        |
| `docs/lora-v1-vs-baseline-comparison.md`  | Smoke-run comparison numbers |
| `results/.../metrics.json`                | Numbers for Q&A              |
| `results/.../text2sql_details.csv`        | Example predictions          |
| `configs/default.yaml`                    | Hyperparameters              |
| `tests/training/test_prompt_parity.py`    | Reproducibility evidence     |


---

## 5. Timing Guide


| Section                                 | Duration    |
| --------------------------------------- | ----------- |
| Introduction + problem                  | 2 min       |
| Architecture + methodology              | 5 min       |
| LoRA v1 vs baseline results             | 3 min       |
| Future work (TEND gold + full training) | 2 min       |
| Q&A                                     | 5–10 min    |
| **Total**                               | **~17 min** |


