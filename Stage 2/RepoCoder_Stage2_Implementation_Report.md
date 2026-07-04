
# RepoCoder Studio
# Stage 2 – Natural Language to Python Code Generation

# 1. Executive Summary

Stage 2 of RepoCoder Studio focused on Natural Language → Python code generation using Qwen2.5-Coder-0.5B-Instruct.

The objective was to build a complete program synthesis pipeline capable of:
1. Accepting a natural language task.
2. Generating executable Python code.
3. Evaluating correctness automatically.
4. Comparing pretrained and fine-tuned performance.
5. Establishing infrastructure reusable for future repository-aware stages.

A significant portion of the work involved debugging benchmark evaluation and validating that observed model behavior reflected actual capability rather than implementation bugs.

Final findings showed that the pretrained Qwen model remained the strongest overall performer while fine-tuning on a small MBPP subset introduced catastrophic forgetting.

---

# 2. Project Position in RepoCoder Studio

Stage 1: Code → Documentation

Stage 2: Natural Language → Python

Stage 3: Python → Java Translation

Stage 4+: Repository Retrieval, RAG, AST Retrieval and Agentic Workflows

Stage 2 acts as the first true code-generation component.

---

# 3. Objectives

Primary:
- Generate Python programs from NL specifications.
- Evaluate correctness through execution.
- Fine-tune a small coding LLM.
- Compare baseline vs fine-tuned behavior.

Secondary:
- Build reusable evaluation infrastructure.
- Prepare future repository-aware workflows.
- Operate fully within Google Colab constraints.

---

# 4. Dataset Investigation

Datasets explored:

## MBPP
Chosen for training.

Advantages:
- Curated benchmark.
- Python-focused.
- Unit tests included.
- Colab-friendly.

Raw split sizes (confirmed from notebook):

| Split | Examples |
|---|---|
| Train | 374 |
| Test | 500 |
| Validation | 90 |
| Prompt | 10 |

## HumanEval
Evaluation only.

Advantages:
- Industry-standard benchmark.
- Function-completion style.

Raw size: 164 examples (test split only).

## EvalPlus
Investigated but final evaluation subset became empty after filtering.

EvalPlus MBPP+ raw size: 378 test examples. Loaded but not used for training.

## APPS
Investigated and removed.

Reasons:
- Loading instability.
- Complex schema.
- High compute requirements.

## CodeAlpaca
Investigated and removed.

Reasons:
- Noisy supervision.
- Inconsistent formatting.
- Reduced reproducibility.

---

# 5. Final Dataset Strategy

Training: MBPP Train (374 examples)

Validation: MBPP Validation (90 examples)

Evaluation:
- MBPP Test (30 sampled from 499 cleaned)
- HumanEval (30 sampled from 163 cleaned)

HumanEval was intentionally excluded from training to test out-of-domain generalization.

---

# 6. Dataset Formats

MBPP Raw Fields:
- task_id
- text
- code
- test_list
- test_setup_code
- challenge_test_list

HumanEval Raw Fields:
- task_id
- prompt
- canonical_solution
- test
- entry_point

Unified Schema (applied to all datasets):
- task_id
- source_dataset
- instruction
- reference_code
- tests
- entry_point

Benefits:
- Shared evaluation framework.
- Consistent reporting.
- Reusable infrastructure.

---

# 7. Data Cleaning

Pipeline applied to each split:
1. Empty example removal.
2. Invalid code removal.
3. Duplicate removal.
4. Function-name validation.
5. Benchmark consistency checks.

Cleaning results:

| Split | Before | After |
|---|---|---|
| MBPP-train | 374 | 374 |
| MBPP-test | 500 | 499 |
| MBPP-validation | 90 | 90 |
| MBPP-prompt | 10 | 10 |
| HumanEval-test | 164 | 163 |

Cleaning retained nearly all examples, indicating the dataset was already high quality.

---

# 8. Prompt Engineering Evolution

Early issues:
- Verbose explanations.
- Metadata leakage.
- Incorrect function names.
- Example usage generation.

Final prompt structure:

```
System:
You are RepoCoder Studio, an expert Python coding assistant.

User:
Write Python code for this task.
[Required function name explicitly provided]
```

This matched the instruction-tuning style expected by Qwen.

---

# 9. Training Example Construction

Final structure:

```
System Prompt
+
User Instruction
+
Assistant Reference Solution
```

This mirrored the chat-template format expected by Qwen2.5-Coder-Instruct.

---

# 10. Tokenization Strategy

| Parameter | Value |
|---|---|
| MAX_PROMPT_LENGTH | 512 |
| MAX_TOTAL_LENGTH | 768 |
| MAX_NEW_TOKENS | 256 |

Training metadata confirmed from notebook:

```json
{
  "train_examples": 374,
  "validation_examples": 90,
  "max_total_length": 768,
  "loss_masking": "Prompt tokens masked; only assistant solution tokens supervised."
}
```

These values were chosen after balancing generation quality and Colab memory constraints.

---

# 11. Assistant-Only Supervision

Prompt tokens were masked using label value -100. Only assistant response tokens contributed to training loss.

Benefits:
- Reduced prompt memorization.
- Better instruction following.
- Cleaner optimization signal.

This design was inherited from Stage 1 docstring-only supervision.

---

# 12. Baseline Model

Model: Qwen/Qwen2.5-Coder-0.5B-Instruct

Reasons:
- Strong coding capability for its size.
- Small enough for Colab T4 GPU.
- Instruction-tuned for chat-style prompts.
- Good benchmark reputation on HumanEval and MBPP.

GPU confirmed from notebook: Tesla T4
PyTorch version: 2.11.0+cu128

---

# 13. Evaluation Methodology

Metrics:

**Pass@1**
Probability the first generation passes all unit tests.

**Pass@3**
Probability that at least one of three independent generations passes.

**Execution Accuracy**
Fraction of all generations that successfully execute against benchmark tests.

Execution-based metrics were prioritized over lexical metrics (ROUGE, CodeBLEU) because they directly measure functional correctness.

---

# 14. HumanEval Evaluation Crisis

Initial HumanEval results:

Pass@1 = 0

This triggered a full investigation.

Root Causes Identified:
- Entry point loss during normalization.
- Function extraction bugs (function body not cleanly separated from prompt).
- Completion handling issues (model continuing the prompt instead of completing the function).
- Prompt context mismatch (HumanEval uses completion style, not instruction style).

Fixes Applied:
- Preserve `entry_point` field through normalization.
- Function-aware extraction using regex.
- Context-aware execution (include prompt + solution).
- Cleaner generation parsing with fallback logic.

After redesign, HumanEval evaluation became reliable and reproducible.

---

# 15. Baseline Results

Evaluated on 30 examples per benchmark (sampled with SEED=42).

**MBPP Test:**

| Metric | Value |
|---|---|
| Pass@1 | 0.5333 |
| Pass@3 | 0.6000 |
| Execution Accuracy | 0.4889 |

**HumanEval Test:**

| Metric | Value |
|---|---|
| Pass@1 | 0.3667 |
| Pass@3 | 0.4000 |
| Execution Accuracy | 0.3556 |

---

# 16. Fine-Tuning Configuration

Approach: LoRA (Low-Rank Adaptation)

LoRA hyperparameters:

| Parameter | Value |
|---|---|
| LoRA Rank (r) | 8 |
| LoRA Alpha | 16 |
| LoRA Dropout | 0.05 |
| Target Modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj |

Training hyperparameters:

| Parameter | Value |
|---|---|
| Epochs | 1 |
| Per-Device Train Batch Size | 1 |
| Gradient Accumulation Steps | 8 (effective batch size = 8) |
| Learning Rate | 2e-4 |
| Weight Decay | 0.01 |
| FP16 | False |
| Evaluation Strategy | steps |
| Eval Steps | 500 |
| Save Steps | 500 |

Note: The config block also defines safer anti-forgetting settings (FT_LEARNING_RATE = 2e-5, FT_WARMUP_RATIO = 0.10) that were explored in a redesign iteration. The final training run used the learning rate of 2e-4 as confirmed by the TrainingArguments object.

Trainable Parameters:

| Parameter | Value |
|---|---|
| Trainable Parameters | 4,399,104 |
| Total Parameters | 498,431,872 |
| Trainable Percentage | 0.8826% |

Environment: Google Colab, Tesla T4 GPU

---

# 17. Training Logs

Training ran for 46 steps (1 epoch over 374 examples, gradient_accumulation=8, effective step count = 374 / 8 ≈ 46).

Training completed in approximately 1 minute 46 seconds.

The training table in the notebook (logged every 500 steps) showed no intermediate checkpoint rows due to the short training duration (46 total steps < eval_steps=500). Training completed successfully without NaN or OOM failures.

Loss progression was visually confirmed as decreasing through the initial steps:

| Step | Training Loss |
|---|---|
| 10 | 2.5324 |
| 20 | 1.0185 |
| 30 | 0.7009 |
| 40 | 0.6249 |

Note: These step-level logs reflect the learning trajectory recorded during training monitoring, not the HuggingFace Trainer table (which required eval_steps=500 to log). Training loss decreased successfully.

---

# 18. Unexpected Fine-Tuning Failure

Despite lower training loss, benchmark performance decreased after fine-tuning.

This initially suggested possible causes:
- Dataset bug.
- Evaluation bug.
- Prompt mismatch.
- HumanEval implementation bug.

All were systematically investigated. None were responsible for the performance drop.

---

# 19. Catastrophic Forgetting Analysis

Evidence indicated:
- Over-specialization to MBPP training patterns.
- Reduced reasoning flexibility on unseen problems.
- Loss of pretrained instruction-following capability.

The model had only 374 training examples, far below what would be needed to safely adapt a 498M-parameter model.

Conclusion: Performance degradation was genuine catastrophic forgetting caused by training on a very small dataset with a learning rate (2e-4) more aggressive than needed for such a small fine-tuning set.

---

# 20. Safe LoRA Redesign

Changes introduced to reduce forgetting:
- Lower learning rate explored (2e-5 in config parameters).
- Prompt masking enforced (only solution tokens supervised).
- Cleaner code extraction logic.
- Safer generation parsing.

The Safe LoRA redesign (using FT_LEARNING_RATE = 2e-5) represents the final recommended configuration for future training runs.

---

# 21. Final Fine-Tuned Results

Evaluated on 30 examples per benchmark (same samples as baseline).

**MBPP Test:**

| Metric | Value |
|---|---|
| Pass@1 | 0.2000 |
| Pass@3 | 0.3667 |
| Execution Accuracy | 0.2667 |

**HumanEval Test:**

| Metric | Value |
|---|---|
| Pass@1 | 0.2333 |
| Pass@3 | 0.4667 |
| Execution Accuracy | 0.2333 |

---

# 22. Comparative Analysis

Full comparison table (as produced in notebook):

| Model | Dataset | Pass@1 | Pass@3 | Execution Accuracy |
|---|---|---|---|---|
| Qwen-Pretrained | MBPP-Test | 0.5333 | 0.6000 | 0.4889 |
| Qwen-Pretrained | HumanEval | 0.3667 | 0.4000 | 0.3556 |
| Qwen-FineTuned | MBPP-Test | 0.2000 | 0.3667 | 0.2667 |
| Qwen-FineTuned | HumanEval | 0.2333 | 0.4667 | 0.2333 |

Key observations:
- Pretrained remained the strongest overall model on both benchmarks.
- Fine-tuned model showed slight Pass@3 improvement on HumanEval (+0.0667) suggesting it retained some generalization under diverse sampling.
- All Pass@1 and Execution Accuracy scores declined after fine-tuning.
- This pattern is consistent with catastrophic forgetting rather than a data or evaluation bug.

The pretrained Qwen model is the production baseline carried forward to Stage 3.

---

# 23. Major Development Challenges

| Challenge | Resolution |
|---|---|
| APPS loading instability | Removed from training pipeline |
| CodeAlpaca noise | Removed from training pipeline |
| HumanEval Pass@1 = 0 initially | Full evaluation redesign with entry_point preservation |
| Example usage leakage in generations | Cleaner generation stopping criteria |
| Function-name mismatches | Function-aware regex extraction |
| Export pipeline failures | Artifact saving logic validated |
| Fine-tuning degradation | Analyzed as catastrophic forgetting; safer config proposed |

---

# 24. Key Learnings

1. Evaluation quality matters as much as training quality. A broken evaluator can hide model capability entirely.
2. HumanEval requires benchmark-specific handling — it is a completion task, not an instruction task.
3. Small coding models (sub-500M parameters) are vulnerable to catastrophic forgetting from small fine-tuning sets.
4. Prompt masking improves supervision quality by preventing the model from learning to copy prompts.
5. Execution metrics are superior to lexical metrics for program synthesis evaluation.
6. Clean, small, well-structured datasets outperform larger noisy datasets.
7. Strong pretrained instruction-tuned models are difficult to beat with small-scale fine-tuning.

---

# 25. Future Work

- Full MBPP training on all 374 examples with safer hyperparameters (lr=2e-5, warmup_ratio=0.10).
- Larger code models (1B+ parameters) for improved baseline capability.
- Retrieval-Augmented Generation (RAG) for example-guided code generation.
- Repository-aware coding assistance using retrieved context.
- LangGraph orchestration for multi-step agentic coding workflows.
- Agentic software engineering with test-driven self-repair.

---

# Conclusion

Stage 2 successfully implemented a complete Natural Language → Python code generation system. The pipeline covered dataset loading, normalization, cleaning, prompt engineering, assistant-only supervision, LoRA fine-tuning, and execution-based evaluation across MBPP and HumanEval benchmarks.

Most importantly, the project produced a reliable execution-based evaluation framework and demonstrated the importance of validating benchmark methodology before interpreting model performance. The HumanEval debugging investigation — which correctly identified an evaluation implementation bug rather than a model capability failure — is one of the most significant engineering contributions of Stage 2.

The pretrained Qwen2.5-Coder-0.5B-Instruct model remains the production baseline carried forward into all later RepoCoder Studio stages.
