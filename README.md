# CodeGen-Implementations-May_26 - Group 46

**Members:** Anupa Vishwanath, Mohan Krishna, Mohan Kumar, and Praveen  

**Proposal Document:**  
https://github.com/nayanjha16/CodeGen-Implementations-May_26/blob/Group-46/RepoCoderStudio-Group46-proposal-V2.docx  

---

## Discussion Points

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
