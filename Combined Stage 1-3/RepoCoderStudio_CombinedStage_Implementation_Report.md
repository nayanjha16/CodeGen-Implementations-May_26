
# RepoCoder Studio — Combined Stage Implementation Report

**Multilingual Code Intelligence via Semantic Corpus Engineering + QLoRA Multitask Fine-Tuning**

IIT-H Capstone | Group 46 | Project 6: CodeGen | Spec Version 2.0

---

## How to read this report

The system is a **pipeline**: raw datasets go in one end, a fine-tuned multitask model comes out the other. Every chapter below corresponds to one stage of that pipeline, in the order it actually executes. Start with the diagram in Section 1 — everything else expands one box from it.

```
 ┌────────────────────┐   ┌──────────────────────┐   ┌───────────────────────┐
 │  1. Raw Datasets    │──▶│ 2. Corpus Engineering│──▶│ 3. Semantic & Structural│
 │  (XLCoST, CodeXGLUE)│   │  (schema + alignment) │   │     Validation          │
 └────────────────────┘   └──────────────────────┘   └───────────────────────┘
                                                                   │
                                                                   ▼
 ┌────────────────────┐   ┌──────────────────────┐   ┌───────────────────────┐
 │ 6. QLoRA Fine-Tuning│◀──│ 5. Prompt Contract +  │◀──│  4. Approved Corpus     │
 │  (frozen 4-bit base │   │   6-Task Dataset      │   │     (403 trusted rows)  │
 │   + trainable LoRA) │   │   Builder             │   │                       │
 └────────────────────┘   └──────────────────────┘   └───────────────────────┘
           │
           ▼
 ┌────────────────────┐   ┌──────────────────────┐
 │ 7. Task-Aware       │──▶│ 8. Baseline vs         │
 │    Evaluation       │   │  Fine-Tuned Results    │
 └────────────────────┘   └──────────────────────┘
```

---

## Executive Summary

RepoCoder Studio takes two public code datasets (XLCoST, CodeXGLUE), builds a **trusted, semantically-validated multilingual corpus** out of them, and uses that corpus to fine-tune a single small language model (Qwen2.5-Coder-0.5B-Instruct) to perform **six** software-engineering tasks at once: Python generation, Java generation, Python↔Java translation (both directions), and Python/Java → natural-language summarization.

The central engineering bet of the project is: **most of the effort and most of the improvement comes from the data pipeline, not the model.** The model is small (0.5B parameters) and only **0.88% of its weights are trained** (QLoRA). Everything else — validation, alignment, prompt design — exists to make sure the ~2,400 examples that small update sees are trustworthy.

**Headline results** (10-example evaluation subset per task, identical pipeline, only the model changed):

| Task | Metric | Baseline | Fine-Tuned | Change |
|---|---|---:|---:|---:|
| T1 NL → Python | Executable/Parse Success | 70% | **100%** | +30 pts |
| T2 NL → Java | Compile Success | 40% | **80%** | +40 pts |
| T3 Python → Java | CodeBLEU-lite | 0.815 | **0.940** | +0.125 |
| T4 Java → Python | CodeBLEU-lite | 0.812 | **0.925** | +0.113 |
| T5 Python → NL | SacreBLEU | 1.50 | **9.82** | +8.32 |
| T6 Java → NL | SacreBLEU | 1.62 | **9.59** | +7.97 |

No task regressed after fine-tuning — evidence that the balanced, round-robin multitask design avoided catastrophic forgetting across the six tasks.

---

# 1. Problem & Motivation

Public code datasets (XLCoST, CodeXGLUE, MBPP, HumanEval, etc.) are not directly trustworthy training data for a multilingual system:

- **No reliable cross-language linkage.** XLCoST's raw structure does not guarantee that "row 500 in the Python split" and "row 500 in the Java split" describe the same task — a naive positional join (tried in Stage 3) produced only ~100 valid pairs out of thousands.
- **No guarantee of syntactic validity.** Scraped snippets can be truncated, indentation-broken, or missing wrapper classes (Java).
- **No guarantee of semantic equivalence.** Two snippets can be syntactically fine individually but not actually implement the same algorithm.
- **Inconsistent task framing.** Different datasets phrase instructions differently, which destabilizes multitask fine-tuning if fed in raw.

**Consequence:** every downloaded row is treated as a **candidate**, not as trusted data, until it survives a validation pipeline (Section 3). Training only ever touches the **approved corpus**.

---

# 2. Corpus Engineering — From Raw Datasets to Candidates

### 2.1 Dataset sources

| Dataset | Role | Config |
|---|---|---|
| **XLCoST** (`codeparrot/xlcost-text-to-code`) | Mandatory primary corpus | `Python-program-level`, `Java-program-level` |
| **CodeXGLUE** (`google/code_x_glue_ct_code_to_text`) | Secondary evidence source for code→text rows | `python`, `java` (falls back to `code_search_net` if unavailable) |

Earlier candidates — **CodeAlpaca, APPS, TransCoder** — were evaluated during Stages 2–3 and explicitly **removed** from the frozen design (see Section 9.4 for why).

### 2.2 The alignment problem, and how it's solved

Because NL, Python, and Java records arrive as **separate unlinked pools**, the system needs to figure out which triples belong together. Two strategies, chosen automatically per situation:

```
                    ┌───────────────────────────────┐
                    │ Same dataset, same split?      │
                    └───────────────────────────────┘
                       │ yes                  │ no (cross-dataset)
                       ▼                       ▼
        ┌───────────────────────┐   ┌─────────────────────────────┐
        │ Normalized-title match │   │ Embedding-based alignment    │
        │ (exact key match on    │   │ (sentence-transformers +     │
        │  normalized NL text)   │   │  cosine similarity)          │
        │ confidence = 1.0       │   │ confidence = avg(sim) + bonus│
        └───────────────────────┘   └─────────────────────────────┘
```

**Embedding-based alignment**, in detail:
1. Embed every NL / Python-doc / Java-doc text with `sentence-transformers/all-MiniLM-L6-v2` (pretrained, off-the-shelf — not trained by this project).
2. Build cosine-similarity matrices `NL↔Python` and `NL↔Java` via one normalized matrix multiply.
3. For each NL record, take its top-`10` Python and top-`10` Java candidates by similarity.
4. Score every (Python, Java) candidate pair: `confidence = min(1.0, (py_sim + java_sim)/2 + structural_bonus)`, where `structural_bonus` (+0.10) rewards pairs whose AST/Tree-sitter function counts agree.
5. Accept only the best-scoring pair per NL record, and only if `confidence ≥ 0.50`.

If `sentence-transformers` is unavailable in a given Colab session, the system falls back to exact normalized-text matching rather than failing outright.

### 2.3 Deduplication

Before candidates are frozen, `DuplicateDetector` removes both **exact-text duplicates** and **structural duplicates** (same normalized token signature) across all source datasets — this runs once, here, at corpus-construction time, not repeatedly during validation.

### 2.4 Result of this stage

**432 candidate rows** — schema-normalized, deduplicated (Python/Java/NL) triples, not yet trusted — carried forward into validation.

---

# 3. Semantic & Structural Validation — From Candidates to Approved Corpus

Every candidate row must pass a layered pipeline before being trusted. Structural checks run first because semantic analysis on invalid code is meaningless.

```
Candidate Row
     │
     ▼
┌───────────────────────┐  fail ──▶ ┌──────────────────────────┐
│ 1. NL validation        │          │ Repair loop (≤3 attempts) │──▶ still failing after
│  length, no code-leakage│◀─────────│  see Section 3.4           │    3 attempts: REJECT
└───────────────────────┘  pass      └──────────────────────────┘    "nl_validation_failed"
     │
     ▼
┌───────────────────────┐  fail ──▶  same repair loop, component="python" ──▶ REJECT
│ 2. Python validation     │          "python_validation_failed" if still failing after 3
│  ast.parse()             │
└───────────────────────┘  pass
     │
     ▼
┌───────────────────────┐  fail ──▶  same repair loop, component="java" ──▶ REJECT
│ 3. Java validation       │          "java_validation_failed" if still failing after 3
│  javac compile +         │
│  Tree-sitter structural  │
│  analysis                │
└───────────────────────┘  pass
     │
     ▼
┌───────────────────────┐  FAIL (rare) ──▶ REJECT "execution_validation_failed"
│ 4. Trusted-test build +  │  NOT_FEASIBLE is *allowed* (config), so this
│    execution check        │  practically never rejects — see Section 3.6
└───────────────────────┘
     │
     ▼
┌───────────────────────┐
│ 5. CSR score computed     │  Jaccard similarity, Python-structure vs Java-structure
│    (supporting evidence,  │  recorded as metadata (`csr_above_threshold`) — does
│     not a rejection gate) │  NOT reject the row in the current frozen code
└───────────────────────┘
     │
     ▼
   Approved Corpus Row
```

Each of steps 1–3 is gated by the **same bounded repair loop** (Section 3.4) before a row is given up on — a failed NL/Python/Java check is not an immediate rejection, it's a trigger for up to 3 repair attempts.

### 3.1 Structural validation

- **Python:** `ast.parse()` — parse success/failure only (no execution).
- **Java:** actual `javac` compilation (10s timeout) — the strongest structural signal available since Java is statically typed.

### 3.2 Tree-sitter structural analysis

Compiler/parser success tells you code is *valid*; it says nothing about its *shape*. For Java, the pipeline additionally parses source with **Tree-sitter** (`tree-sitter` + `tree-sitter-java`, a real parser-generator library — not implemented in-house) to extract a concrete syntax tree, then walks it to build a normalized structural-token vocabulary (`CLASS`, `FUNCTION`, `IF`, `FOR`, `WHILE`, `NEW`, `BINOP`, …). Python gets the equivalent treatment for free via the stdlib `ast` module. If `tree-sitter-java` isn't installed in a given Colab runtime, a regex-based approximation is used instead so the pipeline never hard-fails — but this fallback is strictly weaker (no nesting/scope awareness).

### 3.3 Cross-language Semantic Consistency Ratio (CSR)

CSR is **not a novel algorithm** — it is the well-known **Jaccard similarity coefficient** applied to the structural token sets from Section 3.2:

```
CSR(A, B) = |tokens(A) ∩ tokens(B)| / |tokens(A) ∪ tokens(B)|
```

Used in **two different roles** across the project — this is the most commonly confused part of the pipeline, so both are spelled out explicitly:

| Where | Compares | Purpose |
|---|---|---|
| **Corpus validation** (this stage) | Python code vs. Java code of the *same aligned pair* | Recorded as supporting evidence (`csr_above_threshold` metadata flag) on every approved row — **not** currently a rejection gate. |
| **Model evaluation** (Section 6) | Reference code vs. model-generated code, *same language* | Structural fidelity score for how closely a prediction matches the reference. |

**Version note:** the config docstring for `min_csr_similarity` explicitly says *"CSR threshold relaxed — CSR is now supporting evidence, not a gate."* The on-disk `rejected_corpus.jsonl` from the frozen run does contain rows rejected with reason `csr_similarity_below_threshold` (e.g. CSR = 0.125–0.25) — those were produced by an earlier snapshot of the validation engine that did gate on CSR, before it was relaxed to non-gating metadata. The current source code (`validation_engine.py` v2.4) only ever rejects on `nl_validation_failed`, `python_validation_failed`, `java_validation_failed`, or `execution_validation_failed`.

### 3.4 Teacher-assisted repair & feedback loop

Each of the three gating checks (NL, Python, Java) shares one bounded repair mechanism, owned by `ValidationEngine` and executed by a separate `RepairEngine`:

```
   validation FAILS for component X (NL / Python / Java), attempt = 1
                       │
                       ▼
   ┌──────────────────────────────────────────────────────┐
   │  Build feedback = {component: X, reason, attempt}       │
   └──────────────────────────────────────────────────────┘
                       │
        ┌──────────────┴───────────────┐
        ▼                               ▼
  teacher repair ENABLED           teacher repair DISABLED
        │                               │
        ▼                               ▼
  TeacherEngine regenerates        deterministic fallback ladder
  component X, conditioned on      (progressively more aggressive
  the OTHER two already-valid      per attempt — e.g. dedent →
  modalities + the feedback         function-wrap → class-wrap)
        │                               │
        └──────────────┬───────────────┘
                       ▼
        Re-run the SAME deterministic validator
        (ast.parse / javac / NL length+leakage check)
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          PASS → continue    FAIL → attempt += 1 (max 3)
          pipeline                  → still failing → REJECT
```

Key design points:

- **The teacher is a separate, frozen instance of the same base model** (`Qwen2.5-Coder-0.5B-Instruct`), loaded independently from the student and run with greedy decoding (`do_sample=False`) for determinism. It is a repair *tool* used only during corpus construction — it is never fine-tuned, and its outputs never enter the corpus unchecked.
- **Teacher outputs are never trusted directly** (`teacher_engine.py` states this as an explicit design rule) — every regenerated NL/Python/Java fragment must re-pass the exact same deterministic validator used on raw candidates before it's accepted.
- **Cross-modality conditioning:** when repairing one modality, the teacher is given the *other two already-valid modalities* as context — e.g. `generate_python()` is prompted with the natural-language task and the Java reference, so a repaired Python implementation must remain consistent with the reference the row was aligned against, not just be "some valid Python."
- **Deterministic fallback ladder** (used when teacher repair is disabled, or as the design that inspired the teacher-enabled prompts): each of the 3 attempts escalates —

  | Attempt | Python | Java | Natural Language |
  |---|---|---|---|
  | 1 | dedent | ensure compilation unit | summarize from detected function name |
  | 2 | wrap in a function | force a `Solution` class | generic algorithm-description fallback |
  | 3 | wrap in a class | wrap in `Main` w/ diagnostics preserved | derive from Java class name |

- **Two teacher capabilities exist in code but are disabled in the frozen config**: `propose_tests()` (candidate unit-test generation) and completion-queue processing (`enable_teacher_test_generation=False`, `enable_teacher_completion_queue_processing=False`). This is directly why every approved row ends up `execution_status = NOT_FEASIBLE` in Section 3.6 — the test-proposal machinery exists but was never switched on for this run.

### 3.5 Validation funnel — actual numbers

```
  432 candidate rows
        │
        │  −29 rejected
        │   (nl / python / java validation failed after repair attempts,
        │    plus legacy csr-gated rejections from an earlier run — see 3.3)
        ▼
  403 approved rows  ──────────────▶  FROZEN APPROVED CORPUS
```

### 3.6 Why execution-based testing was excluded

The pipeline includes infrastructure for trusted execution tests (including the teacher's `propose_tests()` capability from Section 3.4), but after validation **0 of the 403 approved rows** had a reliable, safe generic test harness (`execution_status = NOT_FEASIBLE` for all — consistent with test-generation being disabled in the frozen config). Rather than fabricating tests to inflate metrics, the project explicitly excludes execution-based scoring from the frozen design and reports this as a known limitation (Section 9) rather than hiding it.

---

# 4. Prompt Contract v2.6 & the Six-Task Multitask Dataset

### 4.1 Why a formal prompt contract

Feeding six different task types into one model with ad-hoc, inconsistently-worded prompts causes task interference and unstable formatting. **Prompt Contract v2.6** standardizes every prompt into fixed fields: task token, role definition, objective, output contract, expected response header, constraints, and quality checks — so the model always knows which of the six tasks it's being asked to do and exactly what output shape is expected.

### 4.2 The six tasks

| ID | Task | Source → Target |
|---|---|---|
| T1 | NL → Python | Natural Language → Python |
| T2 | NL → Java | Natural Language → Java |
| T3 | Python → Java | Python → Java (translation) |
| T4 | Java → Python | Java → Python (translation) |
| T5 | Python → NL | Python → Natural Language (summarization) |
| T6 | Java → NL | Java → Natural Language (summarization) |

Every approved corpus row is expanded into **all six** task examples (same underlying Python/Java/NL triple, six different input→output framings), so 403 approved rows → 403 × 6 = 2,418 multitask examples.

### 4.3 Round-robin curriculum

Rather than grouping examples by task (which risks the model overfitting to whichever task it sees in long uninterrupted runs), examples are interleaved: `T1, T2, T3, T4, T5, T6, T1, T2, …`. This is the mechanism credited (Section 9.5) with the fact that **no task regressed** after multitask training.

### 4.4 Final dataset statistics

| Split | Examples |
|---|---:|
| Train | 1,776 |
| Validation | 342 |
| Test | 300 |
| **Total** | **2,418** |

Each of the 6 tasks contributes an equal share of every split — a deliberate balance to prevent task bias.

---

# 5. Model & QLoRA Fine-Tuning

### 5.1 Why QLoRA

Full fine-tuning of even a 0.5B model, plus optimizer state, does not comfortably fit alongside data loading and generation on a single Colab **T4 GPU (~15GB VRAM)**. QLoRA (Quantized Low-Rank Adaptation) solves this by freezing the base model in compressed 4-bit form and training only small "adapter" matrices injected into it.

```
┌──────────────────────────────┐
│ Qwen2.5-Coder-0.5B-Instruct    │   pretrained, general code model
└──────────────────────────────┘
              │
              ▼
┌──────────────────────────────┐
│ 4-bit NF4 quantization         │   bitsandbytes library (not custom)
│ (frozen — never updated)       │   ~4× memory reduction on base weights
└──────────────────────────────┘
              │
              ▼
┌──────────────────────────────┐
│ LoRA adapters                 │   small trainable low-rank matrices
│ (trainable — rank 8)           │   injected into attention + MLP layers
└──────────────────────────────┘
              │
              ▼
┌──────────────────────────────┐
│ Fine-tuned multitask model     │   one adapter, six task capabilities
└──────────────────────────────┘
```

### 5.2 Quantization details (`BitsAndBytesConfig`, via `bitsandbytes`)

| Setting | Value | What it does |
|---|---|---|
| `load_in_4bit` | `True` | Base weights stored in 4 bits instead of 16/32 |
| `bnb_4bit_quant_type` | `"nf4"` | NormalFloat4 — quantization scheme tuned for near-Gaussian weight distributions (from the QLoRA paper) |
| `bnb_4bit_compute_dtype` | `float16` | Matmuls de-quantize on the fly to fp16 for numerical stability |
| `bnb_4bit_use_double_quant` | `True` | Quantizes the quantization constants themselves for extra memory savings |

### 5.3 LoRA configuration (`peft` library)

| Setting | Value |
|---|---|
| Rank (`r`) | 8 |
| Alpha | 16 |
| Dropout | 0.05 |
| Target modules | `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj` (all attention + MLP projections) |
| Bias | none |

### 5.4 Training configuration (`TrainingArguments` + `trl.SFTTrainer`)

| Setting | Value |
|---|---|
| Epochs | 1 (demo) / 2 (full) |
| Batch size | 1 |
| Gradient accumulation | 8 (effective batch = 8) |
| Learning rate | 2e-4 |
| Warmup ratio | 0.03 |
| Max sequence length | 1,024 tokens |
| Max new tokens (generation) | 384 |
| Precision | fp16 + gradient checkpointing |
| Step-eval during training | **Disabled** (caused Colab CUDA OOM; evaluated separately post-training) |

### 5.5 Trained parameter footprint

| Metric | Value |
|---|---:|
| Total model parameters | 498,431,872 |
| Trainable (LoRA) parameters | 4,399,104 |
| **Trainable fraction** | **0.8826%** |

Training completed with stable, steadily decreasing loss and no oscillation, saved as adapter `RepoCoderStudio_CombinedStage_LoRA_v1_0`.

---

# 6. Evaluation Methodology

### 6.1 Principle

Baseline and fine-tuned models are evaluated with **exactly** the same dataset, prompts, and metric code — the model checkpoint is the only variable — so observed deltas can be attributed to fine-tuning rather than pipeline drift.

### 6.2 Task-aware metric selection

Different task types need different correctness notions; the evaluator switches metrics by target modality:

```
                     ┌───────────────────────────┐
                     │ What is the target?        │
                     └───────────────────────────┘
                    Python / Java  │        │  Natural Language
                                   ▼        ▼
            ┌─────────────────────────┐  ┌───────────────────────────┐
            │ • Parse (Python: ast)     │  │ • ROUGE-L                  │
            │ • Compile (Java: javac)   │  │ • SacreBLEU                 │
            │ • CodeBLEU (official, or  │  │ • Semantic similarity        │
            │   codebleu_lite fallback) │  │   (embedding cosine sim.)   │
            │ • CSR similarity           │  │                             │
            └─────────────────────────┘  └───────────────────────────┘
```

- **CodeBLEU:** tries the official `dvitel/codebleu` metric once; if it ever throws, permanently falls back to `codebleu_lite` (token-set F1) for the rest of the run — evaluation never blocks on a flaky third-party metric.
- **CSR similarity:** the same Jaccard-over-structural-tokens computation from Section 3.3, now comparing reference vs. predicted code in the same language.
- **Semantic similarity:** cosine similarity between `all-MiniLM-L6-v2` embeddings of reference vs. predicted text — used only for NL-target tasks.

### 6.3 Evaluation configuration

| Property | Value |
|---|---|
| Base model | Qwen2.5-Coder-0.5B-Instruct |
| Fine-tuned model | Base + LoRA adapter |
| Prompt version | `prompt_contract_v2.6` |
| Examples evaluated per task | 10 (demo config) |
| Tasks evaluated | 6 |

---

# 7. Results

### 7.1 Overall comparison

| Task | Baseline | Fine-Tuned | Δ |
|---|---:|---:|---:|
| T1 — NL → Python (primary success) | 70% | **100%** | +30 pts |
| T2 — NL → Java (compile success) | 40% | **80%** | +40 pts |
| T3 — Python → Java (compile success) | 50% | 50% | maintained |
| T4 — Java → Python (parse success) | 90% | 90% | maintained |
| T5 — Python → NL | weaker | markedly stronger | ✔ |
| T6 — Java → NL | weaker | markedly stronger | ✔ |

### 7.2 Task-by-task detail

**T1 — Natural Language → Python**

| Metric | Baseline | Fine-Tuned |
|---|---:|---:|
| Primary/Parse Success | 70% `███████░░░` | **100%** `██████████` |
| CodeBLEU-lite | 0.391 | **0.737** |
| CSR Similarity | 0.539 | **0.870** |

All syntax failures eliminated in the evaluation subset; largest single-metric jump in the project.

**T2 — Natural Language → Java**

| Metric | Baseline | Fine-Tuned |
|---|---:|---:|
| Compile Success | 40% `████░░░░░░` | **80%** `████████░░` |
| CodeBLEU-lite | 0.636 | **0.774** |
| CSR Similarity | 0.810 | **0.866** |

Compile success doubled — the strongest evidence that Prompt Contract v2.6 reinforced Java-specific structural constraints.

**T3 — Python → Java (translation)**

| Metric | Baseline | Fine-Tuned |
|---|---:|---:|
| Compile Success | 50% | 50% (unchanged) |
| CodeBLEU-lite | 0.815 | **0.940** |
| CSR Similarity | 0.839 | **0.929** |

Compile rate on this small subset didn't move, but semantic/structural quality of successful translations improved substantially.

**T4 — Java → Python (translation)**

| Metric | Baseline | Fine-Tuned |
|---|---:|---:|
| Parse Success | 90% | 90% (already strong) |
| CodeBLEU-lite | 0.812 | **0.925** |
| CSR Similarity | 0.860 | **0.871** |

**T5 — Python → Natural Language**

| Metric | Baseline | Fine-Tuned |
|---|---:|---:|
| ROUGE-L | 0.168 | **0.315** |
| SacreBLEU | 1.50 | **9.82** |
| Semantic Similarity | 0.587 | **0.699** |

**T6 — Java → Natural Language**

| Metric | Baseline | Fine-Tuned |
|---|---:|---:|
| ROUGE-L | 0.160 | **0.317** |
| SacreBLEU | 1.62 | **9.59** |
| Semantic Similarity | 0.571 | **0.669** |

### 7.3 Pattern across all six tasks

1. **Biggest gains where the baseline was weakest** — executable code generation (T1/T2) and NL summarization (T5/T6) improved the most.
2. **Translation tasks (T3/T4) started strong**, so gains show up in *semantic quality* (CodeBLEU-lite, CSR) rather than pass/compile rate.
3. **No task regressed** — the round-robin curriculum appears to have avoided catastrophic forgetting across the six tasks, which is not guaranteed in multitask fine-tuning.
4. **Agreement across independent metric families** (structural, lexical, semantic, compile/parse) makes the improvement more credible than any single metric would on its own — though see the limitation on evaluation sample size below.

---

# 8. Failure Analysis

Failures observed during evaluation were grouped into categories to understand *why* predictions fail, not just how often:

| Category | Description |
|---|---|
| Structural failures | Invalid syntax, missing braces, incomplete definitions |
| Compilation failures | Syntactically plausible Java that fails `javac` (bad signatures, missing wrapper class, unresolved identifiers) |
| Semantic mismatch | Structurally valid code that doesn't preserve the intended algorithm (shows up as lower CSR despite passing parse/compile) |
| Translation drift | Syntactically correct translation that deviates semantically from the reference |
| Summary incompleteness | NL explanations that omit algorithmic detail (lowers ROUGE-L/semantic similarity) |

**Takeaway:** structural correctness is necessary but not sufficient; most remaining failures are semantic/reasoning failures rather than syntax failures — which is exactly what CSR and semantic-similarity metrics are designed to catch that pass/fail parsing alone would miss.

---

# 9. Engineering Decisions, Limitations & Future Work

### 9.1 Key decisions and why they were made

| Earlier approach | Final decision | Reason |
|---|---|---|
| CodeAlpaca in training mix | Removed | Instruction noise, no trusted tests |
| APPS dataset | Removed | Loader complexity, runtime overhead |
| TransCoder integration | Removed | Increased multilingual alignment complexity |
| Multiple multilingual repos | XLCoST as sole primary source | Simplifies validation & reproducibility |
| Informal ad-hoc prompts | Prompt Contract v2.6 | Standardized format, reduced task interference |
| Full-parameter fine-tuning | QLoRA | Fits T4 GPU memory budget |
| Positional dataset alignment (Stage 3 legacy) | Semantic embedding + structural-bonus alignment | Positional join yielded only ~100 usable pairs |

### 9.2 Current limitations

- **Corpus size:** 403 approved rows is enough to demonstrate the architecture, not to claim strong generalization.
- **No execution-based testing:** infrastructure exists, but 0 approved rows had a safe generic test harness — explicitly excluded rather than faked.
- **Two languages only** (Python, Java) — XLCoST supports more, but out of scope here.
- **Single foundation model family** (Qwen2.5-Coder) — no cross-model comparison yet.
- **Small evaluation subset** (10 examples/task) for compute-budget reasons — improves confidence via metric agreement, but is not a substitute for larger-scale evaluation.

### 9.3 Natural next steps (ties into the project roadmap)

- Curated trusted unit tests per approved row → real execution-based evaluation.
- Larger validated corpus (more source datasets, same validation bar).
- Additional languages (C++, JavaScript, Go, Rust, C#).
- **Stage 4/5/6 roadmap:** repository-aware retrieval (AST indexing, FAISS + reranker RAG) and agentic orchestration (planner/retriever/generator/validator), building directly on top of this validated corpus and fine-tuned adapter rather than replacing them.

---

# 10. Conclusion

RepoCoder Studio demonstrates that **careful data engineering — semantic validation, structural verification via Tree-sitter, cross-language consistency checks (CSR), and standardized prompt contracts — produces measurable gains on a small model without full-parameter retraining.** Updating under 1% of a 0.5B-parameter model's weights, trained on a 403-row corpus that survived a real validation pipeline, was enough to raise Java compile success from 40% to 80%, eliminate Python syntax failures entirely on the evaluation subset, and roughly 6x SacreBLEU on code summarization — with no task regressing.

The core thesis this project supports: **for practical software-engineering tasks, investment in trustworthy data and disciplined evaluation can matter as much as investment in model scale.**
