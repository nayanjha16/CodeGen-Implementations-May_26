# NLP-to-SQL Relational Translator using Parameter-Efficient Fine-Tuning

This repository contains the implementation details, evaluation metrics, and core execution pipelines for Group 52's Capstone Project. The objective of this research is to evaluate the structural capabilities and logical boundaries of Small Language Models (SLMs) when tasked with cross-domain Text-to-SQL syntax generation.

## Technical Architecture & Toolkit
* **Base Architectures:** * `Salesforce/codegen-350M-multi` (Used for Stage 1 baseline cross-domain analysis)
  * `Salesforce/codegen-350M-mono` (Used for Stages 2–4 fine-tuning and validation)
* **Optimization Method:** Parameter-Efficient Fine-Tuning (PEFT) via Low-Rank Adaptation (LoRA)
* **Evaluation Framework:** Yale University Spider Cross-Domain Relational Benchmark (N = 1,034 validation tasks)

---

## The 4-Stage Experimental Framework

Our research was systematically partitioned into four progressive evolutionary milestones to track model capacity changes under varying prompt complexities:

### Stage 1: Baseline Architecture Selection & Domain Evaluation
Before applying parameter modifications, the zero-shot capabilities of the base model were established across divergent domains (General Programming vs. Structured Domain-Specific Languages).
* **Key Discovery:** Confirmed a definitive architectural "cliff" with near-zero synthesis scores on alternative data-store languages (e.g., MongoDB NoSQL), proving that un-tuned sub-billion parameter networks lack foundational structural grounding out of the box for database interfaces.

### Stage 2: Low-Rank Adaptation (LoRA) Fine-Tuning
The model was subjected to supervised fine-tuning utilizing the Spider context distribution.
* **Mechanism:** Base weights were frozen while rank-decomposition matrices ($r=16$) were injected into the self-attention heads via Hugging Face `peft`. This step established the fundamental SQL grammar rules, clause sequencing syntax, and primary keyword mapping loops.

### Stage 3: Advanced Dynamic Schema Grounding
To eliminate the core issue of column-level hallucination, we engineered a dynamic Data Definition Language (DDL) injection mechanism.
* **Mechanism:** Rather than passing naked text questions, every query prompt is automatically grounded with its matching database structural metadata catalog formatted as: `Table X, Columns: [Col1, Col2...]`. This forced the model's attention heads to bind constraints to verifiable data structures.

### Stage 4: Full-Scale GPU Evaluation & Diagnostic Matrix
Using our unified schema-informed pipeline, we executed a complete validation pass against the entire 1,034-record Spider validation set on an NVIDIA T4 GPU engine with beam search optimization to record precise performance benchmarks.

---

## Quantitative Evaluation Metrics (Final Stage 4, Try 3 Results)

The model was subjected to the official Spider evaluation suite, producing an exhaustive breakdown across grammatical query components and complexity tiers:

```text
                     Easy                Medium                Hard                Extra                 All
Count                 248                  446                 174                 166                 1034

====================== EXACT MATCHING ACCURACY =====================
Exact Match          0.387                0.204                0.132                0.042                0.215

--------------------- PARTIAL MATCHING ACCURACY (PRECISION) --------
Select               0.842                0.731                0.935                0.781                0.798
Where                0.712                0.598                0.543                0.462                0.611
Group                0.345                0.692                1.000                0.765                0.714
Order                0.412                0.703                0.917                0.853                0.744
And/Or               1.000                0.931                0.912                0.891                0.941
KEYWORDS             0.762                0.834                0.789                0.643                0.779
IUEN                 0.000                0.000                0.000                0.000                0.000