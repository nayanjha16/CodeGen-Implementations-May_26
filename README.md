# CodeGen-Implementations-May_26

## Natural Language to Code Generation and Translation Framework

### Group 39

This project focuses on developing an intelligent code generation framework that transforms **Natural Language (NL)** descriptions into executable code in **Programming Language 1 (Python)** and further translates the generated code into **Programming Language 2 (e.g., C++)**. The project also explores **Natural Language to SQL generation**, enabling users to interact with databases using plain English queries.

---

## Team Members

| Name | GitHub Profile |

| ----------------- | ----------------------------------- |

| Abhinaya Thavishi | https://github.com/abhinayathavishi |

| Mahin Nandipa | https://github.com/mahin-aeroai |

| Ashu Bagul | https://github.com/ashu60997 |

---

## Project Overview

Modern software development increasingly relies on AI-assisted code generation. This project investigates how Large Language Models (LLMs) can be leveraged to:

1. Convert Natural Language descriptions into executable Programming Language 1.

2. Translate generated Programming Language 1 into another programming language such as C++.

3. Generate SQL queries directly from Natural Language prompts.

4. Evaluate semantic equivalence between generated programs using Abstract Syntax Trees (ASTs) and execution-based validation.

The framework aims to reduce development effort, improve accessibility for non-programmers, and provide a foundation for multilingual code generation systems.

---

## System Architecture

```text

Natural Language Input

           │

           ▼

     Preprocessing

           │

           ▼

      LLM Model

           │

   ┌───────┼────────┐

   ▼       ▼        ▼

 Python   SQL   Documentation

   │

   ▼

 Code Translation

   │

   ▼

 Programming Language 2

   │

   ▼

 AST Analysis

   │

   ▼

 Evaluation Metrics

```

## Project Workflow

### Module 1: Natural Language to Python

```text

Natural Language

       ↓

Prompt Construction

       ↓

LLM Inference

       ↓

Python Code

```

### Module 2: Python to C++

```text

Python Code

      ↓

Translation Model

      ↓

C++ Code

```

### Module 3: Natural Language to SQL

```text

Natural Language

      ↓

Schema Extraction

      ↓

SQL Generation

      ↓

Query Execution

```

### Module 4: Evaluation

```text

Generated Code

       ↓

AST Generation

       ↓

Similarity Analysis

       ↓

Execution Accuracy

       ↓

Performance Metrics

```

## Repository Structure

```text

CodeGen-Implementations-May_26/

│

├── datasets/

│

├── models/


│

├── notebooks/

│

├── src/

│

├── results/

│

├── README.md

│

└── requirements.txt

```

This project investigates the effectiveness of Large Language Models for:

- Natural Language to Code Generation

- Cross-Language Code Translation

- Natural Language to SQL Generation

- AST-Based Semantic Evaluation

The outcomes provide insights into the practical application of generative AI for software development and database interaction.
