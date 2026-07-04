# System Architecture

High-level architecture diagrams for the CodeGen Fine-Tuning with PEFT & LoRA capstone project: system overview, training, evaluation, validation, and testing.

---

## 1. System Context (Level 0)

Shows the project boundary and external dependencies.

```mermaid
flowchart TB
    subgraph External["External Services & Data"]
        HF["HuggingFace Hub<br/>Base model + TEND dataset"]
        Ollama["Ollama API<br/>Semantic judge (qwen3:4b)"]
    end

    subgraph CodeGenPEFT["CodeGen PEFT / LoRA Pipeline"]
        CLI["CLI Scripts"]
        SRC["src/ Python packages"]
        CFG["configs/default.yaml + .env"]
    end

    subgraph Artifacts["Local Artifacts"]
        BASE["models/base/<br/>Cached base weights"]
        CKPT["models/checkpoints/<br/>LoRA adapters"]
        CACHE["data/cache/tend/<br/>Dataset cache"]
        GOLD["data/spider_gold_validation.jsonl<br/>Frozen benchmark"]
        RES["results/<br/>metrics.json + CSVs"]
        MLF["mlflow.db<br/>Experiment tracking"]
    end

    HF --> BASE
    HF --> CACHE
    CFG --> CLI
    CLI --> SRC
    SRC --> BASE
    SRC --> CKPT
    SRC --> CACHE
    SRC --> GOLD
    SRC --> RES
    SRC --> MLF
    Ollama --> SRC
```

---

## 2. High-Level Component Architecture (Level 1)

```mermaid
flowchart TB
    subgraph Config["Configuration Layer"]
        ENV[".env<br/>MODEL_NAME, paths, Ollama"]
        YAML["configs/default.yaml<br/>hyperparams, LoRA, generation"]
    end

    subgraph Data["Data Layer — src/datasets/"]
        TEND["TENDLoader<br/>HF Spider + BIRD"]
        GOLD["load_gold_validation<br/>50 frozen examples"]
        PRE["preprocess.py"]
    end

    subgraph Model["Model Layer — src/models/"]
        ML["model_loader.py<br/>CodeGenModel + PeftModel"]
        CACHE["ensure_model_cached"]
    end

    subgraph Tasks["Task Layer — 3 independent pipelines"]
        T2S["src/text2sql/<br/>PromptBuilder, SQLGenerator,<br/>SQLValidator, SQLExecutor"]
        S2N["src/sql2nosql/<br/>NoSQLPromptBuilder, NoSQLGenerator"]
        N2D["src/documentation/<br/>DocPromptBuilder, DocGenerator"]
    end

    subgraph Training["Training Layer — src/training/"]
        DS["tend_dataset.py<br/>SFT dataset builder"]
        PF["prompt_factory.py<br/>Training prompt parity"]
        LT["lora_trainer.py<br/>TRL SFTTrainer"]
        AV["adapter_verify.py"]
    end

    subgraph Eval["Evaluation Layer — src/evaluation/"]
        BR["benchmark.py<br/>BenchmarkRunner"]
        MET["metrics.py<br/>EM, exec acc, CodeBLEU..."]
        EXP["export.py<br/>CSV + metrics.json"]
        JUD["ollama_judge.py"]
        MFT["mlflow_tracker.py"]
    end

    subgraph Utils["Utilities — src/utils/"]
        U1["config, device, paths, seeds, logging"]
    end

    ENV --> U1
    YAML --> U1
    U1 --> Data
    U1 --> Model
    U1 --> Training
    U1 --> Eval

    Data --> Training
    Data --> Eval
    Model --> Tasks
    Model --> Training
    Tasks --> Eval
    Training --> Model
    Eval --> JUD
    Eval --> MFT
```

---

## 3. Three-Task Pipeline Architecture

Each task is **independent** at both training and evaluation time. Gold fields from the same dataset row are used — outputs are never chained.

```mermaid
flowchart LR
    subgraph Row["TEND / Gold Validation Row"]
        Q["question"]
        SS["schema"]
        SQL["sql (gold)"]
        NS["nosql_schema"]
        NQ["nosql_query (gold)"]
        DOC["documentation (gold)"]
    end

    subgraph Task1["Task 1: Text2SQL"]
        P1["PromptBuilder<br/>question + schema"]
        G1["SQLGenerator<br/>+ text2sql LoRA"]
        M1["EvaluationMetrics"]
    end

    subgraph Task2["Task 2: SQL2NoSQL"]
        P2["NoSQLPromptBuilder<br/>gold sql + schemas"]
        G2["NoSQLGenerator<br/>+ sql2nosql LoRA"]
        M2["NoSQLEvaluator"]
    end

    subgraph Task3["Task 3: NoSQL2Doc"]
        P3["DocPromptBuilder<br/>gold nosql_query + schema"]
        G3["DocGenerator<br/>+ nosql2doc LoRA"]
        M3["DocumentationEvaluator"]
    end

    Q --> P1
    SS --> P1
    P1 --> G1 --> M1

    SQL --> P2
    SS --> P2
    NS --> P2
    P2 --> G2 --> M2

    NQ --> P3
    NS --> P3
    Q --> P3
    P3 --> G3 --> M3

    M1 --> OUT["results/metrics.json<br/>+ detail CSVs"]
    M2 --> OUT
    M3 --> OUT
```

---

## 4. Training Architecture

```mermaid
flowchart TD
    START["train_all_lora.py<br/>or train_lora.py"] --> CFG["Load config + resolve device<br/>(cuda > mps > dml > cpu)"]
    CFG --> BASELINE{--run-baseline?}
    BASELINE -->|yes| BE["run_baseline_eval.py<br/>(no adapter)"]
    BE --> RES1["results/baseline metrics"]
    BASELINE -->|no| LOOP
    RES1 --> LOOP

    LOOP["For each task:<br/>text2sql → sql2nosql → nosql2doc"]

    LOOP --> LOAD["Load TEND spider+bird train<br/>(~10,697 rows)"]
    LOAD --> FILTER["Filter rows by required fields<br/>+ token budget (2048)"]
    FILTER --> BUILD["build_training_prompt() + target<br/>(matches inference prompts)"]
    BUILD --> SFT["prepare_prompt_completion_dataset<br/>completion-only loss"]
    SFT --> MODEL["Load base model from models/base/"]
    MODEL --> LORA["Apply PEFT LoRA<br/>r=16, alpha=32<br/>target: qkv_proj, out_proj"]
    LORA --> TRAIN["TRL SFTTrainer<br/>5 epochs, lr=2e-4<br/>effective batch=32"]
    TRAIN --> SAVE["Save adapter to<br/>models/checkpoints/v1/task/"]
    SAVE --> META["Write run_metadata.json"]
    META --> MORE{More tasks?}
    MORE -->|yes| LOOP
    MORE -->|no| VERIFY["verify_all_adapters()"]
    VERIFY --> SUMMARY["training_summary.json"]
```

### LoRA Model Architecture

```mermaid
flowchart TB
    subgraph Base["Frozen Base Model (codegen-350M-multi)"]
        EMB["Token Embeddings"]
        ATT["Attention Layers<br/>qkv_proj, out_proj"]
        FFN["Feed-Forward Layers"]
        HEAD["LM Head"]
    end

    subgraph Adapters["Trainable LoRA Adapters (per task)"]
        L1["text2sql ΔW<br/>~few MB"]
        L2["sql2nosql ΔW<br/>~few MB"]
        L3["nosql2doc ΔW<br/>~few MB"]
    end

    ATT -.->|"LoRA injects<br/>low-rank matrices"| L1
    ATT -.-> L2
    ATT -.-> L3

    PROMPT["Task-prefixed prompt<br/>Task: text2sql"] --> EMB
    EMB --> ATT --> FFN --> HEAD --> OUT["Generated completion"]
```

---

## 5. Evaluation Architecture

```mermaid
flowchart TD
    START["run_baseline_eval.py"] --> INIT["BenchmarkRunner<br/>load base + optional adapters"]
    INIT --> DATA{Dataset source}
    DATA -->|default| GOLD["spider_gold_validation.jsonl<br/>(50 frozen examples)"]
    DATA -->|--full-split| TEND["TENDLoader test split<br/>(859 spider / 766 bird)"]

    GOLD --> RUN["run_on_dataset()"]
    TEND --> RUN

    RUN --> T1["Text2SQL batch generation"]
    RUN --> T2["SQL2NoSQL batch generation"]
    RUN --> T3["Documentation batch generation"]

    T1 --> AM1["Automated metrics<br/>EM, exec acc, CodeBLEU..."]
    T2 --> AM2["Automated metrics<br/>token F1, structural equiv..."]
    T3 --> AM3["Automated metrics<br/>BLEU, ROUGE-L..."]

    AM1 --> MERGE["Merge task metrics"]
    AM2 --> MERGE
    AM3 --> MERGE

    MERGE --> JUDGE{Ollama judge?}
    JUDGE -->|yes| OLL["OllamaJudge<br/>semantic equivalence"]
    JUDGE -->|no| EXPORT
    OLL --> EXPORT

    EXPORT["Export artifacts"]
    EXPORT --> MJSON["metrics.json"]
    EXPORT --> CSV1["text2sql_details.csv"]
    EXPORT --> CSV2["sql2nosql_details.csv"]
    EXPORT --> CSV3["documentation_details.csv"]

    MERGE --> MLF{--mlflow?}
    MLF -->|yes| MLFLOW["MLflowTracker.log_evaluation"]
```

---

## 6. Validation & Testing Architecture

Three distinct layers: **unit/smoke tests**, **training validation**, and **benchmark evaluation**.

```mermaid
flowchart TB
    subgraph UnitTests["Unit & Smoke Tests — tests/"]
        T1["test_prompt_parity.py<br/>Train prompts = inference prompts"]
        T2["test_overfit_smoke.py<br/>5 rows → loss < 1.5"]
        T3["test_adapter_load.py<br/>Generate after training"]
        T4["test_adapter_verify.py<br/>Artifact checks"]
        T5["test_device.py<br/>Device resolution"]
    end

    subgraph TrainingValidation["Training Validation"]
        V1["inspect_lora_modules.py<br/>LoRA target modules"]
        V2["build_sft_dataset.py<br/>Filter + token stats"]
        V3["test_tend_loader.py<br/>HF dataset integrity"]
        V4["verify_lora_adapters.py<br/>Post-training artifacts"]
        V5["validate_lora_smoke.py<br/>End-to-end smoke"]
    end

    subgraph BenchmarkEval["Benchmark Evaluation (Held-Out)"]
        B1["spider_gold_validation.jsonl<br/>50 frozen examples"]
        B2["TEND test split<br/>(training eval_loss)"]
        B3["Baseline vs LoRA comparison<br/>results/*/metrics.json"]
    end

    subgraph SemanticValidation["Semantic Validation (Optional)"]
        S1["Ollama judge<br/>qwen3:4b"]
        S2["Per-sample judge_* columns<br/>in detail CSVs"]
    end

    UnitTests -->|"CI / pre-commit"| PASS1["Pipeline integrity"]
    TrainingValidation -->|"Before & after training"| PASS2["Training correctness"]
    BenchmarkEval -->|"Capstone results"| PASS3["Model quality"]
    SemanticValidation --> PASS3
```

### Validation vs Testing vs Evaluation

| Layer | What | When | Dataset | Pass criteria |
|-------|------|------|---------|---------------|
| **Unit tests** | Code correctness | Every commit | Synthetic (5 rows) | All tests pass |
| **Training validation** | Pipeline smoke | Before full train | 50 samples | Adapters saved, loss decreases |
| **Training eval** | Held-out loss | During training | TEND test (~1,625 rows) | eval_loss tracked per epoch |
| **Benchmark eval** | Model quality | After training | Gold validation (50) | Metrics vs baseline |
| **Semantic judge** | Human-like correctness | Optional post-eval | Same 50 examples | judge_correct_rate |

---

## 7. End-to-End Lifecycle

Complete capstone workflow from setup to results.

```mermaid
sequenceDiagram
    participant Dev as Researcher
    participant Setup as Setup Scripts
    participant Test as Unit Tests
    participant Base as Baseline Eval
    participant Train as LoRA Training
    participant Verify as Adapter Verify
    participant LoRA as LoRA Eval
    participant MLflow as MLflow

    Dev->>Setup: pip install, .env, PYTHONPATH
    Dev->>Test: unittest discover tests/
    Test-->>Dev: All pass

    Dev->>Base: run_baseline_eval.py
    Base-->>Dev: results/baseline/metrics.json

    Dev->>Train: train_all_lora.py --run-baseline --version v1
    Train->>Base: Optional baseline snapshot
    Train->>Train: SFT per task (text2sql, sql2nosql, nosql2doc)
    Train-->>Dev: models/checkpoints/v1/*/adapter_*

    Dev->>Verify: verify_lora_adapters.py --version v1
    Verify-->>Dev: All artifacts OK

    Dev->>LoRA: run_baseline_eval.py --adapter-run v1
    LoRA-->>Dev: results/lora/metrics.json + CSVs

    Dev->>MLflow: mlflow ui (optional)
    MLflow-->>Dev: Compare runs visually
```

---

## 8. Directory Structure Map

```
CodeGen-Implementations-May_26/
├── configs/default.yaml          ← Runtime hyperparameters
├── .env                          ← Model name, paths, secrets
├── scripts/
│   ├── train_lora.py             ← Single-task training
│   ├── train_all_lora.py         ← Multi-task orchestration
│   ├── run_baseline_eval.py      ← Primary evaluation
│   └── verify_lora_adapters.py   ← Post-training checks
├── src/
│   ├── text2sql/                 ← Task 1
│   ├── sql2nosql/                ← Task 2
│   ├── documentation/            ← Task 3
│   ├── models/                   ← HF model loader + LoRA
│   ├── datasets/                 ← TEND loader
│   ├── training/                 ← LoRA trainer + SFT builder
│   ├── evaluation/               ← Metrics + benchmark
│   └── utils/                    ← Config, device, paths
├── models/
│   ├── base/                     ← Cached HuggingFace weights
│   └── checkpoints/v1/           ← LoRA adapter outputs
├── data/
│   ├── spider_gold_validation.jsonl  ← Frozen benchmark
│   └── cache/tend/               ← HF dataset cache
├── results/                      ← Evaluation outputs
└── tests/                        ← Unit + smoke tests
```

---

## 9. Data Flow Summary

```mermaid
flowchart LR
    HF["HuggingFace TEND"] --> CACHE["Local JSONL cache"]
    CACHE --> TRAIN["LoRA Training<br/>(train split)"]
    CACHE --> TE["Training eval_loss<br/>(test split)"]
    GOLD["Gold validation JSONL"] --> EVAL["Benchmark Eval"]
    TRAIN --> CKPT["LoRA adapters"]
    CKPT --> EVAL
    BASE["Base model weights"] --> TRAIN
    BASE --> EVAL
    EVAL --> RES["results/"]
    RES --> COMP["Baseline vs LoRA<br/>comparison"]
```
