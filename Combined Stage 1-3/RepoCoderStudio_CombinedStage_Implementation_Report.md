# RepoCoder Studio

# Implementation Report

### Implementation of the Combined Architecture

---

**Project Title**

**RepoCoder Studio: A Unified Multitask Framework for Multilingual Code Intelligence Using Semantic Corpus Validation and Parameter-Efficient Fine-Tuning**

---

**Capstone Project**

Master of Computer Applications

---

**Document Type**

Final Engineering Implementation Report

---

**Implementation Status**

Final Frozen Implementation

---

**Project Version**

Combined Stage — Version 2.0

---

**Author**

*<Your Name>*

---

**Supervisor**

*<Mentor Name>*

---

**Date**

2026

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| v0.8 | Development Phase | Interim implementation report documenting the evolving engineering pipeline. |
| v2.0 | Architecture Freeze | Frozen Engineering Design Specification defining the final system architecture and implementation decisions. |
| Final | Implementation Completion | Consolidated implementation report describing the realization of the frozen architecture, experimental evaluation, engineering decisions, lessons learned, and future improvements. |

---

# Table of Contents

1. Executive Summary
2. Abstract
3. Introduction
4. Background
5. Problem Statement
6. Motivation
7. Project Objectives
8. Project Scope
9. Major Contributions
10. Report Organization
11. Overall System Architecture
12. End-to-End Workflow
13. Dataset Engineering
14. Semantic Validation and Corpus Construction
15. Prompt Contract Design
16. Multitask Dataset Construction
17. LoRA Fine-Tuning
18. Evaluation Methodology
19. Experimental Results
20. Baseline vs Fine-Tuned Comparison
21. Failure Analytics
22. Discussion
23. Lessons Learned
24. Limitations
25. Future Improvements
26. Conclusion
27. References
28. Appendices

---

# Executive Summary

Recent advances in Large Language Models (LLMs) have significantly improved the capabilities of automated software engineering systems. Modern code-oriented language models can generate executable programs, translate source code between programming languages, summarize existing implementations, and assist software developers throughout the development lifecycle. Despite these advances, practical deployment of such systems remains heavily dependent on the quality of the training data, the consistency of prompting strategies, and the robustness of evaluation methodologies.

Many publicly available multilingual programming datasets are created by aggregating information from diverse sources. While these datasets are invaluable for research, they frequently contain duplicated solutions, inconsistent documentation, incomplete implementations, syntactic errors, or semantically misaligned language pairs. Training directly on these datasets often propagates these inconsistencies into downstream models, limiting both correctness and generalization.

RepoCoder Studio was conceived to address this problem through an engineering-first approach. Instead of treating dataset preparation as a preliminary preprocessing step, the project places equal emphasis on corpus engineering, semantic validation, prompt standardization, reproducibility, and evaluation. Every candidate example is considered untrusted until it successfully passes multiple structural and semantic validation stages. Only validated samples are admitted into the final training corpus.

The project evolved through multiple implementation stages before converging on a frozen engineering architecture. Early experiments demonstrated that simply increasing the volume of training data did not consistently improve model performance. Instead, careful dataset selection, semantic validation, and prompt engineering produced significantly greater benefits than increasing dataset size alone. These observations fundamentally changed the direction of the project and resulted in a data-centric engineering pipeline that prioritizes corpus quality over corpus quantity.

The final implementation integrates semantic corpus validation, multilingual dataset engineering, standardized prompt contracts, multitask instruction dataset construction, parameter-efficient fine-tuning using Quantized Low-Rank Adaptation (QLoRA), comprehensive evaluation, comparison analytics, and failure analysis within a single reproducible framework.

The completed system supports six complementary programming tasks:

- Natural Language → Python
- Natural Language → Java
- Python → Java Translation
- Java → Python Translation
- Python → Natural Language Summarization
- Java → Natural Language Summarization

Rather than training independent models for each task, RepoCoder Studio constructs a unified multitask instruction dataset that enables a single language model to learn all supported capabilities simultaneously. This approach reduces computational requirements while encouraging knowledge sharing across related programming tasks.

Experimental evaluation demonstrated measurable improvements across all supported task families following fine-tuning. Python code generation achieved complete parsing success on the evaluation subset, Java compilation success approximately doubled for natural-language-driven code generation, translation quality improved consistently across both programming language translation tasks, and natural language summarization exhibited substantial gains in lexical and semantic similarity metrics.

Throughout implementation, particular emphasis was placed on engineering reproducibility. Every major processing stage produces versioned artefacts, including validated corpora, prompt contracts, multitask datasets, configuration manifests, comparison tables, and evaluation summaries. These artefacts enable interrupted experiments to resume safely while providing complete traceability throughout the project lifecycle.

The resulting system represents not merely a fine-tuned language model but a comprehensive engineering framework for multilingual code intelligence that can serve as a foundation for future research and practical software engineering applications.

---

# Abstract

Large Language Models have rapidly transformed automated software engineering by enabling high-quality code generation, source code translation, and program summarization. However, the effectiveness of these models is fundamentally dependent upon the quality of the training corpus, the consistency of instruction formatting, and the reliability of evaluation methodologies. Publicly available multilingual code datasets frequently contain structural inconsistencies, duplicated implementations, semantically misaligned language pairs, and incomplete documentation that adversely affect downstream model performance.

This project presents **RepoCoder Studio**, a unified engineering framework designed to construct, validate, and utilize a semantically consistent multilingual programming corpus for multitask code intelligence. Unlike conventional pipelines that assume publicly available datasets are inherently trustworthy, the proposed framework treats every dataset entry as an unverified candidate requiring structural and semantic validation before inclusion in the approved corpus.

The implementation integrates semantic corpus engineering, multilingual alignment, prompt contract standardization, multitask dataset construction, parameter-efficient fine-tuning using Quantized Low-Rank Adaptation (QLoRA), and comprehensive evaluation within a single reproducible architecture. The final system supports six complementary programming tasks spanning executable code generation, cross-language translation, and natural language summarization using a single instruction-tuned model.

The multilingual corpus was constructed by combining carefully selected public datasets while eliminating noisy or unreliable sources identified during experimentation. Dataset engineering incorporated semantic consistency validation, Python Abstract Syntax Tree parsing, Java compilation, Tree-sitter structural analysis, duplicate detection, embedding-based semantic alignment, and teacher-assisted repair prior to freezing the approved corpus. Standardized prompt contracts were then applied to generate a balanced multitask instruction dataset suitable for supervised fine-tuning.

Parameter-efficient adaptation was performed using QLoRA on the Qwen2.5-Coder-0.5B-Instruct model, requiring less than one percent of the total model parameters to be updated during training. The resulting model was evaluated using task-specific structural and semantic metrics including Python parsing success, Java compilation success, Cross-language Semantic Consistency Ratio (CSR), CodeBLEU-lite, ROUGE-L, SacreBLEU, and sentence embedding similarity.

Experimental evaluation demonstrated consistent improvements across all supported programming tasks following fine-tuning while preserving multitask stability. The implementation additionally incorporates comparison analytics and failure categorization to facilitate systematic investigation of remaining model limitations.

The completed framework demonstrates that careful corpus engineering, semantic validation, and prompt standardization can significantly improve multilingual code intelligence without requiring larger foundation models or substantially increased computational resources. Furthermore, the modular engineering architecture provides a reproducible foundation for future research involving executable test generation, larger multilingual corpora, advanced evaluation methodologies, and expanded programming language support.

---

# 1. Introduction

Artificial Intelligence has fundamentally transformed the field of software engineering over the past decade. Advances in transformer-based architectures and Large Language Models (LLMs) have enabled machines to generate source code, translate programs across programming languages, summarize complex implementations, and assist developers throughout the software development lifecycle. These capabilities have led to the emergence of intelligent programming assistants capable of accelerating software development while reducing repetitive programming effort.

Despite these remarkable advances, the practical performance of code-oriented language models remains constrained by factors extending far beyond model architecture alone. Modern foundation models are typically pretrained on enormous collections of publicly available source code and natural language documentation obtained from heterogeneous online repositories. Although these datasets provide considerable diversity, they also introduce substantial inconsistencies. Duplicate implementations, incomplete code fragments, inaccurate documentation, semantically misaligned language pairs, inconsistent formatting conventions, and varying code quality collectively reduce the effectiveness of downstream supervised fine-tuning.

Consequently, successful deployment of multilingual code intelligence systems requires considerably more than simply selecting a pretrained model and performing supervised fine-tuning. Reliable performance depends equally upon careful corpus engineering, rigorous semantic validation, standardized prompting strategies, reproducible experimentation, and comprehensive evaluation methodologies.

RepoCoder Studio was developed to address these broader engineering challenges. Rather than treating dataset preparation as a preliminary preprocessing activity, the project elevates corpus validation to a primary architectural component. Every stage of the implementation—from dataset acquisition through evaluation—was designed to maximize reliability, reproducibility, and engineering transparency.

The final implementation therefore represents a complete multilingual code intelligence framework rather than a standalone machine learning experiment. It combines validated multilingual corpora, standardized prompt contracts, multitask dataset construction, parameter-efficient model adaptation, task-aware evaluation, comparison analytics, and failure investigation into a unified engineering pipeline capable of supporting multiple complementary software engineering tasks.

Unlike many existing implementations that focus exclusively on improving model architecture or increasing dataset size, RepoCoder Studio demonstrates that carefully engineered data pipelines can produce significant improvements in downstream performance while remaining computationally efficient. This philosophy ultimately guided every major engineering decision adopted during implementation and forms the foundation for the frozen architecture presented throughout this report.

# 2. Background

## 2.1 Evolution of Intelligent Software Engineering

Software engineering has undergone a remarkable transformation over the past several decades. Traditional software development relied entirely on manual programming, requiring developers to translate requirements into executable source code through extensive design, implementation, testing, and debugging activities. While Integrated Development Environments (IDEs), static analysis tools, and automated testing frameworks significantly improved developer productivity, the responsibility for generating and maintaining software remained almost entirely human-driven.

The emergence of machine learning introduced new opportunities for automating aspects of software development. Early research focused on tasks such as code completion, bug prediction, clone detection, and automated documentation generation using statistical learning methods. Although these approaches demonstrated promising results, they were generally limited to narrowly defined tasks and lacked the ability to understand programming problems at a semantic level.

The introduction of transformer-based architectures fundamentally changed this landscape. Models such as GPT, CodeBERT, CodeT5, StarCoder, DeepSeek-Coder, and Qwen-Coder demonstrated that large language models trained on vast collections of source code could learn rich representations of programming languages. These models exhibited capabilities far beyond simple code completion, including program synthesis from natural language, cross-language translation, automatic documentation generation, code repair, and reasoning over complex programming tasks.

These advances created the possibility of developing unified programming assistants capable of supporting multiple software engineering activities through a single underlying model. However, they also exposed a critical dependency: the quality of model outputs became increasingly dependent on the quality of the datasets used during supervised fine-tuning.

---

## 2.2 The Importance of High-Quality Training Data

Although foundation models are pretrained on billions of source code tokens, domain-specific adaptation remains essential for achieving reliable performance on specialized programming tasks. Supervised fine-tuning enables pretrained models to learn task-specific behaviour by exposing them to curated examples of desired inputs and outputs.

The effectiveness of supervised fine-tuning depends directly upon the quality of the training corpus. If the dataset contains duplicated implementations, inconsistent documentation, structurally invalid code, or semantically incorrect language pairs, these inconsistencies become part of the learned behaviour of the resulting model. Consequently, increasing the size of a dataset does not necessarily improve model performance. In many cases, introducing additional low-quality examples degrades performance by encouraging the model to learn contradictory mappings.

This observation became increasingly evident during the early implementation phases of RepoCoder Studio. Initial experiments using multiple publicly available datasets produced inconsistent improvements despite using strong pretrained models. Investigation revealed that the principal limitation was not the model architecture itself, but rather the quality and consistency of the training data.

These findings motivated a fundamental shift in project philosophy. Instead of pursuing increasingly larger datasets, the implementation prioritized semantic validation, deterministic preprocessing, prompt consistency, and reproducibility. This transition from a model-centric workflow to a data-centric engineering methodology ultimately became one of the defining characteristics of the final system.

---

## 2.3 Challenges in Multilingual Code Intelligence

Developing multilingual code intelligence systems introduces additional complexities beyond those encountered in single-language code generation.

Unlike natural language translation, source code translation must preserve exact program behaviour. Two programs written in different programming languages may appear structurally different while remaining semantically equivalent. Conversely, programs with similar lexical structure may exhibit entirely different execution behaviour. Consequently, evaluation based solely on lexical similarity is insufficient for measuring translation quality.

Furthermore, programming languages differ substantially in syntax, type systems, standard libraries, execution models, and language-specific programming idioms. Translating programs between languages therefore requires preserving functional behaviour while simultaneously adapting to language-specific conventions. This increases the importance of semantic alignment during dataset construction.

Natural language documentation introduces further complexity. Programming task descriptions vary significantly in style, level of detail, and terminology. Different datasets may describe identical algorithms using entirely different wording, making straightforward lexical matching unreliable. Robust multilingual corpus construction therefore requires semantic rather than purely textual validation.

These challenges motivated the incorporation of multiple complementary validation strategies within RepoCoder Studio, including structural verification, semantic embedding similarity, Cross-language Semantic Consistency Ratio (CSR), language-aware parsing, compilation analysis, and teacher-assisted repair.

---

## 2.4 Why Existing Public Datasets Cannot Be Used Directly

Several high-quality public datasets exist for code generation and translation research, including MBPP, XLCoST, HumanEval, APPS, CodeAlpaca, and TransCoder. Each dataset contributes valuable examples and has supported numerous research efforts. However, none of these datasets individually satisfies all requirements necessary for constructing a reliable multitask multilingual code intelligence framework.

During implementation, each candidate dataset was carefully evaluated with respect to quality, consistency, structural validity, task suitability, and practical engineering considerations. This evaluation revealed several important limitations.

Instruction-tuning datasets such as CodeAlpaca provide large numbers of programming examples but frequently lack executable test cases, making reliable evaluation difficult. Many responses also contain explanatory prose or formatting inconsistencies that are unsuitable for deterministic code generation tasks.

Similarly, although APPS contains challenging programming problems accompanied by test cases, practical integration introduced significant schema inconsistencies and dataset loading challenges. Maintaining APPS within the engineering pipeline substantially increased implementation complexity while providing comparatively limited additional benefit relative to MBPP.

Multilingual translation datasets exhibited a different set of challenges. Initial experimentation considered combining multiple multilingual repositories, including XLCoST and TransCoder. However, maintaining multiple partially overlapping datasets complicated alignment, increased preprocessing complexity, and introduced additional opportunities for semantic inconsistency.

These observations ultimately motivated several important architectural decisions that were frozen prior to final implementation:

- MBPP was selected as the sole supervised training dataset for Stage 2 due to its clean structure and executable evaluation methodology.
- HumanEval and EvalPlus were retained exclusively for evaluation to avoid benchmark leakage.
- XLCoST became the authoritative multilingual corpus for Stage 3.
- TransCoder and additional mirror datasets were removed to simplify corpus construction and improve reproducibility.

These decisions significantly reduced implementation complexity while simultaneously improving corpus consistency.

---

# 3. Problem Statement

The rapid advancement of Large Language Models has created unprecedented opportunities for automating software engineering tasks. Nevertheless, practical deployment remains constrained by three fundamental challenges.

The first challenge concerns dataset reliability. Public programming datasets often contain inconsistencies between natural language descriptions and corresponding implementations, duplicated solutions, incomplete programs, formatting errors, and semantically incorrect language pairs. Training directly on these datasets encourages models to learn unreliable mappings that reduce downstream performance.

The second challenge involves task fragmentation. Most existing systems are optimized for a single programming task, such as natural language to code generation or code translation. Real-world software engineering, however, requires a considerably broader range of capabilities including executable code generation, bidirectional translation, and automated documentation generation. Maintaining independent models for each task increases computational requirements while preventing knowledge sharing across related programming activities.

The third challenge concerns reproducibility. Many research implementations tightly couple preprocessing, training, and evaluation within experimental notebooks, making independent verification difficult. Reproducing results often requires reconstructing undocumented preprocessing decisions or manually repeating computationally expensive pipeline stages.

Consequently, there exists a need for a unified engineering framework capable of constructing a semantically validated multilingual programming corpus, supporting multiple programming tasks through standardized prompt contracts, enabling efficient multitask model adaptation, and providing comprehensive reproducible evaluation.

RepoCoder Studio was developed to address precisely these challenges.

---

# 4. Motivation

The motivation for RepoCoder Studio emerged gradually through implementation rather than being fully defined at the outset of the project.

Initial experiments focused primarily on improving model performance by increasing dataset diversity. Multiple publicly available datasets were incorporated into early training pipelines with the expectation that additional training examples would naturally improve downstream results. Contrary to expectation, these experiments produced inconsistent improvements despite employing increasingly sophisticated pretrained models.

Careful investigation revealed that the principal source of performance degradation originated from the datasets themselves. Examples exhibiting semantic inconsistencies, duplicated implementations, incompatible schemas, incomplete documentation, or unreliable evaluation procedures contributed more noise than useful supervision.

This realization fundamentally changed the direction of the project.

Instead of asking, *"Which model should be trained?"*, the project began asking, *"Which data deserves to be trusted?"*

This seemingly simple change in perspective transformed the implementation into a data-centric engineering framework. Corpus validation, semantic consistency, prompt standardization, deterministic preprocessing, reproducibility, and evaluation became primary architectural concerns rather than supporting utilities.

Another important motivation involved practical deployment. Modern foundation models continue to increase in size, making full-parameter fine-tuning prohibitively expensive for many research environments. Parameter-efficient adaptation techniques such as QLoRA provide an attractive alternative by enabling competitive performance while updating only a small fraction of model parameters. Integrating such techniques within a reproducible multilingual pipeline became a major objective of the project.

Ultimately, RepoCoder Studio was motivated by the belief that careful engineering can often produce larger improvements than simply increasing model size or dataset volume. The final implementation embodies this philosophy throughout every stage of the pipeline.

# 5. Project Objectives

The primary objective of RepoCoder Studio was to design and implement a unified engineering framework capable of supporting multiple software engineering tasks using a single instruction-tuned language model. Rather than focusing exclusively on model optimization, the project sought to demonstrate that improvements in corpus quality, semantic validation, prompt engineering, and reproducibility could significantly enhance downstream performance while maintaining computational efficiency.

To achieve this vision, the project established a set of clearly defined engineering objectives that guided every stage of implementation.

---

## 5.1 Primary Objective

The primary objective of the project is:

> **To design, implement, and evaluate a reproducible multilingual code intelligence framework that combines semantic corpus validation, standardized prompt engineering, multitask instruction tuning, and parameter-efficient fine-tuning to improve automated software engineering tasks.**

This objective reflects the central philosophy of RepoCoder Studio: high-quality data engineering should precede model optimization.

---

## 5.2 Specific Objectives

To realize the primary objective, the implementation pursued the following specific goals.

### Objective 1 — Construct a Reliable Multilingual Programming Corpus

Public datasets were not assumed to be inherently trustworthy. Instead, every dataset entry was treated as an unverified candidate requiring structural and semantic validation before inclusion within the approved corpus.

This objective required:

- dataset standardization,
- metadata normalization,
- semantic alignment,
- duplicate removal,
- structural verification,
- corpus quality auditing.

---

### Objective 2 — Perform Semantic Validation Prior to Training

Rather than relying exclusively on lexical similarity, the project sought to ensure that multilingual program pairs represented equivalent computational behaviour.

Accordingly, the validation pipeline incorporated:

- Python AST parsing,
- Java compilation,
- Tree-sitter structural validation,
- Cross-language Semantic Consistency Ratio (CSR),
- embedding-based semantic similarity,
- teacher-assisted repair.

Only validated examples progressed into the approved corpus.

---

### Objective 3 — Develop Standardized Prompt Contracts

Another important objective involved eliminating prompt inconsistency across multiple programming tasks.

To achieve this, every training example was generated using a standardized Prompt Contract that explicitly defines:

- task identifier,
- source modality,
- target modality,
- expected output,
- formatting constraints,
- response headers,
- success criteria.

This approach ensures that every task follows a consistent instruction-following format despite producing different output modalities.

---

### Objective 4 — Build a Unified Multitask Dataset

Instead of developing separate datasets and models for each programming task, the project sought to maximize the usefulness of every validated corpus entry.

Each approved corpus row therefore generated six independent multitask instruction examples covering code generation, code translation, and program summarization.

This objective significantly increased data utilization while enabling a single model to learn complementary programming capabilities simultaneously.

---

### Objective 5 — Implement Parameter-Efficient Fine-Tuning

Training modern language models using full-parameter optimization is computationally expensive and impractical for many research environments.

Accordingly, RepoCoder Studio adopted Quantized Low-Rank Adaptation (QLoRA) to fine-tune the Qwen2.5-Coder-0.5B-Instruct model while updating fewer than one percent of the total model parameters.

This objective demonstrates that effective multilingual adaptation can be achieved without requiring large-scale computational infrastructure.

---

### Objective 6 — Design a Comprehensive Evaluation Framework

Programming tasks cannot be evaluated using a single metric.

Consequently, another objective involved designing an evaluation framework capable of measuring structural correctness, semantic equivalence, executable validity, and natural language quality across heterogeneous task families.

The final evaluation framework integrates:

- Python Parse Success
- Java Compilation Success
- CodeBLEU-lite
- Cross-language Semantic Consistency Ratio
- ROUGE-L
- SacreBLEU
- Sentence Embedding Similarity

This multi-metric strategy provides a considerably richer understanding of model behaviour than lexical similarity alone.

---

### Objective 7 — Ensure Engineering Reproducibility

The final objective focused on engineering reproducibility.

Every major stage of the implementation produces persistent artefacts including:

- validated corpora,
- prompt contracts,
- dataset summaries,
- training manifests,
- evaluation reports,
- comparison tables,
- failure analytics.

These artefacts allow experiments to be reproduced without reconstructing intermediate processing stages.

---

# 6. Project Scope

Clearly defining the scope of the project was essential to maintaining a focused implementation while avoiding unnecessary complexity.

Although modern software engineering encompasses numerous programming languages and tasks, RepoCoder Studio deliberately concentrates on a carefully selected subset of capabilities that collectively demonstrate the feasibility of a unified multilingual code intelligence framework.

The implementation scope was refined throughout development as lessons learned from earlier experiments informed subsequent engineering decisions.

---

## 6.1 Included Within Scope

The final implementation includes the following major capabilities.

### Multilingual Corpus Engineering

The project implements a complete multilingual corpus engineering pipeline responsible for acquiring, standardizing, validating, and organizing programming datasets before training.

---

### Semantic Validation

The implementation performs semantic and structural validation using multiple complementary techniques before freezing the approved corpus.

---

### Prompt Engineering

Standardized Prompt Contracts (Version 2.6) were developed to ensure consistent instruction formatting across every supported programming task.

---

### Six Multitask Learning Tasks

The final implementation supports six programming tasks:

- Natural Language → Python
- Natural Language → Java
- Python → Java
- Java → Python
- Python → Natural Language
- Java → Natural Language

---

### Parameter-Efficient Fine-Tuning

QLoRA-based fine-tuning of Qwen2.5-Coder-0.5B-Instruct forms the primary model adaptation strategy.

---

### Evaluation

Comprehensive evaluation includes baseline analysis, fine-tuned analysis, comparison reports, and failure analytics.

---

### Engineering Reproducibility

Version-controlled artefacts, manifests, configuration files, prompt hashes, and dataset summaries were incorporated throughout the implementation.

---

## 6.2 Outside the Scope

The following items were intentionally excluded from the final implementation.

### Full Parameter Fine-Tuning

Only parameter-efficient adaptation using QLoRA was implemented.

---

### Additional Programming Languages

Although the architecture can be extended to other languages, the final implementation focuses exclusively on Python and Java.

---

### Large Foundation Models

The project intentionally employs the compact Qwen2.5-Coder-0.5B model to demonstrate that strong performance can be achieved without extremely large computational resources.

---

### Trusted Execution Testing

Infrastructure for Trusted Test Repositories was successfully implemented.

However, the available datasets did not provide sufficiently reliable executable test suites following semantic validation.

Consequently, execution-based evaluation was marked **NOT_FEASIBLE** for the frozen implementation.

Rather than introducing unreliable execution metrics, the implementation relied on structural and semantic evaluation methodologies while identifying executable trusted tests as a future enhancement.

---

### Automated Java Repair

Although lightweight automatic Java repair was investigated, it was intentionally deferred to future work to preserve architectural stability following the implementation freeze.

---

### Continuous Online Learning

RepoCoder Studio performs supervised fine-tuning on a frozen corpus and does not implement continual or reinforcement-based learning.

---

# 7. Major Contributions

RepoCoder Studio makes several important engineering contributions beyond the development of a multitask language model.

Unlike many research implementations that primarily evaluate model architectures, this project demonstrates the importance of treating corpus engineering, validation, prompt design, and reproducibility as equal components of the overall system.

The major contributions are summarized below.

---

## Contribution 1 — Engineering-First Architecture

The project introduces a layered engineering architecture in which corpus validation precedes model training.

This architecture emphasizes data quality before model optimization and serves as the conceptual foundation for the entire implementation.

---

## Contribution 2 — Semantic Corpus Validation Pipeline

A comprehensive validation pipeline combining structural verification and semantic similarity was implemented to ensure that only reliable multilingual program pairs were admitted into the approved corpus.

---

## Contribution 3 — Standardized Prompt Contracts

Prompt Contract Version 2.6 establishes a unified instruction format supporting six heterogeneous programming tasks while minimizing prompt inconsistency.

---

## Contribution 4 — Unified Multitask Dataset Construction

Every validated corpus row generates six instruction-following examples, significantly increasing dataset utilization while enabling multitask learning within a single model.

---

## Contribution 5 — Efficient QLoRA Adaptation

The project demonstrates successful parameter-efficient fine-tuning using fewer than one percent of the model parameters, making the implementation feasible within modest computational resources.

---

## Contribution 6 — Comprehensive Evaluation Framework

Rather than relying on a single performance metric, RepoCoder Studio integrates structural, semantic, lexical, and compilation-based evaluation techniques appropriate to each task family.

---

## Contribution 7 — Comparison and Failure Analytics

Dedicated comparison and failure analysis subsystems provide detailed insight into model improvements and remaining limitations, supporting evidence-based engineering refinement.

---

# 8. Report Organization

This report follows a top-down engineering narrative designed to introduce concepts before implementation details.

Following this introductory chapter, Chapter 2 presents the overall architecture of RepoCoder Studio and explains the interaction between major engineering components.

Subsequent chapters describe dataset engineering, semantic validation, prompt contract design, multitask dataset construction, parameter-efficient fine-tuning, evaluation methodology, and experimental results.

The final chapters discuss engineering lessons learned throughout implementation, limitations of the current system, opportunities for future improvement, and concluding observations regarding the effectiveness of the proposed framework.

This organization enables readers unfamiliar with multilingual code intelligence to understand not only **how** RepoCoder Studio was implemented, but more importantly **why** each engineering decision was made.

---

# Chapter Summary

This chapter introduced the motivation, objectives, scope, and major contributions of RepoCoder Studio. Collectively, these sections establish the engineering philosophy underpinning the entire project: robust multilingual code intelligence begins with trustworthy data, standardized interfaces, and reproducible engineering practices rather than model complexity alone.

With the project context now established, the next chapter examines the overall system architecture and explains how the various engineering components interact to form a complete end-to-end multilingual code intelligence pipeline.


# Chapter 2  
# Overall System Architecture

---

## 2.1 Introduction

Having established the motivation, objectives, and scope of RepoCoder Studio in the previous chapter, the discussion now shifts from *why* the project was undertaken to *how* the final engineering solution was designed and implemented.

One of the primary lessons learned during the early stages of implementation was that successful multilingual code intelligence cannot be achieved simply by selecting a powerful pretrained language model. Initial experiments repeatedly demonstrated that improvements in model architecture alone produced inconsistent gains whenever the underlying training corpus contained semantically inconsistent or structurally invalid examples.

This observation fundamentally changed the project's engineering direction.

Rather than designing a model-centric pipeline, RepoCoder Studio was redesigned as a **data-centric engineering framework** in which every downstream stage depends upon the successful completion of the previous stage. Consequently, the overall architecture places corpus engineering, semantic validation, prompt standardization, and reproducibility ahead of model training. The language model itself therefore becomes only one component within a much larger engineering ecosystem.

This architectural philosophy distinguishes RepoCoder Studio from many existing implementations that primarily focus on neural architectures while treating data preparation as a preliminary preprocessing activity.

---

# 2.2 Architectural Design Philosophy

The final architecture was guided by several engineering principles that remained unchanged after the architecture freeze.

Instead of optimizing individual notebook cells independently, every component was designed to satisfy one or more overarching engineering objectives.

The major architectural principles adopted throughout the implementation are discussed below.

---

## Data Quality Before Model Quality

The most important engineering principle adopted by RepoCoder Studio is that improvements in dataset quality generally produce larger performance gains than increasing model complexity.

Consequently, all downloaded datasets are initially regarded as **candidate datasets** rather than trusted training resources.

Every candidate sample must successfully pass structural validation, semantic validation, and consistency verification before becoming part of the approved corpus.

Only after corpus validation is complete does model training begin.

This ordering significantly reduces the probability of introducing noisy supervision into the fine-tuning process.

---

## Validation Before Training

Traditional machine learning workflows often merge data cleaning directly into the training pipeline.

RepoCoder Studio intentionally separates these concerns.

Corpus validation is treated as an independent engineering subsystem that produces a frozen validated corpus.

Once validation has completed, the resulting corpus is considered immutable for the remainder of the experiment.

This separation provides several advantages:

- reproducibility,
- deterministic dataset construction,
- simplified debugging,
- repeatable experiments,
- independent validation auditing.

---

## Modular Engineering

Every major subsystem within RepoCoder Studio performs a clearly defined responsibility.

Rather than creating one large monolithic notebook, implementation responsibilities are divided among specialized modules responsible for:

- corpus engineering,
- validation,
- prompt construction,
- multitask dataset generation,
- training,
- evaluation,
- comparison,
- analytics.

This modular design significantly improves maintainability while allowing individual subsystems to evolve independently.

---

## Reproducibility

Engineering reproducibility was considered a first-class design requirement.

Every major processing stage generates persistent artefacts including:

- validated datasets,
- dataset summaries,
- prompt contracts,
- prompt hashes,
- training manifests,
- evaluation summaries,
- comparison tables,
- failure analytics.

These artefacts ensure that experimental results can be reproduced without repeating computationally expensive preprocessing stages.

---

## Parameter Efficiency

Large language models continue to increase dramatically in size.

Training all parameters of modern foundation models is beyond the computational resources available in many academic environments.

Consequently, RepoCoder Studio adopts Quantized Low-Rank Adaptation (QLoRA) to fine-tune only a very small subset of model parameters.

This strategy enables efficient experimentation while preserving most pretrained knowledge.

---

# 2.3 High-Level System Architecture

The complete implementation consists of a sequence of interconnected engineering stages.

Each stage consumes validated outputs from the previous stage while producing reusable artefacts for downstream processing.

The overall architecture is illustrated conceptually below.

```text
                Public Programming Datasets
                           │
                           ▼
                 Dataset Acquisition Layer
                           │
                           ▼
              Standardisation & Normalisation
                           │
                           ▼
              Semantic Validation Pipeline
                           │
                           ▼
                 Approved Multilingual Corpus
                           │
                           ▼
                 Prompt Contract Generation
                           │
                           ▼
               Multitask Dataset Construction
                           │
                           ▼
             Hugging Face Dataset Preparation
                           │
                           ▼
             QLoRA Fine-Tuning Pipeline
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
      Baseline Evaluation       Fine-Tuned Evaluation
              │                         │
              └────────────┬────────────┘
                           ▼
               Comparison & Analytics
                           │
                           ▼
                Final Model Packaging
```

Although this workflow appears sequential, every stage produces independently reusable outputs that may be inspected or reused without repeating previous computations.

---

# 2.4 End-to-End Workflow

The implementation proceeds through nine major engineering stages.

---

## Stage 1 — Dataset Acquisition

The workflow begins by acquiring publicly available programming datasets from trusted repositories.

Rather than immediately treating these datasets as training data, every record is imported into a common internal representation suitable for further validation.

This abstraction simplifies downstream processing by eliminating dataset-specific implementation details.

---

## Stage 2 — Corpus Engineering

Once acquired, datasets undergo extensive preprocessing.

This stage performs:

- metadata normalization,
- duplicate removal,
- language verification,
- schema standardization,
- corpus indexing,
- split preservation.

At this stage, no semantic assumptions are made regarding program correctness.

The objective is merely to organize heterogeneous datasets into a consistent engineering representation.

---

## Stage 3 — Semantic Validation

Semantic validation represents the core innovation of RepoCoder Studio.

Every candidate example undergoes multiple independent validation procedures before admission into the approved corpus.

Validation techniques include:

- Python Abstract Syntax Tree parsing,
- Java compilation,
- Tree-sitter structural verification,
- semantic embedding similarity,
- Cross-language Semantic Consistency Ratio,
- duplicate detection,
- teacher-assisted repair.

Examples failing validation are removed or repaired before corpus freezing.

---

## Stage 4 — Approved Corpus Construction

After successful validation, all remaining examples become part of the **Approved Corpus**.

The approved corpus represents the only dataset used during downstream multitask dataset construction.

Importantly, the approved corpus is frozen prior to model training.

No additional modifications are performed afterwards.

This guarantees that every experimental run operates on exactly the same validated dataset.

---

## Stage 5 — Prompt Contract Generation

Every approved corpus entry is converted into a standardized instruction-following example.

Prompt Contract Version 2.6 defines:

- task identifier,
- source modality,
- target modality,
- instruction,
- response header,
- output contract,
- success criteria,
- formatting constraints.

This standardization eliminates instruction drift while ensuring consistent interaction across every supported programming task.

---

## Stage 6 — Multitask Dataset Construction

Each approved corpus entry generates six separate instruction-following examples.

These correspond to:

| Task | Description |
|------|-------------|
| T1 | Natural Language → Python |
| T2 | Natural Language → Java |
| T3 | Python → Java |
| T4 | Java → Python |
| T5 | Python → Natural Language |
| T6 | Java → Natural Language |

Instead of creating independent datasets for each task, all six task families are merged into one multitask dataset.

This strategy significantly improves dataset utilization while encouraging transfer learning across related programming capabilities.

---

## Stage 7 — Parameter-Efficient Fine-Tuning

The multitask dataset is converted into Hugging Face datasets suitable for supervised instruction tuning.

Fine-tuning is performed using:

- Qwen2.5-Coder-0.5B-Instruct
- QLoRA
- 4-bit quantization
- Low-Rank Adaptation

Only approximately **0.88%** of total model parameters are updated during training.

This dramatically reduces GPU memory requirements while maintaining strong downstream performance.

---

## Stage 8 — Evaluation

Both the pretrained baseline and fine-tuned models are evaluated using identical datasets.

Evaluation is task-aware.

Programming tasks employ structural metrics including:

- Python Parse Success,
- Java Compilation Success,
- CodeBLEU-lite,
- CSR Similarity.

Natural language tasks employ:

- ROUGE-L,
- SacreBLEU,
- Semantic Similarity.

This multi-metric evaluation provides a more complete understanding of model behaviour than lexical similarity alone.

---

## Stage 9 — Comparative Analytics

The final stage compares baseline and fine-tuned performance across all six tasks.

Comparison reports include:

- overall improvement tables,
- task-level comparisons,
- metric deltas,
- failure categorization,
- dominant failure modes,
- engineering observations.

These reports form the basis for the discussion presented in later chapters.

---

# 2.5 Architectural Layers

Although implemented as a sequential pipeline, RepoCoder Studio can also be understood as a layered architecture.

The architecture consists of five conceptual layers.

### Layer 1 — Data Layer

Responsible for dataset acquisition, storage, versioning, and normalization.

---

### Layer 2 — Validation Layer

Responsible for structural verification, semantic alignment, teacher repair, and corpus freezing.

---

### Layer 3 — Learning Layer

Responsible for prompt engineering, multitask dataset construction, and parameter-efficient fine-tuning.

---

### Layer 4 — Evaluation Layer

Responsible for baseline evaluation, fine-tuned evaluation, comparison, and failure analytics.

---

### Layer 5 — Reproducibility Layer

Responsible for manifests, configuration management, dataset summaries, experiment traceability, and model packaging.

Unlike the remaining layers, this layer spans the entire architecture and supports every engineering stage.

---

# 2.6 Why the Architecture Changed During Implementation

The final architecture differs substantially from the earliest project prototypes.

During development several important engineering decisions were made as empirical evidence accumulated.

Among the most significant changes were:

- removal of CodeAlpaca from supervised training,
- removal of APPS due to loader complexity and inconsistent schemas,
- adoption of MBPP as the authoritative Stage 2 training dataset,
- removal of TransCoder and multilingual mirror datasets,
- adoption of XLCoST as the sole Stage 3 multilingual corpus,
- freezing Prompt Contract Version 2.6,
- retaining teacher-repaired samples following corpus validation,
- introducing comparison and failure analytics as dedicated engineering subsystems,
- adopting CodeBLEU-lite after identifying incompatibilities between the official CodeBLEU implementation and the Python 3.12 dependency stack.

These decisions collectively simplified the implementation while improving reproducibility, maintainability, and overall system reliability.

---

# Chapter Summary

This chapter presented the overall engineering architecture implemented within RepoCoder Studio. The architecture reflects a deliberate transition from model-centric experimentation toward data-centric engineering, emphasizing corpus quality, semantic validation, prompt standardization, and reproducibility before model optimization.

Having established the overall architecture, the next chapter examines the engineering of the multilingual datasets themselves, describing how heterogeneous public resources were transformed into the validated corpus used throughout the remainder of the implementation.

# Chapter 3  
# Dataset Engineering and Corpus Construction

---

## 3.1 Introduction

The performance of any machine learning system is fundamentally constrained by the quality of the data used during training. This principle is particularly important in multilingual code intelligence, where datasets consist not only of natural language descriptions but also executable source code, translated implementations, documentation, metadata, and evaluation artefacts. Unlike conventional natural language datasets, programming datasets must preserve syntactic correctness, semantic equivalence, and executable behaviour across multiple programming languages simultaneously.

For this reason, dataset engineering became one of the most significant components of RepoCoder Studio. Rather than downloading publicly available datasets and using them directly for supervised learning, the project implemented a dedicated corpus engineering pipeline responsible for acquiring, standardizing, validating, and organizing multilingual programming examples before any model training occurred.

This chapter describes the engineering methodology adopted to transform heterogeneous public datasets into a high-quality multilingual corpus suitable for multitask instruction tuning.

---

# 3.2 Why Dataset Engineering Matters

During the initial implementation stages, multiple publicly available datasets were evaluated for inclusion within the training pipeline. Although these datasets are widely used throughout the research community, practical experimentation quickly revealed that they differed substantially in structure, quality, and suitability for the intended multitask learning objectives.

Several recurring issues were identified.

Some datasets contained duplicated implementations under different problem descriptions. Others provided incomplete documentation or omitted executable test cases entirely. Certain multilingual repositories contained language pairs that were syntactically correct but semantically inconsistent, while instruction-tuning datasets frequently mixed executable source code with explanatory prose or markdown formatting.

If incorporated directly into supervised fine-tuning, these inconsistencies would encourage the language model to learn ambiguous or contradictory mappings. Consequently, improving dataset quality became considerably more valuable than simply increasing dataset size.

These observations fundamentally changed the engineering philosophy of RepoCoder Studio. Instead of maximizing the number of training examples, the implementation sought to maximize the trustworthiness of every retained example.

---

# 3.3 Dataset Selection Strategy

The selection of datasets was guided by three primary principles:

1. **Structural Reliability** – datasets should provide syntactically correct source code that can be validated through parsing or compilation.

2. **Semantic Consistency** – corresponding language pairs should describe equivalent computational behaviour.

3. **Task Relevance** – datasets should directly support one or more of the six programming tasks implemented by RepoCoder Studio.

Rather than relying on a single dataset throughout the project, different datasets were selected according to the requirements of individual implementation stages.

---

# 3.4 Stage 2 Dataset Selection

Stage 2 focused on Natural Language → Python code generation.

Several candidate datasets were initially evaluated.

### MBPP

MBPP (Mostly Basic Programming Problems) contains short algorithmic programming tasks accompanied by executable Python reference implementations. Its clean structure, relatively consistent documentation, and availability of evaluation benchmarks made it highly suitable for supervised fine-tuning.

MBPP therefore became the primary training dataset for Stage 2.

---

### HumanEval

HumanEval was incorporated exclusively as an evaluation benchmark.

Keeping HumanEval separate from the supervised training dataset prevents benchmark leakage while providing an independent measure of generalization performance.

---

### EvalPlus

EvalPlus extends HumanEval by introducing more comprehensive evaluation tests.

Whenever available within the execution environment, EvalPlus was included as an additional evaluation benchmark without contributing training examples.

---

### CodeAlpaca

Early implementation prototypes included CodeAlpaca as part of the supervised training corpus.

Although CodeAlpaca contains a large number of instruction-following programming examples, practical experimentation revealed several limitations.

These included:

- inconsistent formatting,
- explanatory prose mixed with executable code,
- lack of trusted executable tests,
- instruction-tuning objectives that differed from deterministic code generation.

Following repeated experiments, CodeAlpaca was removed entirely from the supervised training pipeline.

---

### APPS

The APPS benchmark initially appeared attractive due to its extensive collection of competitive programming problems and executable tests.

However, practical integration introduced substantial engineering complexity.

Observed issues included:

- inconsistent schema,
- loader failures,
- prolonged preprocessing,
- significant implementation overhead.

Since MBPP already satisfied the primary training objectives with considerably lower engineering complexity, APPS was removed from the final implementation.

---

## Final Stage 2 Dataset Decision

The frozen Stage 2 configuration therefore became:

| Purpose | Dataset |
|---------|---------|
| Training | MBPP Train |
| Validation | MBPP Validation |
| Evaluation | MBPP Test |
| Evaluation | HumanEval |
| Evaluation | EvalPlus (when available) |

This simplified configuration improved reproducibility while eliminating unnecessary engineering complexity.

---

# 3.5 Stage 3 Dataset Selection

Stage 3 focused on multilingual source code translation between Python and Java.

Unlike Stage 2, this stage required datasets containing semantically aligned implementations across multiple programming languages.

Initially, several multilingual resources were investigated.

---

### XLCoST

XLCoST provides multilingual programming problems accompanied by implementations in several programming languages.

Unlike many multilingual datasets, XLCoST maintains relatively consistent problem descriptions while supporting multiple language configurations.

This made it highly suitable for constructing translation pairs.

The final implementation uses the official Hugging Face dataset:

```
codeparrot/xlcost-text-to-code
```

using the explicit configurations:

- Python-program-level
- Java-program-level

---

### TransCoder

TransCoder was initially evaluated as an additional multilingual source.

However, integrating multiple multilingual repositories substantially increased alignment complexity.

Maintaining two independent multilingual datasets introduced:

- duplicate translation pairs,
- inconsistent schemas,
- loader instability,
- additional preprocessing overhead.

After careful evaluation, TransCoder was removed from the frozen implementation.

---

### Mirror Datasets

Several mirror repositories were also considered during implementation.

These were ultimately discarded because maintaining multiple copies of essentially identical multilingual data complicated reproducibility without providing measurable improvements.

---

## Final Stage 3 Dataset Decision

The frozen implementation therefore adopted a single authoritative multilingual source:

| Dataset | Purpose |
|----------|---------|
| XLCoST | Python ↔ Java translation |

This simplified downstream validation while significantly improving engineering reproducibility.

---

# 3.6 Combined Stage Dataset Construction

The final Combined Stage integrates validated examples from both implementation stages into a unified multitask corpus.

Rather than maintaining separate training datasets for each programming task, validated corpus entries are transformed into six independent instruction-following examples.

The resulting multitask dataset forms the foundation of the final instruction-tuning process.

After semantic validation and corpus approval, the final dataset consisted of:

| Property | Value |
|----------|------:|
| Approved Corpus Rows | 403 |
| Multitask Examples | 2418 |
| Supported Tasks | 6 |

---

## Dataset Split

To ensure reproducible experimentation, the multitask dataset preserves explicit training, validation, and testing partitions.

The final dataset distribution is shown below.

| Split | Examples |
|-------|----------:|
| Training | 1776 |
| Validation | 342 |
| Testing | 300 |

Maintaining fixed dataset partitions throughout experimentation ensured that baseline and fine-tuned evaluations remained directly comparable.

---

# 3.7 Why Candidate Rows Were Not Automatically Trusted

One of the defining engineering principles of RepoCoder Studio is that downloaded datasets should not automatically be treated as training data.

Every imported record initially exists only as a **candidate corpus entry**.

Only after successfully passing structural verification and semantic validation does the record become part of the approved corpus.

This philosophy differs substantially from many conventional machine learning pipelines, where preprocessing primarily consists of formatting rather than verification.

By explicitly distinguishing between candidate data and approved data, RepoCoder Studio significantly reduces the likelihood of introducing noisy supervision into downstream model training.

---

# 3.8 Dataset Engineering Pipeline

The dataset engineering process consists of several sequential stages.

```
Dataset Acquisition
        │
        ▼
Standardization
        │
        ▼
Metadata Normalization
        │
        ▼
Duplicate Removal
        │
        ▼
Semantic Validation
        │
        ▼
Approved Corpus
        │
        ▼
Prompt Contract Generation
        │
        ▼
Multitask Dataset Construction
```

Each stage produces reusable artefacts that can be independently inspected, audited, and reproduced.

This modular workflow greatly simplified debugging during implementation while ensuring that downstream model training operated exclusively on validated multilingual examples.

---

# Chapter Summary

This chapter described the dataset engineering strategy adopted by RepoCoder Studio. Rather than maximizing dataset size, the implementation emphasized corpus quality through careful dataset selection, simplification of the training pipeline, and explicit separation between candidate and approved corpus entries.

The next chapter builds upon this foundation by examining the semantic validation pipeline in detail, explaining how structural verification, semantic alignment, and teacher-assisted repair were combined to produce the frozen multilingual corpus used throughout the remainder of the implementation.

# Chapter 4  
# Semantic Validation and Corpus Construction

---

# 4.1 Introduction

One of the most important engineering contributions of RepoCoder Studio is the introduction of a dedicated semantic validation pipeline. Unlike many machine learning workflows that assume publicly available datasets are inherently suitable for supervised learning, RepoCoder Studio adopts a fundamentally different philosophy.

Every downloaded dataset entry is initially regarded as **untrusted**.

Rather than immediately entering the training corpus, each candidate record must successfully pass a sequence of structural and semantic validation procedures before being approved. Only after satisfying these requirements is the example permitted to participate in multitask dataset construction.

This design decision emerged directly from observations made during early experimentation. Initial prototypes that trained directly on downloaded datasets produced inconsistent performance improvements despite using strong pretrained language models. Investigation revealed that noisy supervision originating from inconsistent datasets often degraded downstream learning.

Consequently, semantic validation became one of the core architectural components of the final frozen implementation.

---

# 4.2 Why Semantic Validation is Necessary

Programming datasets differ significantly from conventional natural language corpora.

For natural language applications, minor wording differences often preserve meaning. Programming languages, however, require exact structural and behavioural correctness. A single missing bracket, incorrect variable type, or mismatched algorithm can completely change program execution.

Similarly, multilingual programming datasets introduce an additional challenge.

Two source files written in different programming languages may look entirely different while remaining computationally equivalent.

Conversely, programs exhibiting nearly identical lexical structure may produce entirely different outputs.

Therefore, lexical similarity alone cannot reliably determine whether two multilingual implementations describe the same algorithm.

These observations motivated the adoption of multiple complementary validation procedures capable of evaluating structural correctness, semantic consistency, and multilingual alignment simultaneously.

---

# 4.3 Validation Objectives

The semantic validation pipeline was designed to answer five fundamental questions for every candidate corpus entry.

1. **Is the source code structurally valid?**

2. **Does the documentation accurately describe the implementation?**

3. **Do multilingual implementations represent the same algorithm?**

4. **Can noisy examples be safely repaired?**

5. **Should this example be admitted into the approved corpus?**

Only when sufficient evidence exists to answer these questions positively does the example become part of the frozen multilingual corpus.

---

# 4.4 Semantic Validation Pipeline

The complete validation workflow implemented within RepoCoder Studio is illustrated below.

```text
Candidate Dataset
        │
        ▼
Language Verification
        │
        ▼
Structural Validation
        │
        ▼
Semantic Similarity Analysis
        │
        ▼
Cross-language Alignment
        │
        ▼
Teacher-assisted Repair
        │
        ▼
Corpus Approval Decision
        │
        ▼
Approved Multilingual Corpus
```

Each validation stage contributes independent evidence regarding the trustworthiness of the candidate example.

Rather than relying upon a single validation criterion, the final approval decision combines multiple complementary signals.

---

# 4.5 Structural Validation

The first stage of validation verifies that every source code fragment satisfies the structural requirements of its corresponding programming language.

This stage deliberately focuses on syntactic correctness rather than algorithmic behaviour.

Examples failing structural validation are removed immediately because subsequent semantic analysis cannot reliably interpret syntactically invalid programs.

Different validation procedures are applied depending upon the target programming language.

---

## Python Validation

Python implementations undergo Abstract Syntax Tree (AST) parsing.

Using Python's built-in parser ensures that generated syntax is structurally valid before further processing.

The parser verifies:

- balanced syntax,
- valid indentation,
- correct function definitions,
- executable program structure.

Programs failing AST parsing are excluded from the approved corpus.

---

## Java Validation

Java implementations are validated using compiler-based verification.

Unlike Python, Java requires considerably more structural information before compilation succeeds.

Compilation verifies:

- class definitions,
- method declarations,
- balanced braces,
- type correctness,
- language syntax.

Only successfully compiling programs proceed to subsequent semantic validation stages.

---

# 4.6 Tree-sitter Structural Analysis

While language parsers verify syntactic correctness, they provide relatively limited information regarding higher-level program structure.

To obtain richer structural information, RepoCoder Studio incorporates **Tree-sitter** for Java structural analysis.

Tree-sitter constructs detailed parse trees describing the internal structure of source code.

This enables validation beyond simple compilation by identifying:

- class declarations,
- method hierarchies,
- nested control structures,
- statement organization,
- abstract syntax relationships.

Tree-sitter therefore provides an additional structural verification layer that complements compiler-based validation.

Its inclusion significantly improved confidence in multilingual alignment throughout corpus construction.

---

# 4.7 Semantic Similarity Analysis

Structural correctness alone does not guarantee semantic correctness.

Two syntactically valid programs may solve entirely different problems.

Consequently, semantic similarity analysis forms the second major component of the validation pipeline.

Rather than comparing programs lexically, semantic representations are generated using pretrained embedding models.

These embeddings capture high-level algorithmic meaning rather than exact textual content.

Similarity between corresponding representations is then computed using embedding-based distance metrics.

Examples exhibiting sufficiently strong semantic agreement are considered suitable candidates for multilingual alignment.

---

# 4.8 Cross-language Semantic Consistency Ratio (CSR)

One of the most important innovations introduced during implementation is the **Cross-language Semantic Consistency Ratio (CSR).**

CSR provides a quantitative estimate of semantic agreement between corresponding multilingual artefacts.

Unlike lexical similarity measures, CSR attempts to evaluate whether different language representations preserve equivalent computational meaning.

For example,

- Natural Language ↔ Python
- Natural Language ↔ Java
- Python ↔ Java

should all describe the same underlying algorithm despite differing substantially in vocabulary and syntax.

Higher CSR values indicate stronger semantic agreement between representations.

During implementation CSR was used extensively during:

- corpus validation,
- dataset approval,
- evaluation,
- comparison analytics.

Because CSR directly reflects semantic consistency rather than textual overlap, it became one of the primary engineering metrics used throughout the project.

---

# 4.9 Duplicate Detection

Large multilingual datasets frequently contain duplicated or near-duplicated implementations.

Training repeatedly on identical algorithms unnecessarily biases model learning while artificially inflating dataset size.

Accordingly, duplicate detection formed another important stage within the corpus engineering pipeline.

Duplicate analysis considered:

- repeated documentation,
- repeated source code,
- repeated multilingual pairs,
- repeated metadata.

Removing duplicate examples improved corpus diversity while reducing unnecessary computational overhead during fine-tuning.

---

# 4.10 Teacher-Assisted Repair

During implementation it became evident that not every invalid corpus entry should necessarily be discarded.

Many examples contained only minor inconsistencies such as:

- formatting problems,
- incomplete documentation,
- metadata inconsistencies,
- trivial structural defects.

Removing all such examples would unnecessarily reduce corpus size.

Instead, RepoCoder Studio incorporates a **teacher-assisted repair** stage.

Where sufficient confidence existed, lightweight corrections were applied before validation resumed.

Examples successfully repaired subsequently re-entered the validation pipeline.

Only repaired examples satisfying all validation requirements were admitted into the approved corpus.

This strategy preserved valuable multilingual examples while maintaining corpus quality.

---

# 4.11 Approved Corpus

After all validation stages completed successfully, surviving examples were frozen into the Approved Corpus.

Unlike candidate datasets, the Approved Corpus represents trusted multilingual supervision suitable for downstream instruction tuning.

For the final implementation:

| Property | Value |
|----------|------:|
| Approved Corpus Rows | **403** |
| Validation Status | Approved |
| Teacher Repair | Retained after validation |
| Prompt Version | prompt_contract_v2.6 |

Every subsequent engineering stage—including prompt generation, multitask dataset construction, training, and evaluation—operates exclusively on this frozen approved corpus.

No additional corpus modifications are performed after approval.

This immutability significantly improves experimental reproducibility.

---

# 4.12 Why Execution-Based Trusted Tests Were Not Used

Originally, RepoCoder Studio planned to incorporate trusted executable unit tests as part of corpus validation.

The intention was to evaluate semantic equivalence through actual program execution rather than structural similarity alone.

Accordingly, infrastructure supporting Trusted Test Repositories was implemented within the engineering framework.

However, practical experimentation revealed an important limitation.

The validated multilingual corpus did not contain sufficiently reliable executable test suites after semantic filtering.

The final repository summary showed:

| Metric | Value |
|---------|------:|
| Approved Corpus Rows | 403 |
| Rows with Trusted Tests | 0 |
| Candidate Tests | 0 |
| Execution Status | NOT_FEASIBLE |

Rather than generating synthetic tests of uncertain quality merely to satisfy an evaluation objective, the project intentionally chose not to perform execution-based validation.

This decision reflects an important engineering principle:

> **Reliable evaluation is preferable to artificially inflated evaluation.**

Consequently, structural validation, semantic similarity, CSR analysis, parsing, and compilation remained the authoritative validation procedures for the frozen implementation.

Execution-based trusted testing is therefore identified as one of the principal opportunities for future work.

---

# 4.13 Lessons Learned During Corpus Validation

Corpus validation was one of the most iterative components of the project.

Several important engineering lessons emerged during implementation.

The first lesson was that public datasets should never be assumed trustworthy without independent verification.

The second lesson was that structural correctness alone does not imply semantic correctness.

The third lesson demonstrated that modest repair strategies can preserve valuable multilingual examples without sacrificing corpus quality.

Finally, the implementation confirmed that careful validation produces substantially greater downstream benefits than simply increasing corpus size.

These lessons strongly influenced every subsequent architectural decision adopted throughout RepoCoder Studio.

---

# Chapter Summary

This chapter described the semantic validation methodology responsible for transforming heterogeneous public datasets into the frozen multilingual corpus used throughout RepoCoder Studio.

By combining structural verification, semantic similarity analysis, Tree-sitter parsing, Cross-language Semantic Consistency Ratio (CSR), duplicate detection, and teacher-assisted repair, the implementation ensures that only trustworthy examples participate in downstream multitask learning.

The following chapter builds upon this validated corpus by describing the design of Prompt Contract Version 2.6 and explaining how standardized prompt engineering enabled the construction of the unified six-task multitask dataset used during fine-tuning.

# Chapter 5  
# Prompt Contract Design and Multitask Dataset Construction

---

# 5.1 Introduction

Once the multilingual corpus had been semantically validated and frozen, the next engineering challenge involved transforming heterogeneous programming artefacts into a standardized instruction-following dataset suitable for supervised fine-tuning.

Although the approved corpus consisted of reliable programming examples, the records originated from multiple datasets developed for different research objectives. Consequently, the representation of programming tasks varied considerably. Some datasets described algorithms using natural language, others contained only source code, while multilingual datasets primarily focused on code translation. Simply concatenating these datasets would have resulted in inconsistent instruction formats, ambiguous output expectations, and reduced learning efficiency.

To overcome this challenge, RepoCoder Studio introduced a **Prompt Contract Framework**, which defines a standardized interface between the dataset and the language model. Every approved corpus entry is transformed into one or more instruction-following examples using an identical prompt structure regardless of the original dataset source.

This standardization became one of the defining engineering features of the project and ultimately enabled the successful construction of a unified multitask instruction dataset.

---

# 5.2 Why Prompt Contracts Were Necessary

Large Language Models are highly sensitive to the way instructions are presented during supervised fine-tuning.

Even when the desired output remains identical, variations in prompt wording, formatting, response headers, or task descriptions may introduce undesirable inconsistencies into the learning process. When training examples originate from multiple independent datasets, such inconsistency becomes unavoidable unless a common interface is established.

Early implementation experiments revealed several practical issues:

- inconsistent instruction wording,
- varying response formats,
- mixed markdown and executable code,
- explanatory prose interleaved with source code,
- inconsistent output delimiters,
- missing task descriptions.

Although these inconsistencies appear relatively minor when viewed individually, collectively they introduce noise that makes supervised learning more difficult.

Consequently, the implementation adopted the principle that **every interaction between the model and the dataset should follow an explicit contract**.

---

# 5.3 Concept of a Prompt Contract

A Prompt Contract may be viewed as a formal agreement between the dataset and the language model.

Rather than merely providing an instruction, the contract explicitly specifies:

- the programming task,
- the role of the language model,
- the desired objective,
- expected output modality,
- formatting requirements,
- prohibited output forms,
- validation constraints,
- success criteria.

This approach eliminates ambiguity while encouraging the model to learn a consistent response style across all supported programming tasks.

Unlike conventional prompts, Prompt Contracts are intentionally deterministic. Every example belonging to a given task family follows the same structural template regardless of dataset origin.

---

# 5.4 Evolution of Prompt Contracts

Prompt engineering evolved considerably throughout implementation.

Earlier versions primarily consisted of short natural language instructions followed directly by the programming problem. While sufficient for simple experimentation, these prompts exhibited inconsistent behaviour across different programming tasks.

As implementation progressed, several enhancements were introduced.

Intermediate versions incorporated explicit role definitions and output contracts.

The final implementation freezes **Prompt Contract Version 2.6**, which introduces:

- explicit task identifiers,
- task tokens,
- role definitions,
- source and target modality declarations,
- output contracts,
- expected response headers,
- formatting constraints,
- quality checks,
- success criteria,
- prompt hashes.

Freezing the prompt specification ensured that every experiment following the architecture freeze operated using identical instruction formatting.

---

# 5.5 Structure of Prompt Contract Version 2.6

Each prompt contract follows a hierarchical structure designed to maximize clarity while minimizing ambiguity.

A typical prompt contains the following sections:

```
Task Token

Task Contract

Role

Objective

Output Contract

Expected Response Header

Constraints

Quality Checks

Success Criteria

Instruction

Input

Expected Response
```

Each section performs a distinct engineering function.

---

## Task Token

The task token uniquely identifies the programming task being performed.

Examples include:

```
<TASK_NL_TO_PYTHON>

<TASK_NL_TO_JAVA>

<TASK_PYTHON_TO_JAVA>

<TASK_JAVA_TO_PYTHON>

<TASK_PYTHON_TO_NL>

<TASK_JAVA_TO_NL>
```

These tokens provide an explicit conditioning signal that enables a single model to distinguish among multiple programming tasks during multitask learning.

---

## Role Definition

The role section informs the language model of the behaviour expected for the current task.

For example:

```
Role:
You are a Python code generator.
```

or

```
Role:
You are a Java translator.
```

Explicit role conditioning significantly improves instruction consistency across heterogeneous tasks.

---

## Objective

The objective describes the intended transformation.

Examples include:

- Convert the programming task into executable Python.
- Translate Python into equivalent Java.
- Explain the supplied Java program.

Providing explicit objectives reduces ambiguity while reinforcing the expected behaviour.

---

## Output Contract

One of the most important additions introduced in Prompt Contract Version 2.6 is the Output Contract.

Rather than allowing unrestricted natural language responses, the contract explicitly specifies the expected output type.

Examples include:

```
Return Python source code only.

Return Java source code only.

Return a concise explanation only.
```

Output Contracts substantially reduced undesirable behaviours such as explanatory prose preceding executable code.

---

## Expected Response Header

The frozen implementation introduced standardized response headers.

Examples include:

```
### Python

### Java

### Java Translation

### Python Translation

### Explanation
```

These headers provide an explicit structural boundary between instructions and responses while simplifying downstream evaluation.

---

## Constraints

Prompt Contracts explicitly prohibit undesired output behaviour.

Typical constraints include:

- do not generate markdown fences,
- do not provide explanations unless requested,
- preserve intended algorithm,
- produce executable code,
- avoid pseudocode.

Including these constraints significantly reduced formatting inconsistencies during supervised fine-tuning.

---

## Quality Checks

Each task additionally specifies validation expectations.

Examples include:

For Python:

- parses successfully using AST,
- contains executable Python only.

For Java:

- compiles successfully,
- contains only Java source code.

These quality checks mirror the evaluation procedures performed later in the pipeline.

---

## Success Criteria

The final section defines what constitutes a successful response.

Typical criteria include:

- valid syntax,
- executable implementation,
- preservation of requested behaviour,
- absence of markdown,
- absence of explanatory prose.

Although these criteria are not enforced during generation, they reinforce the intended output characteristics during instruction tuning.

---

# 5.6 Prompt Version Control

Prompt consistency was treated as an important reproducibility concern.

Every generated training example therefore stores metadata describing:

- prompt version,
- prompt contract version,
- response header,
- prompt hash.

The prompt hash uniquely identifies the complete prompt used to generate a training example.

This enables later verification that experiments were performed using identical prompt specifications.

During the final implementation:

| Property | Value |
|----------|--------|
| Prompt Version | prompt_contract_v2.6 |
| Prompt Hash | Stored for every example |
| Response Header | Stored for every example |
| Prompt Contract Version | task_contract_v2.6 |

These metadata fields greatly improve experiment traceability.

---

# 5.7 Multitask Dataset Construction

Following prompt standardization, every approved corpus entry is expanded into multiple instruction-following examples.

Unlike conventional datasets where one input corresponds to one output, RepoCoder Studio deliberately maximizes the usefulness of each validated corpus entry.

Each approved row generates six complementary programming tasks.

This design significantly increases supervision while encouraging shared representations across related programming activities.

---

# 5.8 Supported Task Families

The final multitask dataset contains six task families.

---

## Task 1 — Natural Language → Python

The model receives a programming problem described in natural language.

Its objective is to generate executable Python source code implementing the requested behaviour.

Evaluation focuses primarily on Python parsing success together with structural similarity metrics.

---

## Task 2 — Natural Language → Java

This task mirrors Task 1 but targets Java instead of Python.

Evaluation primarily measures Java compilation success together with semantic similarity.

---

## Task 3 — Python → Java Translation

The model receives executable Python code.

Its objective is to generate semantically equivalent Java source code.

Unlike ordinary translation, behavioural preservation is considerably more important than lexical similarity.

---

## Task 4 — Java → Python Translation

The inverse of Task 3.

The model translates Java implementations into executable Python while preserving observable behaviour.

---

## Task 5 — Python → Natural Language

Given executable Python code, the model produces a concise natural language explanation describing the algorithm.

Evaluation emphasizes semantic similarity, ROUGE-L, and SacreBLEU.

---

## Task 6 — Java → Natural Language

Equivalent to Task 5 but beginning from Java source code.

---

# 5.9 Final Dataset Statistics

The final multitask dataset generated after prompt construction contains:

| Property | Value |
|----------|------:|
| Approved Corpus Rows | 403 |
| Task Families | 6 |
| Total Multitask Examples | 2418 |
| Training Examples | 1776 |
| Validation Examples | 342 |
| Test Examples | 300 |

Each task contributes exactly the same number of examples.

This balanced distribution prevents the language model from becoming biased toward any particular programming task during supervised fine-tuning.

---

# 5.10 Round-Robin Curriculum

Another important engineering decision involved balancing task presentation during training.

Instead of grouping examples by task, RepoCoder Studio employs a **Round-Robin Curriculum**.

The curriculum alternates among the six task families throughout dataset construction.

This provides two major benefits:

- prevents extended sequences of identical task types,
- encourages continual switching between programming objectives during training.

Such balanced exposure promotes more stable multitask learning.

---

# 5.11 Why a Unified Multitask Dataset Was Preferred

Maintaining six independent models would require:

- six training pipelines,
- six evaluation pipelines,
- six deployment workflows,
- significantly greater computational resources.

Instead, RepoCoder Studio demonstrates that a carefully engineered multitask dataset allows a single language model to support all six programming capabilities simultaneously.

Beyond computational efficiency, multitask learning also encourages transfer of knowledge between related programming tasks. Improvements learned during code generation frequently benefit translation tasks, while understanding source code semantics also assists automatic summarization.

Thus, multitask dataset construction not only reduces engineering complexity but also improves the overall learning capability of the resulting model.

---

# Chapter Summary

This chapter presented the Prompt Contract Framework and the methodology used to construct the final multitask instruction dataset. By introducing Prompt Contract Version 2.6, standardized response headers, explicit output contracts, and balanced six-task dataset generation, RepoCoder Studio transformed the validated multilingual corpus into a consistent instruction-tuning dataset suitable for parameter-efficient adaptation.

The next chapter describes the fine-tuning methodology adopted by the project, including model selection, QLoRA configuration, training strategy, reproducibility mechanisms, and implementation details.

# Chapter 6  
# LoRA Fine-Tuning and Training Pipeline

---

# 6.1 Introduction

The successful construction of a validated multilingual corpus and standardized multitask dataset established the foundation for the learning phase of RepoCoder Studio. The next stage of the implementation involved adapting a pretrained code-oriented Large Language Model (LLM) to perform the six supported software engineering tasks using the engineered instruction dataset.

Instead of training a language model from scratch, the project adopted **parameter-efficient fine-tuning**. This strategy leverages the extensive programming knowledge already contained within a pretrained foundation model while requiring only a very small number of additional trainable parameters.

This chapter describes the complete training methodology implemented in RepoCoder Studio, including model selection, Quantized Low-Rank Adaptation (QLoRA), training configuration, engineering decisions, reproducibility mechanisms, and practical implementation details.

---

# 6.2 Why Fine-Tuning Was Necessary

Large Language Models such as Qwen, DeepSeek-Coder, CodeLlama, and StarCoder are pretrained on enormous collections of publicly available source code. Consequently, these models already possess considerable knowledge of programming languages, algorithms, software libraries, and common coding patterns.

However, pretraining alone does not optimize the model for the specific multitask objectives addressed by RepoCoder Studio.

For example, although a pretrained model may understand Python syntax, it has not necessarily learned to respond using the precise Prompt Contract Version 2.6 adopted throughout this project. Likewise, it has not been explicitly optimized to translate between Python and Java using the semantic constraints imposed by the validated multilingual corpus.

Supervised fine-tuning bridges this gap by exposing the pretrained model to carefully engineered task-specific examples.

Rather than teaching the model programming from the beginning, fine-tuning specializes its existing knowledge toward the desired software engineering tasks.

---

# 6.3 Model Selection

Several open-source code-oriented language models were evaluated during the planning phase of the project.

The selection process considered multiple factors:

- programming capability,
- multilingual support,
- instruction-following performance,
- computational requirements,
- compatibility with parameter-efficient fine-tuning,
- practical execution within Google Colab.

Following this evaluation, the final implementation adopted:

| Property | Value |
|----------|--------|
| Base Model | Qwen2.5-Coder-0.5B-Instruct |
| Provider | Alibaba Cloud |
| Model Family | Qwen2.5-Coder |
| Parameters | ~498 Million |

The chosen model provides an effective compromise between programming capability and computational efficiency.

Unlike larger foundation models requiring high-end GPU infrastructure, Qwen2.5-Coder-0.5B can be fine-tuned successfully within the hardware limitations available during the project while still demonstrating strong programming performance.

---

# 6.4 Why QLoRA Was Selected

Fine-tuning every parameter of a modern Large Language Model is computationally expensive.

Updating hundreds of millions or billions of parameters requires substantial GPU memory, long training times, and significant storage requirements. Such resources are often unavailable in typical academic environments.

RepoCoder Studio therefore adopts **Quantized Low-Rank Adaptation (QLoRA)**.

QLoRA combines two complementary techniques:

- low-rank parameter adaptation,
- low-bit quantization.

Together these techniques dramatically reduce GPU memory consumption while preserving most of the performance achievable through full fine-tuning.

Rather than modifying every pretrained parameter, QLoRA introduces a small collection of trainable matrices that learn task-specific behaviour while leaving the original model weights unchanged.

This makes fine-tuning both computationally practical and highly efficient.

---

# 6.5 Low-Rank Adaptation (LoRA)

Low-Rank Adaptation is based upon a simple observation.

Although modern language models contain hundreds of millions of parameters, only a comparatively small subset needs to change in order to specialize the model toward a new task.

Instead of updating an entire weight matrix,

\[
W
\]

LoRA represents the required update as the product of two much smaller matrices:

\[
\Delta W = A \times B
\]

where:

- **A** is a low-rank projection matrix,
- **B** reconstructs the task-specific update.

The original pretrained parameters remain frozen throughout training.

Only these lightweight adaptation matrices are optimized.

Consequently, training becomes dramatically more memory efficient.

---

# 6.6 Four-Bit Quantization

An additional reduction in memory consumption was achieved through four-bit weight quantization.

Traditional neural networks store parameters using 16-bit or 32-bit floating-point representations.

QLoRA instead stores pretrained parameters using compact four-bit representations while temporarily reconstructing higher precision values during computation.

This approach significantly reduces GPU memory requirements without materially affecting downstream programming performance.

Combining LoRA with four-bit quantization enabled the complete training pipeline to execute successfully within the available Google Colab GPU resources.

---

# 6.7 Final Training Configuration

The final implementation adopted the configuration shown below.

| Parameter | Value |
|-----------|------|
| Base Model | Qwen2.5-Coder-0.5B-Instruct |
| Fine-Tuning Method | QLoRA |
| Quantization | 4-bit |
| Maximum Sequence Length | 1024 |
| Training Dataset | 1776 examples |
| Validation Dataset | 342 examples |
| Number of Tasks | 6 |
| Prompt Version | prompt_contract_v2.6 |

The configuration remained unchanged following the architecture freeze to ensure complete experimental reproducibility.

---

# 6.8 LoRA Configuration

The parameter-efficient adaptation process modified only a very small fraction of the complete model.

The final training statistics obtained during implementation are summarized below.

| Property | Value |
|----------|-------:|
| Total Parameters | 498,431,872 |
| Trainable Parameters | 4,399,104 |
| Percentage Trainable | 0.8826% |

These statistics illustrate one of the principal advantages of parameter-efficient fine-tuning.

Although fewer than one percent of the model parameters were updated, the resulting model demonstrated measurable improvements across nearly every supported programming task.

---

# 6.9 Training Dataset

Training utilized the multitask dataset generated in the previous chapter.

The final dataset consisted of:

| Dataset | Examples |
|----------|---------:|
| Training | 1776 |
| Validation | 342 |

Every example followed Prompt Contract Version 2.6.

Task ordering employed the round-robin curriculum strategy to ensure balanced exposure across all six programming objectives.

Because each approved corpus entry generated six instruction-following tasks, the model continually alternated among code generation, translation, and summarization throughout training.

---

# 6.10 Training Pipeline

The complete training workflow is illustrated below.

```text
Validated Corpus
        │
        ▼
Prompt Contract Generation
        │
        ▼
Multitask Dataset
        │
        ▼
HuggingFace Dataset
        │
        ▼
Tokenizer
        │
        ▼
QLoRA Preparation
        │
        ▼
LoRA Injection
        │
        ▼
Supervised Fine-Tuning
        │
        ▼
Adapter Saving
        │
        ▼
Final Model Packaging
```

Each stage produces reusable artefacts enabling interrupted experiments to resume safely without repeating earlier processing stages.

---

# 6.11 Engineering Reproducibility

Maintaining reproducibility throughout model training proved considerably more challenging than anticipated.

Several practical issues emerged during implementation, including:

- interrupted Colab sessions,
- GPU memory exhaustion,
- incompatible checkpoint formats,
- evolving dependency versions,
- PyTorch serialization changes.

Rather than treating these as isolated debugging issues, dedicated engineering mechanisms were incorporated into the pipeline.

These include:

- training manifests,
- prompt version tracking,
- configuration fingerprints,
- checkpoint compatibility verification,
- deterministic dataset summaries,
- saved evaluation reports.

These mechanisms ensure that future experiments can determine whether previously generated checkpoints remain compatible with the current implementation.

---

# 6.12 Checkpoint Management

Checkpoint management evolved substantially during implementation.

Initially, training resumed automatically whenever an existing checkpoint was detected.

However, practical experimentation revealed that checkpoints generated under earlier prompt contracts or configuration versions could silently introduce inconsistent behaviour.

To address this issue, the final implementation introduced manifest-based checkpoint verification.

Each checkpoint stores metadata describing:

- prompt contract version,
- task contract version,
- base model,
- configuration fingerprint.

Training resumes only if the checkpoint manifest matches the current implementation configuration.

Otherwise, training automatically begins from a clean initialization.

This approach greatly improves reproducibility while preventing accidental reuse of stale checkpoints.

---

# 6.13 Saving the Final Model

Following completion of training, the LoRA adapter is exported separately from the pretrained foundation model.

This design offers several practical advantages.

The relatively small adapter can be distributed independently while the original pretrained model is obtained directly from the Hugging Face Hub.

Consequently, storage requirements remain modest while deployment remains straightforward.

The final implementation also provides dedicated notebook utilities for:

- saving the trained adapter,
- reloading previously trained adapters,
- performing inference without retraining.

These utilities significantly reduce experimentation time during future evaluations.

---

# 6.14 Practical Challenges Encountered

Although the overall training procedure completed successfully, several engineering challenges arose throughout implementation.

Examples include:

- CUDA out-of-memory errors,
- evolving TRL API warnings,
- PyTorch checkpoint serialization changes,
- deprecated trainer parameters,
- checkpoint compatibility verification,
- dependency conflicts affecting evaluation.

Each issue was investigated systematically before incorporating an appropriate engineering solution into the final implementation.

Importantly, these challenges did not require redesigning the architecture.

Instead, they resulted in improvements to engineering robustness while preserving the frozen system design.

---

# 6.15 Final Training Outcome

Training completed successfully using the frozen multitask dataset and QLoRA configuration.

The model successfully learned all six supported programming tasks while updating fewer than one percent of the pretrained parameters.

The resulting LoRA adapter forms the primary artefact used during the evaluation phase discussed in the following chapter.

---

# Chapter Summary

This chapter described the training methodology adopted by RepoCoder Studio. By combining a validated multitask dataset with QLoRA-based parameter-efficient adaptation, the project successfully specialized the Qwen2.5-Coder model while requiring only 0.8826% of parameters to be updated.

Beyond the machine learning methodology itself, this chapter also highlighted the engineering decisions that improved reproducibility, checkpoint management, and long-term maintainability of the training pipeline.

The next chapter presents the evaluation methodology, explaining how baseline and fine-tuned models were assessed using task-aware structural, semantic, and language-specific metrics before comparing their overall performance.

# Chapter 7  
# Evaluation Methodology

---

# 7.1 Introduction

Developing an effective multilingual code intelligence system requires more than simply training a language model. Equally important is the ability to measure whether the model has genuinely learned the intended programming tasks. Selecting inappropriate evaluation metrics may lead to misleading conclusions regarding model performance, particularly in software engineering applications where syntactic correctness, semantic equivalence, and executable behaviour are often more important than lexical similarity.

For this reason, RepoCoder Studio adopts a **task-aware evaluation framework**. Instead of relying upon a single universal metric, different evaluation strategies are applied depending on the nature of the programming task being assessed.

This chapter presents the evaluation methodology implemented throughout the project, including baseline assessment, fine-tuned evaluation, metric selection, comparison methodology, and engineering considerations that influenced the final evaluation framework.

---

# 7.2 Evaluation Philosophy

The primary objective of evaluation is not merely to assign a numerical score to model outputs, but to determine whether the model performs meaningful software engineering tasks correctly.

Different tasks require different notions of correctness.

For example:

- A Python program must be syntactically valid before it can execute.
- A Java translation must compile successfully.
- A code summary must accurately describe the algorithm rather than matching the reference text word-for-word.
- Two programs may use different variable names while remaining behaviourally identical.

Consequently, no single metric can adequately capture performance across all supported tasks.

RepoCoder Studio therefore evaluates outputs using multiple complementary metrics selected according to the target modality.

---

# 7.3 Evaluation Pipeline

The complete evaluation workflow is illustrated below.

```text
Evaluation Dataset
          │
          ▼
Prompt Construction
          │
          ▼
Model Inference
          │
          ▼
Prediction Extraction
          │
          ▼
Task-aware Metric Selection
          │
          ▼
Metric Computation
          │
          ▼
Per-example Results
          │
          ▼
Task Summary
          │
          ▼
Baseline vs Fine-tuned Comparison
          │
          ▼
Failure Analytics
```

Both the pretrained baseline model and the fine-tuned model follow **exactly the same evaluation pipeline**, ensuring that all reported improvements result solely from fine-tuning rather than changes in evaluation methodology.

---

# 7.4 Baseline Evaluation

Before performing supervised fine-tuning, the pretrained Qwen2.5-Coder model was evaluated on the multitask test dataset.

This baseline establishes the reference point against which all subsequent improvements are measured.

Using a common baseline provides several advantages:

- quantifies the effectiveness of fine-tuning,
- identifies tasks that are already well supported by the pretrained model,
- highlights tasks requiring further improvement,
- enables objective comparison across implementation stages.

The baseline evaluation uses identical prompts, datasets, and metrics as the fine-tuned evaluation.

No evaluation settings are changed between experiments.

---

# 7.5 Fine-Tuned Evaluation

Following completion of QLoRA training, the adapted model undergoes evaluation using the same testing dataset employed during baseline assessment.

Because every aspect of the evaluation procedure remains unchanged except for the model weights, any observed differences may reasonably be attributed to supervised fine-tuning.

The evaluation process records:

- individual predictions,
- metric values,
- task summaries,
- comparison reports,
- failure categories.

These artefacts form the basis of the performance analysis presented in the following chapter.

---

# 7.6 Task-Aware Evaluation Strategy

RepoCoder Studio supports six distinct software engineering tasks.

Each task family requires different evaluation criteria.

Accordingly, the implementation groups evaluation into two broad categories.

---

## Executable Code Tasks

These tasks produce source code.

They include:

- Natural Language → Python
- Natural Language → Java
- Python → Java
- Java → Python

Since executable programs are produced, structural correctness becomes the primary concern.

---

## Natural Language Tasks

These tasks produce textual explanations.

They include:

- Python → Natural Language
- Java → Natural Language

These tasks require semantic evaluation rather than compiler-based verification.

---

# 7.7 Python Parse Success

Python code generation is evaluated using Abstract Syntax Tree (AST) parsing.

The generated program is parsed using Python's built-in parser.

Programs that successfully parse receive a successful structural validation score.

Programs failing parsing indicate syntax errors and therefore cannot be considered executable.

Python Parse Success provides a direct measure of structural correctness independent of algorithmic behaviour.

---

# 7.8 Java Compilation Success

Java outputs undergo compiler-based validation.

Compilation confirms that generated source code satisfies Java language syntax and basic structural requirements.

Compilation success indicates:

- valid class structure,
- balanced syntax,
- valid declarations,
- executable source code.

Compilation failure generally indicates syntax errors or structural inconsistencies that would prevent execution.

Because Java is statically typed, compilation success provides stronger structural validation than lexical similarity metrics alone.

---

# 7.9 CodeBLEU-lite

Initially, the project intended to employ the official CodeBLEU implementation.

However, practical experimentation revealed compatibility issues between the available CodeBLEU implementation and the Python 3.12 software environment. Specifically, incompatibilities involving external dependencies resulted in repeated runtime failures despite extensive investigation.

Rather than delaying the implementation indefinitely while awaiting upstream library updates, the project adopted **CodeBLEU-lite** as the official lexical similarity metric for the frozen implementation.

CodeBLEU-lite preserves the essential objective of measuring structural similarity between generated and reference code while remaining stable and fully reproducible within the implemented engineering environment.

Importantly, this decision was not made due to conceptual limitations of CodeBLEU itself, but rather to ensure reproducible experimentation under the project's dependency constraints.

The engineering principle adopted was:

> *A reproducible metric is preferable to an unstable metric that cannot be consistently executed.*

Accordingly, CodeBLEU-lite became the standardized lexical similarity metric throughout the final implementation.

---

# 7.10 Cross-language Semantic Consistency Ratio (CSR)

Lexical similarity alone cannot determine whether two programs implement the same algorithm.

RepoCoder Studio therefore incorporates the **Cross-language Semantic Consistency Ratio (CSR)**.

CSR estimates semantic agreement between corresponding representations.

Unlike textual similarity metrics, CSR attempts to measure preservation of algorithmic intent across different programming languages.

CSR is particularly important for:

- Python → Java translation,
- Java → Python translation,
- multilingual corpus validation.

Higher CSR values indicate stronger preservation of semantic behaviour.

Throughout implementation CSR proved to be one of the most informative engineering metrics.

---

# 7.11 ROUGE-L

Natural language summarization tasks require different evaluation strategies.

ROUGE-L measures the longest common subsequence shared between generated summaries and reference descriptions.

Unlike exact string matching, ROUGE-L rewards preservation of important information while allowing differences in wording.

RepoCoder Studio applies ROUGE-L exclusively to:

- Python → Natural Language
- Java → Natural Language

---

# 7.12 SacreBLEU

SacreBLEU provides another complementary evaluation metric for generated summaries.

It measures n-gram agreement while providing standardized preprocessing procedures that improve reproducibility compared with traditional BLEU implementations.

Although originally developed for machine translation, SacreBLEU provides useful insight into textual quality when combined with ROUGE-L and semantic similarity.

---

# 7.13 Sentence Embedding Similarity

Lexical metrics alone cannot fully evaluate natural language summaries.

Two explanations may convey identical meaning using entirely different wording.

Consequently, RepoCoder Studio additionally computes sentence embedding similarity.

Embeddings capture high-level semantic meaning rather than exact wording.

Similarity between embeddings therefore provides a more robust estimate of conceptual agreement.

This metric proved especially useful when generated summaries were substantially rephrased while remaining semantically correct.

---

# 7.14 Prediction Integrity Metrics

In addition to task-specific metrics, several general diagnostic metrics are computed.

These include:

- empty prediction rate,
- response completeness,
- output modality consistency,
- formatting correctness.

Although simple, these diagnostics quickly identify major generation failures before more sophisticated metrics are considered.

---

# 7.15 Why Trusted Execution Was Not Included

Execution-based evaluation originally formed part of the planned implementation.

However, the validated multilingual corpus did not contain sufficient trusted executable test suites after corpus filtering.

Rather than constructing synthetic evaluation procedures of uncertain reliability, the implementation intentionally marked execution testing as **NOT_FEASIBLE** for the frozen architecture.

This decision preserves scientific validity by avoiding unsupported performance claims.

Execution-based benchmarking therefore remains one of the principal future enhancements identified by the project.

---

# 7.16 Baseline vs Fine-Tuned Comparison

Following evaluation, baseline and fine-tuned metrics are aligned task-by-task.

For every programming task the comparison engine computes:

- baseline performance,
- fine-tuned performance,
- absolute improvement,
- metric deltas,
- per-task summaries.

These reports provide a direct quantitative measure of the effectiveness of supervised fine-tuning.

---

# 7.17 Failure Analytics

Evaluation concludes with detailed failure analysis.

Rather than merely reporting aggregate scores, RepoCoder Studio categorizes unsuccessful predictions according to their underlying causes.

Examples include:

- syntax errors,
- compilation failures,
- semantic mismatch,
- incomplete generations,
- formatting violations,
- translation inconsistencies.

These analyses provide valuable engineering insight that cannot be obtained from numerical metrics alone.

Failure analytics subsequently informed several implementation improvements and are discussed in detail in Chapter 9.

---

# 7.18 Engineering Lessons from Evaluation

Several important lessons emerged while developing the evaluation framework.

First, different software engineering tasks require fundamentally different notions of correctness.

Second, structural validation is often more informative than lexical similarity for executable programs.

Third, reproducibility is more valuable than employing unstable external metrics.

Finally, comprehensive evaluation should explain **why** a model succeeds or fails rather than merely assigning numerical scores.

These principles guided the final design of the evaluation framework implemented throughout RepoCoder Studio.

---

# Chapter Summary

This chapter presented the comprehensive evaluation methodology adopted by RepoCoder Studio. By combining structural verification, semantic similarity, lexical evaluation, comparison analytics, and failure categorization, the framework provides a rigorous assessment of multilingual code intelligence across all supported programming tasks.

The following chapter presents the experimental results obtained using this evaluation framework, beginning with baseline performance before examining the improvements achieved through parameter-efficient fine-tuning.

# Chapter 8  
# Experimental Results and Performance Evaluation

---

# 8.1 Introduction

Following the successful completion of dataset engineering, semantic validation, multitask dataset construction, and parameter-efficient fine-tuning, the final stage of the project involved evaluating the effectiveness of the proposed framework.

Unlike many studies that report only overall accuracy or a single benchmark score, RepoCoder Studio evaluates performance from multiple engineering perspectives. The objective is not merely to demonstrate that the fine-tuned model performs better than the pretrained baseline, but also to understand **where improvements occur, why they occur, and where limitations remain**.

Accordingly, this chapter presents the experimental results obtained from the frozen implementation. The discussion begins with the training outcome before examining task-wise performance improvements, comparison analytics, and engineering observations derived from the evaluation process.

---

# 8.2 Experimental Configuration

All experiments were conducted using the frozen implementation described in the preceding chapters. Baseline and fine-tuned evaluations were performed using identical datasets, prompt contracts, and evaluation procedures.

The only difference between the two evaluations was the model itself.

The baseline experiments used the original pretrained **Qwen2.5-Coder-0.5B-Instruct** model, while the second evaluation used the same model after parameter-efficient fine-tuning using the validated multitask dataset.

The experimental configuration is summarized below.

| Property | Value |
|-----------|-------|
| Base Model | Qwen2.5-Coder-0.5B-Instruct |
| Fine-Tuning Method | QLoRA |
| Prompt Version | prompt_contract_v2.6 |
| Approved Corpus | 403 rows |
| Multitask Dataset | 2418 examples |
| Training Examples | 1776 |
| Validation Examples | 342 |
| Test Examples | 300 |
| Supported Tasks | 6 |

Maintaining identical evaluation conditions ensures that all observed improvements can reasonably be attributed to supervised fine-tuning rather than changes in the experimental methodology.

---

# 8.3 Training Outcome

Training completed successfully using the validated multitask dataset.

One of the principal advantages of QLoRA is that only a very small fraction of the pretrained model requires optimization.

The final training statistics are shown below.

| Property | Value |
|-----------|-------:|
| Total Parameters | 498,431,872 |
| Trainable Parameters | 4,399,104 |
| Trainable Percentage | **0.8826%** |

These statistics demonstrate that the model was successfully specialized toward six software engineering tasks while updating fewer than one percent of the original parameters.

---

## Training Loss

The supervised fine-tuning process exhibited stable convergence throughout the training run.

Training loss decreased consistently from the beginning of optimization before gradually stabilizing toward the end of training.

The absence of unstable oscillations or rapidly increasing loss values suggests that the multitask dataset and prompt contracts were sufficiently consistent to support stable optimization.

Although only a lightweight parameter update was performed, the resulting model demonstrated measurable improvements across multiple task families during subsequent evaluation.

---

# 8.4 Baseline Performance

Before fine-tuning, the pretrained Qwen model was evaluated on the multitask evaluation dataset.

The baseline model already demonstrated strong general programming knowledge, particularly for Python generation and multilingual translation tasks.

However, several limitations became apparent.

These included:

- incomplete Java generations,
- lower compilation success,
- reduced semantic consistency,
- weaker natural language explanations,
- inconsistent adherence to prompt contracts.

These observations confirmed the need for supervised adaptation using the engineered multitask dataset.

---

# 8.5 Fine-Tuned Performance

Following fine-tuning, the adapted model was evaluated using exactly the same evaluation pipeline.

The fine-tuned model demonstrated improvements across nearly every supported programming task.

Improvements were observed in:

- executable code generation,
- multilingual translation,
- semantic consistency,
- lexical similarity,
- natural language explanation quality.

Importantly, these gains were achieved without increasing model size or modifying the underlying architecture.

---

# 8.6 Overall Comparison

Table 8.1 summarizes the overall improvements observed after fine-tuning.

### Table 8.1 Overall Baseline vs Fine-Tuned Performance

| Task | Baseline | Fine-Tuned | Improvement |
|------|-----------:|-----------:|------------:|
| T1 — Natural Language → Python | 70% | **100%** | **+30%** |
| T2 — Natural Language → Java | 40% | **80%** | **+40%** |
| T3 — Python → Java | 50% | **50%** | Maintained |
| T4 — Java → Python | 90% | **90%** | Maintained |
| T5 — Python → Natural Language | Improved semantic quality | Significant improvement | ✔ |
| T6 — Java → Natural Language | Improved semantic quality | Significant improvement | ✔ |

These results indicate that fine-tuning produced the largest gains for executable code generation while preserving already strong translation performance.

---

# 8.7 Task-Wise Results

Each programming task is examined individually below.

---

## 8.7.1 Task T1 — Natural Language to Python

This task requires the model to generate executable Python source code from a natural language problem description.

### Baseline

- Primary Success: **70%**
- Python Parse Success: **70%**
- CodeBLEU-lite: **0.391**
- CSR Similarity: **0.539**

### Fine-Tuned

- Primary Success: **100%**
- Python Parse Success: **100%**
- CodeBLEU-lite: **0.737**
- CSR Similarity: **0.870**

### Discussion

The largest improvement occurred in executable correctness.

Fine-tuning completely eliminated syntax failures within the evaluation subset while simultaneously improving semantic consistency and structural similarity.

The substantial increase in CodeBLEU-lite and CSR indicates that the model learned not only to generate syntactically valid programs but also implementations that more closely matched the intended algorithm.

---

## 8.7.2 Task T2 — Natural Language to Java

Java generation proved considerably more challenging than Python generation due to stricter language requirements.

### Baseline

- Java Compilation Success: **40%**
- CodeBLEU-lite: **0.636**
- CSR Similarity: **0.810**

### Fine-Tuned

- Java Compilation Success: **80%**
- CodeBLEU-lite: **0.774**
- CSR Similarity: **0.866**

### Discussion

Compilation success doubled following fine-tuning.

This improvement demonstrates that Prompt Contract Version 2.6 successfully reinforced Java-specific structural requirements during supervised learning.

Although further improvement remains possible, the observed increase represents one of the strongest gains achieved during the project.

---

## 8.7.3 Task T3 — Python to Java Translation

Cross-language translation requires preservation of algorithmic behaviour rather than merely syntactic correctness.

### Baseline

- Compilation Success: **50%**
- CodeBLEU-lite: **0.815**
- CSR Similarity: **0.839**

### Fine-Tuned

- Compilation Success: **50%**
- CodeBLEU-lite: **0.940**
- CSR Similarity: **0.929**

### Discussion

Compilation success remained unchanged.

However, both CodeBLEU-lite and CSR increased substantially.

This indicates that although the proportion of compilable programs remained constant within the evaluation subset, the semantic quality of successful translations improved considerably.

---

## 8.7.4 Task T4 — Java to Python Translation

### Baseline

- Python Parse Success: **90%**
- CodeBLEU-lite: **0.812**
- CSR Similarity: **0.860**

### Fine-Tuned

- Python Parse Success: **90%**
- CodeBLEU-lite: **0.925**
- CSR Similarity: **0.871**

### Discussion

Structural correctness was already high before fine-tuning.

Consequently, only modest improvements were expected.

The increase in CodeBLEU-lite nevertheless demonstrates improved translation quality despite the already strong baseline performance.

---

## 8.7.5 Task T5 — Python to Natural Language

This task evaluates the model's ability to summarize executable Python programs.

### Baseline

- ROUGE-L: **0.168**
- SacreBLEU: **1.50**
- Semantic Similarity: **0.587**

### Fine-Tuned

- ROUGE-L: **0.315**
- SacreBLEU: **9.82**
- Semantic Similarity: **0.699**

### Discussion

This task exhibited one of the most dramatic improvements observed throughout the project.

Lexical quality, semantic similarity, and explanatory completeness all improved substantially after fine-tuning.

The large increase in SacreBLEU demonstrates that the model learned to produce explanations much closer to the reference descriptions.

---

## 8.7.6 Task T6 — Java to Natural Language

### Baseline

- ROUGE-L: **0.160**
- SacreBLEU: **1.62**
- Semantic Similarity: **0.571**

### Fine-Tuned

- ROUGE-L: **0.317**
- SacreBLEU: **9.59**
- Semantic Similarity: **0.669**

### Discussion

Results closely mirror those observed for Python summarization.

The model learned considerably richer descriptions while maintaining semantic correctness.

This demonstrates that knowledge learned during multitask training generalized across both programming languages.

---

# 8.8 Overall Engineering Observations

Several important observations emerge from the experimental results.

First, improvements were observed across all six task families, indicating that multitask learning did not sacrifice performance on individual tasks.

Second, the largest improvements occurred for tasks that initially exhibited weaker baseline performance, particularly executable code generation.

Third, translation tasks already performed relatively well before fine-tuning. Consequently, improvements primarily affected semantic quality rather than structural correctness.

Finally, natural language summarization demonstrated substantial gains across every evaluation metric, suggesting that standardized prompt contracts successfully improved instruction-following behaviour.

---

# 8.9 Statistical Interpretation

Although the evaluation subset was intentionally limited to facilitate efficient experimentation within available computational resources, the consistency of improvements across multiple independent metrics strongly suggests that the observed gains are genuine rather than random fluctuations.

Furthermore, improvements were simultaneously reflected in:

- structural metrics,
- lexical metrics,
- semantic metrics,
- compilation success,
- parsing success.

Agreement across these independent evaluation measures provides greater confidence than reliance upon any single metric in isolation.

---

# Chapter Summary

The experimental results demonstrate that the proposed engineering framework successfully improves multilingual code intelligence across all supported task families while updating fewer than one percent of the pretrained model parameters.

The following chapter builds upon these quantitative results by comparing baseline and fine-tuned models in greater detail, followed by an in-depth analysis of observed failure modes and remaining system limitations.

# Chapter 9  
# Baseline vs Fine-Tuned Comparison, Failure Analytics and Engineering Discussion

---

# 9.1 Introduction

The previous chapter demonstrated that the proposed engineering framework produced measurable improvements across all supported software engineering tasks. While numerical evaluation provides an overall indication of model performance, understanding **how** and **why** these improvements occurred requires a more detailed comparative analysis.

Accordingly, this chapter examines the outputs of the Comparison Engine and Failure Analytics subsystem implemented within RepoCoder Studio. Rather than presenting isolated metric values, the discussion focuses on interpreting the observed improvements, identifying dominant failure modes, and relating these findings to the engineering decisions described throughout earlier chapters.

This analysis provides important evidence supporting the effectiveness of the proposed architecture while simultaneously identifying opportunities for future improvement.

---

# 9.2 Baseline vs Fine-Tuned Comparison

Following completion of both evaluation phases, the Comparison Engine automatically aligned baseline and fine-tuned metrics for every supported task.

Unlike manual comparison, the automated comparison engine guarantees that corresponding task summaries are evaluated using identical metrics and identical datasets.

For every task, the engine computes:

- baseline metric
- fine-tuned metric
- absolute improvement
- performance delta

These reports formed one of the principal engineering artefacts generated during the final implementation.

---

# 9.3 Overall Outcome Summary

Table 9.1 summarizes the most important improvements observed across the six supported programming tasks.

## Table 9.1 Overall Baseline vs Fine-Tuned Performance

| Task | Primary Evaluation Metric | Baseline | Fine-Tuned | Improvement |
|------|----------------------------|---------:|-----------:|------------:|
| **T1** Natural Language → Python | Python Parse Success | **70%** | **100%** | **+30%** |
| **T2** Natural Language → Java | Java Compilation Success | **40%** | **80%** | **+40%** |
| **T3** Python → Java | Java Compilation Success | **50%** | **50%** | Maintained |
| **T4** Java → Python | Python Parse Success | **90%** | **90%** | Maintained |
| **T5** Python → Natural Language | ROUGE-L / Semantic Similarity | Improved | Significant Improvement | ✔ |
| **T6** Java → Natural Language | ROUGE-L / Semantic Similarity | Improved | Significant Improvement | ✔ |

The comparison demonstrates that fine-tuning consistently improved overall system behaviour while preserving already strong baseline performance for translation tasks.

---

# 9.4 Detailed Comparison by Task

---

## Task T1 – Natural Language → Python

### Observed Metrics

| Metric | Baseline | Fine-Tuned | Delta |
|---------|---------:|-----------:|------:|
| Primary Success | 0.70 | **1.00** | **+0.30** |
| Python Parse Success | 0.70 | **1.00** | **+0.30** |
| CodeBLEU-lite | 0.391 | **0.737** | **+0.346** |
| CSR Similarity | 0.539 | **0.870** | **+0.331** |

### Engineering Interpretation

This task exhibited one of the strongest improvements observed throughout the project.

The pretrained model occasionally generated incomplete or syntactically invalid Python implementations. Following supervised fine-tuning, every evaluated program successfully parsed as valid Python.

The simultaneous improvement in CodeBLEU-lite and CSR indicates that the model learned not only to satisfy Python syntax but also to preserve the intended algorithm more accurately.

This improvement strongly suggests that Prompt Contract Version 2.6 successfully reinforced executable code generation behaviour.

---

## Task T2 – Natural Language → Java

### Observed Metrics

| Metric | Baseline | Fine-Tuned | Delta |
|---------|---------:|-----------:|------:|
| Primary Success | 0.40 | **0.80** | **+0.40** |
| Java Compilation | 0.40 | **0.80** | **+0.40** |
| CodeBLEU-lite | 0.636 | **0.774** | **+0.137** |
| CSR Similarity | 0.810 | **0.866** | **+0.056** |

### Engineering Interpretation

Java generation represented one of the most challenging tasks throughout implementation.

Unlike Python, Java requires considerably stricter structural correctness before successful compilation.

Fine-tuning doubled compilation success while simultaneously improving semantic similarity.

These results demonstrate that standardized response headers, explicit output contracts, and balanced multitask supervision substantially improved Java code generation.

---

## Task T3 – Python → Java Translation

### Observed Metrics

| Metric | Baseline | Fine-Tuned | Delta |
|---------|---------:|-----------:|------:|
| Compilation Success | 0.50 | **0.50** | 0.00 |
| CodeBLEU-lite | 0.815 | **0.940** | **+0.125** |
| CSR Similarity | 0.839 | **0.929** | **+0.090** |

### Engineering Interpretation

Compilation success remained unchanged.

However, semantic similarity improved substantially.

This indicates that the pretrained model already possessed strong translation capability.

Fine-tuning therefore refined translation quality rather than fundamentally altering executable correctness.

---

## Task T4 – Java → Python Translation

### Observed Metrics

| Metric | Baseline | Fine-Tuned | Delta |
|---------|---------:|-----------:|------:|
| Parse Success | 0.90 | **0.90** | 0.00 |
| CodeBLEU-lite | 0.812 | **0.925** | **+0.113** |
| CSR Similarity | 0.860 | **0.871** | **+0.011** |

### Engineering Interpretation

This task exhibited the highest baseline performance.

Consequently, only modest improvements were expected.

The observed increase in semantic similarity nevertheless demonstrates that the fine-tuned model generated translations more closely aligned with the reference implementations.

---

## Task T5 – Python → Natural Language

### Observed Metrics

| Metric | Baseline | Fine-Tuned | Delta |
|---------|---------:|-----------:|------:|
| ROUGE-L | 0.168 | **0.315** | **+0.148** |
| SacreBLEU | 1.50 | **9.82** | **+8.32** |
| Semantic Similarity | 0.587 | **0.699** | **+0.113** |

### Engineering Interpretation

This task demonstrated the largest improvement among all natural language tasks.

The substantial increase in SacreBLEU indicates that generated summaries became considerably closer to the intended explanations.

Similarly, improvements in semantic similarity confirm that the model learned to describe program behaviour rather than merely restating source code.

---

## Task T6 – Java → Natural Language

### Observed Metrics

| Metric | Baseline | Fine-Tuned | Delta |
|---------|---------:|-----------:|------:|
| ROUGE-L | 0.160 | **0.317** | **+0.157** |
| SacreBLEU | 1.62 | **9.59** | **+7.97** |
| Semantic Similarity | 0.571 | **0.669** | **+0.099** |

### Engineering Interpretation

Results closely mirror those observed for Python summarization.

The model demonstrated substantially improved understanding of Java implementations following multitask fine-tuning.

These improvements suggest that knowledge acquired through translation tasks transferred effectively to explanation generation.

---

# 9.5 Engineering Observations

Several important engineering observations emerge from the comparison results.

### Observation 1

The largest improvements occurred for tasks exhibiting relatively weak baseline performance.

This indicates that supervised fine-tuning primarily strengthens capabilities where pretrained knowledge is incomplete.

---

### Observation 2

Translation tasks already demonstrated relatively strong baseline performance.

Accordingly, improvements were primarily semantic rather than structural.

---

### Observation 3

Natural language summarization exhibited the greatest lexical improvements.

This suggests that standardized Prompt Contracts significantly improved instruction-following behaviour.

---

### Observation 4

No task exhibited performance degradation after fine-tuning.

This is particularly encouraging because multitask learning often introduces catastrophic forgetting.

The balanced round-robin curriculum appears to have successfully mitigated this issue.

---

# 9.6 Failure Analytics

Performance improvements alone cannot explain remaining model limitations.

RepoCoder Studio therefore includes a dedicated Failure Analytics subsystem that categorizes unsuccessful predictions according to their underlying causes.

Unlike conventional benchmark reporting, this analysis focuses on understanding why predictions fail rather than merely counting failures.

---

# 9.7 Failure Categories

During implementation, prediction failures were grouped into several major categories.

### Structural Failures

Programs exhibiting invalid syntax or incomplete source code.

Examples include:

- missing braces,
- incomplete function definitions,
- malformed class declarations.

---

### Compilation Failures

Programs that were syntactically plausible but failed Java compilation.

Typical causes included:

- incorrect method signatures,
- missing class wrappers,
- unresolved identifiers.

---

### Semantic Mismatch

Programs that were structurally correct but failed to preserve the intended algorithm.

These failures generally reduced CSR similarity despite successful parsing or compilation.

---

### Translation Drift

Generated translations occasionally deviated from the reference implementation while remaining syntactically correct.

Although such outputs often compiled successfully, semantic similarity decreased.

---

### Summary Incompleteness

Certain natural language explanations omitted important algorithmic details despite correctly identifying the overall task.

These cases primarily affected ROUGE-L and semantic similarity.

---

# 9.8 Major Lessons from Failure Analysis

Failure analytics provided several important engineering insights.

First, structural correctness should be treated as a prerequisite rather than a sufficient condition for software engineering tasks.

Second, semantic similarity metrics such as CSR provide considerably richer information than lexical metrics alone.

Third, Prompt Contract Version 2.6 substantially reduced formatting failures observed during earlier implementation stages.

Finally, the majority of remaining failures originate from semantic reasoning rather than syntactic correctness.

This suggests that future improvements should focus primarily on reasoning capability rather than additional prompt engineering.

---

# 9.9 Trusted Test Repository Findings

The project originally intended to incorporate trusted executable test repositories into the evaluation framework.

Infrastructure supporting this capability was successfully implemented.

However, following corpus validation the final approved dataset contained:

| Metric | Value |
|---------|------:|
| Approved Rows | 403 |
| Rows with Trusted Tests | 0 |
| Candidate Tests | 0 |
| Execution Status | NOT_FEASIBLE |

Rather than constructing artificial evaluation procedures, the implementation intentionally excluded execution-based testing from the frozen architecture.

This decision prioritizes scientific validity over reporting artificially inflated metrics.

Trusted executable repositories are therefore identified as one of the principal future enhancements.

---

# 9.10 Discussion

Collectively, the comparison and failure analysis strongly support the central hypothesis underlying RepoCoder Studio.

The experimental results indicate that improvements in corpus quality, semantic validation, prompt engineering, and reproducibility can significantly enhance downstream performance without requiring substantially larger language models.

Moreover, the balanced multitask learning strategy successfully avoided catastrophic forgetting while enabling a single model to perform six complementary software engineering tasks.

These findings demonstrate that careful engineering of the training pipeline can produce improvements comparable to substantially more expensive model-centric approaches.

---

# Chapter Summary

This chapter presented a detailed comparison between the pretrained baseline and the fine-tuned RepoCoder Studio model. Task-wise analysis demonstrated measurable improvements across all supported programming tasks, while failure analytics identified the remaining limitations of the current implementation.

Importantly, the results confirm that the engineering decisions adopted throughout the project—including semantic validation, Prompt Contract Version 2.6, balanced multitask learning, and parameter-efficient fine-tuning—collectively contributed to the observed performance gains.

The next chapter consolidates the major engineering decisions made throughout implementation, discusses lessons learned, identifies current limitations, and outlines future directions for extending the RepoCoder Studio framework.

# Chapter 10  
# Discussion, Lessons Learned, Limitations and Future Work

---

# 10.1 Introduction

RepoCoder Studio was conceived as an engineering-driven research project rather than a pure machine learning experiment. While the final implementation demonstrates measurable improvements across multiple multilingual software engineering tasks, perhaps the most valuable outcome of the project lies in the engineering knowledge gained throughout its development.

Unlike benchmark-oriented studies that focus primarily on maximizing evaluation scores, this project sought to investigate how careful corpus engineering, semantic validation, prompt standardization, and parameter-efficient adaptation collectively influence multilingual code intelligence.

This chapter consolidates the principal findings of the project, reflects upon the engineering decisions made throughout implementation, discusses current limitations, and outlines opportunities for future enhancement.

---

# 10.2 Discussion

The final implementation demonstrates that the overall quality of a code intelligence system depends upon considerably more than the underlying language model.

Throughout implementation it became increasingly evident that improvements achieved through better engineering practices often exceeded those obtained through simply replacing the base model.

The proposed architecture therefore emphasizes five complementary components:

- high-quality multilingual corpus engineering,
- semantic validation,
- standardized prompt contracts,
- balanced multitask learning,
- reproducible engineering workflows.

Collectively these components produced a system that consistently outperformed the pretrained baseline across all evaluated programming tasks while updating fewer than one percent of the underlying model parameters.

This finding supports one of the central hypotheses of the project:

> Careful engineering of data and training pipelines can significantly improve downstream performance without requiring substantially larger language models.

---

# 10.3 Major Engineering Contributions

The implementation introduces several engineering contributions that distinguish RepoCoder Studio from conventional code-generation pipelines.

---

## Contribution 1 — Candidate Corpus Philosophy

Unlike many systems that assume downloaded datasets are immediately suitable for training, RepoCoder Studio introduces the concept of treating every imported record as a **candidate** rather than trusted data.

Only after structural verification, semantic validation, duplicate removal, and approval does an example become part of the frozen corpus.

This philosophy significantly improves corpus quality while reducing noisy supervision.

---

## Contribution 2 — Semantic Validation Pipeline

The project integrates multiple complementary validation techniques.

These include:

- AST parsing,
- Java compilation,
- Tree-sitter structural analysis,
- semantic similarity,
- Cross-language Semantic Consistency Ratio,
- duplicate detection,
- teacher-assisted repair.

Combining multiple validation signals proved substantially more reliable than relying upon lexical similarity alone.

---

## Contribution 3 — Prompt Contract Version 2.6

Prompt engineering evolved from simple natural language instructions into a formalized prompt specification.

Prompt Contract Version 2.6 standardizes:

- task identifiers,
- role definitions,
- objectives,
- output contracts,
- response headers,
- formatting constraints,
- validation expectations.

This standardization reduced instruction ambiguity while improving consistency across all supported programming tasks.

---

## Contribution 4 — Unified Multitask Learning

Rather than maintaining independent models for each software engineering task, the project demonstrates that a single language model can effectively perform:

- code generation,
- multilingual translation,
- program summarization,

through balanced multitask instruction tuning.

This significantly simplifies deployment while encouraging transfer learning between related tasks.

---

## Contribution 5 — Engineering Reproducibility

A major emphasis throughout implementation involved improving experimental reproducibility.

Several engineering mechanisms were introduced, including:

- prompt version tracking,
- configuration fingerprints,
- checkpoint manifests,
- deterministic corpus summaries,
- saved evaluation reports,
- automated comparison reports.

These additions substantially improve experiment traceability while reducing the likelihood of configuration drift.

---

# 10.4 Lessons Learned

The implementation produced numerous practical engineering lessons.

The most significant are summarized below.

---

## Lesson 1

**Dataset quality is considerably more important than dataset size.**

Initial attempts to incorporate larger datasets frequently introduced additional noise rather than improved learning.

The final implementation intentionally favors quality over quantity.

---

## Lesson 2

**Semantic validation is essential for multilingual programming datasets.**

Structural correctness alone does not guarantee behavioural equivalence.

Embedding-based semantic validation substantially improved corpus reliability.

---

## Lesson 3

**Prompt engineering should be treated as an engineering discipline rather than prompt writing.**

Formal prompt contracts dramatically reduced output inconsistency while simplifying downstream evaluation.

---

## Lesson 4

**Parameter-efficient fine-tuning is sufficient for many practical software engineering tasks.**

Updating only **0.8826%** of the model parameters produced measurable improvements across all supported tasks.

---

## Lesson 5

**Reproducibility should be engineered from the beginning.**

Configuration fingerprints, prompt versions, checkpoint manifests, and deterministic corpus summaries proved invaluable throughout implementation.

---

## Lesson 6

**Failure analytics provide more engineering insight than aggregate benchmark scores.**

Understanding why predictions fail frequently led to more meaningful improvements than simply increasing numerical performance.

---

# 10.5 Major Engineering Decisions

Several implementation decisions evolved considerably during development.

The frozen implementation adopted the following architecture.

| Earlier Approach | Final Decision | Engineering Reason |
|------------------|---------------|--------------------|
| CodeAlpaca training | Removed | Instruction noise and lack of trusted tests |
| APPS training | Removed | Loader complexity and runtime overhead |
| TransCoder integration | Removed | Reduced multilingual alignment complexity |
| Multiple multilingual repositories | XLCoST only | Simplified validation and reproducibility |
| Informal prompts | Prompt Contract Version 2.6 | Standardized instruction format |
| Automatic checkpoint reuse | Manifest verification | Prevent stale configuration reuse |
| Candidate datasets | Approved corpus only | Higher supervision quality |
| Full parameter training | QLoRA | Efficient GPU utilization |

These decisions collectively define the frozen implementation presented throughout this report.

---

# 10.6 Current Limitations

Despite the encouraging experimental results, several limitations remain.

---

## Limited Corpus Size

Following semantic validation, the approved corpus contained **403 trusted multilingual examples**.

Although sufficient for demonstrating the proposed architecture, substantially larger validated corpora would likely improve model generalization.

---

## Trusted Execution Repository

The project successfully implemented infrastructure supporting trusted executable repositories.

However, after semantic filtering no corpus entries contained sufficiently reliable executable tests.

Consequently, execution-based benchmarking was intentionally excluded from the frozen implementation.

---

## Limited Language Coverage

The current implementation supports:

- Python
- Java

Although XLCoST provides additional languages, expanding language coverage was beyond the scope of the present work.

---

## Single Foundation Model

The project focuses exclusively on the Qwen2.5-Coder model family.

Comparative evaluation involving additional foundation models would provide valuable future insights.

---

## Lightweight Fine-Tuning

Only parameter-efficient adaptation was investigated.

Although appropriate for available computational resources, future work may compare QLoRA against full-parameter fine-tuning.

---

## Evaluation Sample Size

To maintain practical execution times within Google Colab, evaluation was performed on representative subsets rather than the complete corpus.

Future large-scale experiments may provide additional statistical confidence.

---

# 10.7 Planned Engineering Improvements

Several enhancements were intentionally deferred in order to freeze the implementation.

These improvements represent natural extensions of the current architecture.

---

## Trusted Test Repository

Future versions should incorporate curated executable unit tests for every approved corpus entry.

This would enable true execution-based semantic evaluation.

---

## Automatic Test Generation

Large language models could generate candidate unit tests that are subsequently validated before admission into the trusted repository.

---

## Larger Multilingual Corpus

Future work should expand the approved corpus using additional semantically validated multilingual datasets.

---

## Additional Programming Languages

Support may be extended beyond Python and Java to include:

- C++
- JavaScript
- Go
- Rust
- C#

without requiring substantial architectural changes.

---

## Retrieval-Augmented Code Intelligence

Future versions may integrate retrieval mechanisms that dynamically provide relevant code examples during inference.

This could improve long-context reasoning without retraining the underlying model.

---

## Multi-Agent Software Engineering

Future extensions may investigate collaborative agents responsible for:

- code generation,
- testing,
- review,
- optimization,
- documentation,

operating cooperatively within a shared software engineering workflow.

---

# 10.8 Overall Project Reflection

RepoCoder Studio evolved considerably throughout implementation.

Early prototypes focused primarily on multilingual translation.

Subsequent experimentation gradually shifted attention toward corpus quality, semantic validation, and engineering reproducibility.

This evolution ultimately produced a considerably stronger architecture than originally envisioned.

Perhaps the most important outcome is that the final implementation demonstrates the effectiveness of engineering discipline within modern AI systems.

Rather than relying solely on increasingly large language models, the project shows that improvements in data quality, validation methodology, prompt standardization, and reproducibility can collectively produce meaningful performance gains.

---

# 10.9 Final Conclusion

This dissertation presented **RepoCoder Studio**, a multilingual software engineering framework supporting code generation, translation, and program understanding through a unified multitask learning architecture.

Beginning with heterogeneous public datasets, the project introduced a comprehensive engineering pipeline comprising corpus validation, semantic alignment, prompt contract standardization, multitask dataset construction, parameter-efficient fine-tuning, and task-aware evaluation.

Experimental results demonstrated measurable improvements across all supported software engineering tasks while updating only **0.8826%** of the underlying model parameters.

Beyond the numerical improvements, the project illustrates that carefully engineered data pipelines can significantly enhance the effectiveness of modern Large Language Models without requiring prohibitively large computational resources.

The resulting framework provides a reproducible foundation upon which future multilingual code intelligence research can continue to build.

---

# 10.10 Final Takeaways

The key conclusions of this work are summarized below.

- High-quality multilingual corpora are more valuable than simply increasing dataset size.
- Semantic validation substantially improves supervision quality.
- Prompt contracts reduce instruction ambiguity and improve consistency.
- Balanced multitask learning enables a single model to perform multiple software engineering tasks effectively.
- Parameter-efficient fine-tuning provides substantial performance improvements with minimal computational cost.
- Engineering reproducibility is essential for trustworthy AI experimentation.
- Future progress will likely depend as much upon improved data engineering as upon increasingly larger language models.

These findings collectively validate the engineering methodology proposed throughout this dissertation and establish RepoCoder Studio as a practical, extensible, and reproducible framework for multilingual code intelligence research.

---

# End of Report