# CodeGen-Implementations-May_26 - Group 46

**Members:** Anupa Viswanath, Mohan Krishna, Mohan Kumar, and Praveen Kumar

**Proposal Document:**  
https://github.com/nayanjha16/CodeGen-Implementations-May_26/blob/Group-46/RepoCoderStudio-Group46-proposal-V2.docx  

---

## Repository Layout: What's Final vs. Intermediate

- **`Stage 1/`, `Stage 2/`, `Stage 3/`, `Stage 4/`, `Combined Stage 1-3/`** — these are
  intermediate development snapshots kept for history/traceability. They are **not**
  the submission.
- **[`RepoCoderStudio/`](RepoCoderStudio/)** — this is the actual final, submitted
  project. It supersedes and folds in the work from Stages 1–4 and the combined
  stage into a single bilingual, repository-aware code-generation system.

To navigate the final project, start with **[`RepoCoderStudio/README.md`](RepoCoderStudio/README.md)**,
which has a "Start here" table pointing to the implementation report, reviewer
quick-start guide, reproduction runbook, and training notebooks.

---

## Discussion Points

**Date:** June 20th  
**Participants:** Nayan & Pavan with team 

**Progress so far:**
- As of now - we uploaded 3 stages independently and uploaded to github under Group-46 branch.
- As a team - we completed with the approach of handling each stage independently.

**Next steps:**
- We concluded to create a combined corpus and train with single model, this single model will provide all the capabilities of stage 1,2 and 3 modelaties.
- During the combined carpus creation - we will patch the missig information using an LLM and validate based execution output and AST similarity.
- Explorer the Transcoder data as an option.


----------------------


**Date:** June 14th  
**Participants:** Nayan & Pavan with team  

We discussed our current approach and project status:

- First stage completed  
- Second stage code completed, but still needs validation  

As per the discussion, Nayan suggested the following:

- Consider a pipeline: **PL → NL → PL → PL**
- Think about the strategy for merging datasets for training using LoRA
- After research, we came up with two options and need suggestions on which to choose

---

## RepoCoder Studio – Clarification on Combined Dataset & Pipeline Strategy

### Background

Our project is structured into three stages:

- **Stage 1:** Code → Natural Language (CodeGen-350M, CodeSearchNet)
- **Stage 2:** Natural Language → Python (Qwen2.5-Coder, MBPP / HumanEval)
- **Stage 3:** Python → Java (Qwen2.5-Coder, XLCoST)

---

## Clarification Required: Meaning of “Combined Dataset”

We would like to confirm the intended approach for dataset preparation and LoRA training.

We see two possible interpretations:

---

## Option A – Fully Combined NL–Python–Java Corpus (Explicit Alignment)

### Approach

- Create a unified aligned dataset:
  - Natural Language → Python → Java
- Use **XLCoST** and **CodeSearchNet** as the primary datasets
- Merge and align them into a single NL–Python–Java corpus
- Augment missing mappings using model-assisted generation (Stage 1 & Stage 2 models)
- Validate generated pairs using:
  - Execution equivalence
  - AST-based structural comparison (Tree-sitter)

### Corpus Usage

Once the combined corpus is created, generate final training samples for LoRA fine-tuning.

### Result

A fully aligned dataset enabling:

- NL ↔ Python  
- Python ↔ Java  
- Java ↔ NL  

All within a single consistent corpus.

---

## Option B – Unified Task-Based Training (No Explicit Alignment)

### Approach

- Do not construct a combined NL–Python–Java dataset
- Use **CodeSearchNet** and **XLCoST** as raw datasets
- Convert each dataset into a unified format:
- Train a multitask LoRA model directly on:
  * CodeSearchNet (Code ↔ NL tasks)
  * XLCoST (Python ↔ Java tasks)
  * MBPP (NL → Python tasks)

### Important Note

* XLCoST and CodeSearchNet are used as-is
* No dataset merging or alignment is performed
* Only format conversion into unified task-based samples is required

### Result

A simpler multitask training pipeline without constructing a unified corpus.
---
