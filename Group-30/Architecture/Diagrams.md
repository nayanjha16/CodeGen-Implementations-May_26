
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
## Baseline Accuracy Computation

## Phase 1: NL -> PL1
The diagram below shows the LORA fine tuning of the codegen-350m-multi to create programs from C++ and python documentation, where the documentation serve as prompt to generate code

Dataset with C++ and python code
LORA PEFT codegen-350m-multi
for each C++ and python record
training:
    generate code from the documentation for the programming language
    perform AST and GraphCodeBERTScore for the generated program and the ground truth program in the dataset. Average the scores.
