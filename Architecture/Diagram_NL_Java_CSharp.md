
> **⚠️ DRAFT**
>
> This diagram is under development and subject to change.

# Table Of Contents

-   [Dataset Generation Pipeline](#dataset-generation-pipeline)
-   [Baseline Accuracy Computation](#baseline-accuracy-computation)
-   [Phase 1: NL -\> Java (PL1)](#phase-1-nl---java-pl1)
-   [Phase 2: Java (PL1) -\> C# (PL2)](#phase-2-java-pl1---c-pl2)

------------------------------------------------------------------------

# Dataset Generation Pipeline

``` mermaid
graph TD
    A([CodeSearchNet Dataset]) --> B[Filter Java records with Natural Language descriptions]
    B --> C@{shape: docs, label: "Multiple NL + Java Records"}

    C -- "For each record" --> D["unsloth/Qwen2.5-Coder-1.5B-Instruct-bnb-4bit"]

    D -- "Generate Java (PL1) from NL" --> E[Generated Java Code]

    E --> F["unsloth/Qwen2.5-Coder-1.5B-Instruct-bnb-4bit"]

    F -- "Translate Java PL1 to CSharp PL2" --> G[Generated CSharp Code]

    subgraph Iteration[Three Iterations]
        subgraph AverageScores[Average Scores]
            G --> H[Compute AST Similarity + GraphCodeBERTScore]
        end
    end

    H --> I{Highest Score}
    I --> J[Store NL + Java + CSharp + Score]

    style A fill:#e1f5fe
    style Iteration fill:#f3e5f5
    style AverageScores fill:#fff3e0
    style J fill:#e8f5e8
```

------------------------------------------------------------------------

# Baseline Accuracy Computation

``` mermaid
flowchart TD
A[CodeSearchNet Dataset] --> B[For each NL + Java sample]

subgraph NLJava["NL to Java PL1"]
B --> C[Prompt model with Natural Language]
C --> D[Generate Java]
D --> E[Compare with Ground Truth Java using AST + GraphCodeBERTScore]
E --> F[Average Score]
end

subgraph JavaCS["Java PL1 to CSharp PL2"]
F --> G[Use Generated/Ground Truth Java]
G --> H[Generate CSharp]
H --> I[Compare with Ground Truth CSharp using AST + GraphCodeBERTScore]
I --> J[Average Score]
end

F --> K[Overall NL to Java Accuracy]
J --> L[Overall Java to CSharp Accuracy]

style NLJava fill:#f3e5f5
style JavaCS fill:#fff3e0
```

------------------------------------------------------------------------

# Phase 1: NL -\> Java (PL1)

``` mermaid
flowchart TD
subgraph Training["Fine Tuning NL to Java"]
A[CodeSearchNet: NL + Java] --> B[LoRA Fine-tuning on unsloth/Qwen2.5-Coder-1.5B-Instruct-bnb-4bit]

subgraph PerRecord[For each record]
B --> C[Input: Natural Language]
C --> D[Generate Java Code]
D --> E[AST + GraphCodeBERTScore against Java Ground Truth]
E --> F[Average Score]
end
end

F --> G[Fine-tuned NL -> Java Model]

style Training fill:#f3e5f5
style PerRecord fill:#fff3e0
```

------------------------------------------------------------------------

# Phase 2: Java (PL1) -\> C# (PL2)

``` mermaid
flowchart TD
subgraph Training["Fine Tuning Java to CSharp"]
A[CodeSearchNet Java Samples] --> B[LoRA Fine-tuning on unsloth/Qwen2.5-Coder-1.5B-Instruct-bnb-4bit]

subgraph PerRecord[For each Java record]
B --> C[Input Java PL1]
C --> D[Generate CSharp (PL2)]
D --> E[AST + GraphCodeBERTScore against C# Ground Truth]
E --> F[Average Score]
end
end

F --> G[Fine-tuned Java to CSharp Model]

style Training fill:#f3e5f5
style PerRecord fill:#fff3e0
```
