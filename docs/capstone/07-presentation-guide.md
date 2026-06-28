# Presentation Guide

Slide outline, demo script, and talking points for the capstone defense.

---

## 1. Recommended Slide Deck (15–20 minutes)

### Slide 1: Title
- **CodeGen Studio: Interactive Database Querying Using Small Code Language Models**
- Your name, program, date
- Base model: codegen-350M-multi | Method: LoRA fine-tuning

### Slide 2: Problem Statement
- Developers work across SQL and NoSQL databases
- Three sequential tasks: NL→SQL, SQL→MongoDB, Query→Documentation
- Large models are expensive; small models need fine-tuning

### Slide 3: Objectives
- Build reproducible 3-task pipeline
- Baseline evaluation on fixed benchmark
- LoRA fine-tuning per task
- Compare automated + semantic metrics

### Slide 4: System Architecture (use diagram)
Copy from [02-system-architecture.md](02-system-architecture.md) — **Section 2 (Component Architecture)** or **Section 3 (Three-Task Pipeline)**

### Slide 5: Three Tasks
| Task | Input | Output |
|------|-------|--------|
| Text2SQL | Question + schema | SQL |
| SQL2NoSQL | Gold SQL + schemas | MongoDB query |
| NoSQL2Doc | Gold MongoDB query | Documentation |

Emphasize: **independent evaluation** — gold inputs, not chained predictions

### Slide 6: Dataset
- TEND (Spider + BIRD): ~10,697 train, ~1,625 test
- Frozen 50-example gold validation for benchmark
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

### Slide 10: Results — Text2SQL
- Judge: 4% → 14% (+250%)
- Syntax validity: 98% → 100%
- Chart from [05-results-and-analysis.md](05-results-and-analysis.md)

### Slide 11: Results — SQL2NoSQL & Documentation
- SQL2NoSQL syntax: 26% → 98%
- Documentation CodeBLEU: 0.03 → 0.24 (+705%)

### Slide 12: Key Findings & Limitations
- LoRA helps even at smoke scale (50 samples)
- Execution accuracy 0% (no bundled DBs)
- Full-scale training expected to improve further

### Slide 13: Demo (Live or Video)
See Section 2 below

### Slide 14: Future Work
- Full 10k training, execution accuracy, human eval, model comparison

### Slide 15: Q&A

---

## 2. Live Demo Script (5 minutes)

### Prerequisites
```bash
conda activate ai
export PYTHONPATH="$(pwd)"
# Ensure .env is configured
# Optional: start Ollama for judge
```

### Demo Option A: Quick Evaluation (Recommended)

```bash
# Show baseline eval on 5 samples (fast)
python scripts/run_baseline_eval.py --max-samples 5 --no-judge

# Show results
cat results/spider_gold_validation_*/metrics.json | python -m json.tool | head -40
```

**Talking points while running:**
- "This evaluates all three tasks on our frozen 50-example benchmark"
- "Each task uses gold inputs — we're measuring isolated task quality"
- "Output includes metrics.json and per-sample CSVs for error analysis"

### Demo Option B: Show LoRA vs Baseline

```bash
# If adapters exist
python scripts/run_baseline_eval.py --adapter-run v1 --max-samples 5 --no-judge

# Compare
echo "=== Baseline ===" && cat results/spider_gold_validation_codegen-350M-multi_2506_2029/metrics.json | python -m json.tool | grep -A2 "judge_correct"
echo "=== LoRA v1 ===" && cat results/spider_gold_validation_codegen-350M-multi_lora-v1_2506_2343/metrics.json | python -m json.tool | grep -A2 "judge_correct"
```

### Demo Option C: Show a Single Prediction

Open a detail CSV and walk through one row:

```bash
head -3 results/spider_gold_validation_*/text2sql_details.csv
```

Point out: `question`, `predicted_sql`, `ground_truth`, `judge_sql_correct`

### Demo Option D: Architecture Walkthrough (No GPU needed)

```bash
# Show project structure
ls src/
ls models/checkpoints/v1/ 2>/dev/null || echo "Adapters not trained yet"

# Run unit tests (fast)
python -m unittest tests.training.test_prompt_parity -v
```

---

## 3. Anticipated Questions & Answers

### "Why LoRA instead of full fine-tuning?"
LoRA trains only ~0.1–1% of parameters. Adapters are a few MB each, swappable per task, and the base model stays frozen — reducing overfitting risk and storage.

### "Why evaluate tasks independently instead of chaining?"
Chaining would confound errors — a bad SQL prediction would ruin sql2nosql metrics. Independent evaluation with gold inputs isolates each task's capability.

### "Why only 50 benchmark examples?"
Speed and reproducibility. The frozen set enables fair before/after comparison. Full TEND test (~1,625 rows) is available via `--full-split`.

### "Why is execution accuracy 0%?"
Spider SQLite database files are not bundled with the evaluation set. We validate SQL syntax but cannot execute against the original databases without additional setup.

### "Why is the documentation judge still 0%?"
Despite large metric gains (CodeBLEU +705%), the Ollama judge applies strict semantic criteria. With only 50 training samples, outputs may be structurally improved but not semantically equivalent to gold docs.

### "How do you ensure training prompts match inference?"
Unit test `test_prompt_parity.py` verifies that `build_training_prompt()` produces identical strings to runtime `PromptBuilder.build()`.

### "Can this run on a Mac?"
Yes. Device auto-resolution selects MPS (Apple GPU). Training takes ~10–15 hours per task on MPS; smoke runs with 50 samples finish in minutes.

### "What would you do with more time?"
Full-scale training on all 10,697 rows, bundle Spider SQLite DBs for execution accuracy, human evaluation on 20 stratified samples, and compare against Qwen2.5-Coder-0.5B.

---

## 4. Poster Layout (Alternative Format)

If presenting as a poster instead of slides:

```
┌─────────────────────────────────────────────────────────┐
│  TITLE + AUTHORS                                        │
├──────────────┬──────────────────────────────────────────┤
│  PROBLEM     │  ARCHITECTURE DIAGRAM                    │
│  & OBJECTIVES│  (Section 3 from architecture doc)     │
├──────────────┼──────────────────────────────────────────┤
│  METHODOLOGY │  RESULTS TABLE                           │
│  LoRA, data, │  Baseline vs LoRA bar charts           │
│  metrics     │                                          │
├──────────────┴──────────────────────────────────────────┤
│  DEMO QR CODE / GITHUB LINK  │  FUTURE WORK & LIMITS    │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Files to Have Open During Defense

| File | Why |
|------|-----|
| `docs/capstone/02-system-architecture.md` | Architecture diagrams |
| `results/.../metrics.json` | Numbers for Q&A |
| `results/.../text2sql_details.csv` | Example predictions |
| `configs/default.yaml` | Hyperparameters |
| `tests/training/test_prompt_parity.py` | Reproducibility evidence |

---

## 6. Timing Guide

| Section | Duration |
|---------|----------|
| Introduction + problem | 2 min |
| Architecture + methodology | 5 min |
| Results | 4 min |
| Live demo | 3 min |
| Limitations + future work | 2 min |
| Q&A | 5–10 min |
| **Total** | **~20 min** |
