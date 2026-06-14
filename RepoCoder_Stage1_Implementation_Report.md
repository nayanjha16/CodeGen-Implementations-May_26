# RepoCoder Studio – Stage 1 Final Frozen Implementation Report

**Multilingual Code Documentation Generation using LoRA Fine-Tuned CodeGen-350M-Multi**

Submission Version

---

## Executive Summary

Stage 1 establishes the code-understanding foundation of RepoCoder Studio. The objective is to automatically generate concise developer documentation from Python and Java source code. The project evolved through environment stabilization, dataset investigation, cleaning, token-length analysis, documentation-quality filtering, prompt engineering, docstring-only supervision, LoRA fine-tuning, evaluation, and output-quality refinement.

**Final Results:**
- Baseline ROUGE-L: 0.0235 → Fine-Tuned ROUGE-L: 0.4388  
- Baseline CodeBERTScore: 0.7806 → Fine-Tuned CodeBERTScore: 0.9080  
- Baseline Empty Output Rate: 44% → Fine-Tuned Empty Output Rate: 0%  

---

## Project Background and Motivation

Modern software repositories contain millions of lines of code with limited documentation. Developers spend substantial effort understanding unfamiliar code. Automated documentation generation reduces onboarding time, improves maintainability, and enables downstream code intelligence systems. Stage 1 focuses on this problem because documentation generation requires genuine code understanding and therefore provides an excellent foundation for later stages.

---

## Project Objectives

**Primary objectives:**
- Generate documentation from Python and Java code.
- Fine-tune a code language model using parameter-efficient techniques.
- Design a reproducible training and evaluation pipeline.
- Operate within Google Colab resource constraints.

**Secondary objectives:**
- Build reusable infrastructure for later stages.
- Develop robust cleaning and filtering pipelines.
- Establish evaluation methodology.

---

## Relationship to RepoCoder Studio Roadmap

- **Stage 1:** Code → Documentation  
- **Stage 2:** Natural Language → Python  
- **Stage 3:** Python → Java  
- **Stage 4+:** Repository Retrieval, AST-Aware Processing, Agents  

Stage 1 provides the code-understanding capability required by all subsequent stages.

---

## System Architecture

`Dataset Loading → Standardization → Cleaning → Token Analysis → Quality Filtering → Prompt Construction → Docstring-Only Supervision → LoRA Fine-Tuning → Evaluation → Reporting`

The architecture was intentionally modular so that common functionality can later be extracted into reusable modules.

---

## Environment Stabilization and Dependency Management

Significant effort was required to stabilize the Colab environment. Dependency conflicts involving `transformers`, `datasets`, `accelerate`, `huggingface_hub`, evaluation libraries and `Gradio` were encountered. Stable versions were identified and reused. This became an important lesson in reproducible machine-learning experimentation.

---

## Dataset Selection

**Dataset:** CodeSearchNet  
**Languages:** Python, Java  

These languages align with later project stages and provide sufficient training data for multilingual experimentation.

---

## Dataset Standardization

All examples converted into:
- `code`
- `docstring`
- `language_tag`

---

## Dataset Cleaning

Operations included:
- HTML removal
- Javadoc cleanup
- Whitespace normalization
- Empty/invalid example removal
- Repeated-sentence cleanup

---

## Token Length Analysis and Context Window Selection

**Results (500 sampled examples):**
- Avg Prompt Tokens: 282.04  
- Avg Documentation Tokens: 25.80  
- Avg Combined Tokens: 307.83  
- Max Combined Tokens: 3786  
- Truncation Rate: 7.2% (Java 5.2%, Python 9.2%)  

**Decision:** `MAX_LENGTH = 768` (compatible with Colab memory constraints)

---

## Documentation Filtering Strategy

Rules:
- Min documentation length: 4 words  
- Max documentation length: 150 words  
- Removal of low-quality examples  

**Results:**  
- Python: 412,178 → 389,991 examples retained  
- Java: 454,451 → 374,427 examples retained  

---

## Baseline Evaluation

**Metrics:**
- ROUGE-L: 0.0235  
- CodeBERTScore: 0.7806  
- Empty Output Rate: 44%  

Outputs were often empty or unrelated, showing need for fine-tuning.

---

## Prompt Engineering

Prompts included:
- Task instruction
- Programming language
- Source code
- Documentation marker

---

## Docstring-Only Supervision

Only documentation tokens contributed to training.  
- Avg supervised doc tokens: 22.75  
- Avg masked prompt/padding tokens: 745.25  

---

## LoRA Fine-Tuning Design

- Trainable Parameters: 983,040  
- Total Parameters: 357,695,488  
- Trainable Percentage: 0.2748%  

LoRA enabled efficient adaptation within Colab constraints.

---

## Training Results

Loss progression:  
- Step 100 → 2.1432  
- Step 200 → 1.7792  
- Step 300 → 1.4961  
- Step 400 → 1.6448  
- Step 500 → 1.9857  
- Step 600 → 1.8575  

No NaN failures, OOM issues, or gradient-scaling problems.

---

## Fine-Tuned Evaluation Results

**Overall:**
- ROUGE-L: 0.4388  
- CodeBERTScore: 0.9080  
- Empty Output Rate: 0%  

**Language Breakdown:**
- Java: ROUGE-L 0.1671, CodeBERTScore 0.8552  
- Python: ROUGE-L 0.6896, CodeBERTScore 0.9425  

---

## Baseline vs Fine-Tuned Comparison

- ROUGE-L: 0.0235 → 0.4388 (+0.4153)  
- CodeBERTScore: 0.7806 → 0.9080 (+0.1274)  
- Empty Output Rate: 44% → 0%  

---

## Output Quality Refinement

Improvements:
- Repeated sentence removal
- Conciseness enforcement
- Improved cleaning rules
- Generation constraints
- Post-processing

---

## Representative Outputs

- Factorial: *"If n is a non-negative integer, the result is the factorial of n."*  
- JSON Reader: *"Reads a JSON file and returns a dictionary."*  
- Palindrome: *"Checks if the string is a palindrome. Returns true if the string is a palindrome."*  
- File Reader: *"Reads a file. Returns the contents of the file as a string."*  

---

## Challenges and Solutions

- Dependency conflicts → Stable version pinning  
- Dataset loader failures → Official-first strategy  
- Context-window selection → Token analysis  
- Verbose documentation → Quality filtering  
- Colab limitations → LoRA and chunked design  
- Output repetition → Cleaning and decoding improvements  

---

## Lessons Learned

1. Clean data ≠ good training data  
2. Dataset quality > dataset size  
3. Token analysis guides context-window selection  
4. Prompt masking improves supervision quality  
5. LoRA is effective for Colab-scale experimentation  
6. Combine quantitative + qualitative evaluation  
7. Evidence-driven engineering decisions  

---

## Future Work

- Stage 2: Natural Language → Python  
- Stage 3: Python → Java  
- Repository-aware retrieval  
- AST-aware chunking  
- Agent orchestration  
- Larger-context code models  

---

## Conclusion

Stage 1 successfully established a multilingual documentation-generation pipeline. The final model achieved substantial improvements over the pretrained baseline, eliminated empty outputs, and demonstrated meaningful code understanding. The resulting system provides a strong foundation for all subsequent RepoCoder Studio stages.
