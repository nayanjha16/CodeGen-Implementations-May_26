# **Table Of Contents**

- [Document Generation Fidelity Diagram](#document-generation-fidelity-diagram)
- [Baseline Accuracy Computation](#baseline-accuracy-computation)
- [Phase 1: NL -> PL1](#phase-1-nl---pl1)
- [Phase 2: PL1 -> PL2](#Phase-2--PL1----PL2)

---

## Document Generation Fidelity Diagram
The diagram below shows the steps to generate documentation for the programs (C++ and python); and the steps to ensure fidelity of the documentation generated.

```mermaid
graph TD
    A([bigcode/the-stack-dedup dataset]) --> B[Filter by language = C++, Python]
    B --> C@{ shape: docs, label: "Multiple records from Dataset"}
    C -- "Pass each record"--> D[Qwen/Qwen2.5-Coder-3B-Instruct model]
    D --> E[codegen-350m-multi model]
    E -- "Code documentation, intent and programming language" --> F("codegen-350m-multi model")
    subgraph Iteration[Three Iterations]

        subgraph AverageScores[AverageScores]
        F -- " code generated from documentation"--> G("Generate AST and GraphCodeBERTScore")
        end
    end

    G --> L{Select highest score}
    L --> M[Add documentation + score to dataset]
    style A fill:#e1f5fe
    style Iteration fill:#f3e5f5
    style AverageScores fill:#fff3e0
    style M fill:#e8f5e8
```

---


## Baseline Accuracy Computation

The diagram below shows the baseline accuracy computation for NL->PL1 and PL1->PL2 conversions.

```mermaid
flowchart TD
    A[Dataset with C++ and Python code + documentation] --> B[For each record]

    subgraph NLtoPL[NL -> PL1 Conversion]
        B --> C[Give documentation to codegen-350m-multi]
        C -- "Generate code for C++ or Python" --> D[Generated code in programming language]
        D --> E[Compare: AST + GraphCodeBERTScore]
        E --> F[Average scores]
        F --> G[Save score as NL->PL1 score]
    end

    subgraph PLtoPL[PL1 -> PL2 Conversion - Python records only]
        B -- "If Python" --> H1[Documentation]
        H1 --"Generate C++ code"--> H[codegen-350m-multi]
        H --> I[C++ Code]
        I -- "Generate Python Code" -->J[codegen-350m-multi]
        J --> K[Generated Python code]
        K --> L[Compare: AST + GraphCodeBERTScore with ground truth]
        L --> M[Average scores]
        M --> N[Save score as PL1->PL2 score]
    end

    G --> O[Accuracy NL->PL1 = Average of all NL->PL1 scores <br>Accuracy PL1->PL2 = Average of all PL1->PL2 scores]
    N --> O

    style A fill:#e1f5fe
    style NLtoPL fill:#f3e5f5
    style PLtoPL fill:#fff3e0
```

---


## Phase 1: NL -> PL1
The diagram below shows the LORA fine tuning of the codegen-350m-multi to create programs from C++ and python documentation, where the documentation serve as prompt to generate code

```mermaid
flowchart TD
    subgraph Training[Fine Tuning NL -> PL]
        A[Dataset with C++ and Python code] --> B[LORA PEFT codegen-350m-multi]
        direction TB
        subgraph PerRecord[For each C++ & Python record]
            direction TB
            B --> C[Generate code from documentation for the programming language]
            C --> D[Perform AST and GraphCodeBERTScore for generated vs ground truth]
            D --> E[Average the scores]
        end
    end

    style Training fill:#f3e5f5
    style PerRecord fill:#fff3e0
    E --> F[Fine Tuned Model for NL -> Pl1]
```

---

## Phase 2: PL1 -> PL2
The phase 2 of the fine tuning is where in the dataset, for the python programming language, the documentation is taken and passed to the PEFT codegen-350m-multi to create C++ program. This is different from Phase 1 since in phase 1, the output generated was same programming language as in the dataset. The generated C++ code is then given to the PEFT codegen-350m-multi to create python program. The generated python program is then AST and GraphCodeBERTScore compared with the ground truth python program.
``` mermaid
flowchart TD
        subgraph Training[Training]
            A[Dataset with Python code] --> B
            subgraph PerRecord[For each and Python record]
            direction TB
                A -- " Generate C++ code for python documentation" --> B[LORA PEFT codegen-350m-multi]
                B -- "Generated C++ Code, convert to python" --> C[LORA PEFT codegen-350m-multi]
                C --> D[Python Code]
                D --> E[Perform AST and GraphCodeBERTScore for generated vs ground truth]
                E --> F[Average the scores]
            end
        end

        style Training fill:#f3e5f5
        style PerRecord fill:#fff3e0
        F --> G[Fine Tuned Model for NL -> Pl1]
```