# Final Presentation — Detailed Slide Deck Guide

> **Purpose:** Everything you need to build the final defense / demo presentation.  
> **Not a summary** — copy talking points, tables, diagrams, and demo scripts into slides.  
> **Final model version for results:** **LoRA v4** (`checkpoint_version: v4` in `hf-deploy/manifest.yaml`).  
> **Update placeholders** marked `TODO:` (team names, demo video URL, Cloud Run URL if shown live).

**This document is self-contained** — all capstone context, architecture, methodology, dataset details, v4 results, deployment guides, and Q&A prep are included below. External links are limited to public web resources (Hugging Face, PyPI, Ollama, etc.).

**Suggested timing (~15–20 min + Q&A)**


| Slide     | Focus                                       | Time                 |
| --------- | ------------------------------------------- | -------------------- |
| 1         | Title + team                                | 1 min                |
| 2         | Problem, architecture, IDE path, why a tool | 3–4 min              |
| 3         | TEND dataset pipeline                       | 3–4 min              |
| 4         | Project + LoRA v4 results                   | 4–5 min              |
| 5         | Deployments (Cloud Run, HF, tool)           | 2–3 min              |
| 6         | Demo video                                  | 2–3 min              |
| 7         | Thank you + questions                       | 1 min + Q&A          |
| **A1–A8** | **Appendix — judge Q&A / impress slides**   | jump during Q&A only |


---



# SLIDE 1 — Title & Team



## Slide title (on screen)

**Interactive Database Querying Using Small Code Language Models**

**Subtitle: CodeGen Fine-Tuning with PEFT & LoRA***

## Subtitle lines (pick what fits your program branding)

- Fine-tuning `Salesforce/codegen-350M-multi` with **PEFT / LoRA**
- Three tasks: **Text→SQL** · **SQL→MongoDB** · **NoSQL→Documentation**
- Dataset: **TEND** ([care2achieve/tend](https://huggingface.co/datasets/care2achieve/tend))
- Production path: **Hugging Face adapters** + **Google Cloud Run API** + **desktop tool**



## Team members

All team members contributed across every project task (dataset, training, evaluation, deployment, tool, and presentation).

- Naresh Reddy Yadulla
- Mohana K Kishore Dwadasi
- Sivakrishna Andraju

**On slide:** list names only — no roles or per-person task split.

- Institution / program / course name — **TODO**
- Date — **TODO**
- Mentors / advisors (if required) — **TODO**
- Repo / org: `care2achieve` (HF org for models + dataset)



## Speaker notes (Slide 1)

> “We fine-tuned a **350M** code language model with **LoRA** on an execution-validated multi-task dataset we built — **TEND** — covering natural language to SQL, SQL to MongoDB, and query documentation. Our **final adapters are LoRA v4**. We also shipped the model as an OpenAI-compatible API on **Cloud Run**, published adapters on **Hugging Face**, and built a **desktop Text-to-SQL tool** that generates, validates, and executes SQL against a live PostgreSQL database.”



## Visual suggestions

- Clean title slide; logo of institution if required
- Small icons: Hugging Face, Google Cloud, PostgreSQL/MongoDB, CodeGen
- Do **not** overload with metrics on slide 1

---



# SLIDE 2 — Problem Statement, Architecture, IDE Extension Path, Why Build a Tool



## 2.1 Problem statement (on screen — short bullets)

**Modern apps use both SQL and NoSQL.** Developers and analysts need to:

1. Turn **natural-language questions** into correct **SQL**
2. Translate **SQL** into **MongoDB** shell queries
3. Produce **human-readable documentation** for NoSQL queries

**Why this is hard**

- Full fine-tuning of large LMs is costly and impractical for research / edge / student hardware
- Zero-shot small code LMs (e.g. CodeGen-350M) are weak on structured DB tasks
- Training data for **aligned** NL ↔ SQL ↔ Mongo ↔ docs with **execution proof** is rare
- IDE copilots (Cursor / VS Code) need a **deployable, OpenAI-compatible** endpoint — not a research notebook

**Our answer**

- One frozen base model + **three small LoRA adapters** (few–tens of MB each)
- Train and evaluate on **TEND** (Spider + BIRD, multi-task, execution-validated gold)
- Serve via **FastAPI** (intent → adapter hot-swap) on **Cloud Run / HF**
- Prove usefulness with a **desktop tool** that runs generated SQL against a real DB



## 2.2 System architecture (use diagram on slide)



### End-to-end product architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│  Clients                                                                │
│  • Desktop AI SQL Assistant                                             │
│  • Cursor / VS Code (OpenAI base URL → /v1/chat/completions)            │
│  • curl / any OpenAI-compatible SDK                                     │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ HTTPS / localhost
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  Multi-Adapter API Gateway                                              │
│  Intent classifier (rules + MiniLM embeddings)                          │
│  Prompt builder (Task: text2sql | sql2nosql | nosql2doc)                │
│  PEFT set_adapter hot-swap                                              │
│  Base: Salesforce/codegen-350M-multi + 3 LoRA adapters (v4)             │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
   text2sql LoRA         sql2nosql LoRA         nosql2doc LoRA
   (NL + schema → SQL)   (SQL → Mongo)          (Mongo → docs)
```



### Research / training architecture (three independent tasks)

Emphasize: **tasks are trained and evaluated independently** with **gold** fields — we do **not** chain predicted SQL into sql2nosql during benchmarking (that would confound errors).


| Task          | Input                                  | Output              | Adapter     |
| ------------- | -------------------------------------- | ------------------- | ----------- |
| **Text2SQL**  | Question + SQL schema                  | SQL                 | `text2sql`  |
| **SQL2NoSQL** | Gold SQL + SQL/Mongo schemas           | MongoDB shell query | `sql2nosql` |
| **NoSQL2Doc** | Gold Mongo query + schema (+ question) | Documentation       | `nosql2doc` |


```text
TEND / gold row
  question, schema, sql, nosql_schema, nosql_query, documentation
        │
        ├─► Text2SQL:  question + schema  ──► predicted SQL
        ├─► SQL2NoSQL: gold SQL + schemas ──► predicted Mongo
        └─► NoSQL2Doc: gold Mongo + schema ──► predicted docs
```



### Research pipeline modules (talking depth)


| Layer      | Component                                      | Role                                                         |
| ---------- | ---------------------------------------------- | ------------------------------------------------------------ |
| Config     | Runtime configuration                          | Model name, LoRA, generation, seeds                          |
| Data       | Dataset loader & benchmark                     | TEND HF loader, gold validation set                          |
| Model      | Model & adapter manager                        | Cache base weights; load PEFT adapters                       |
| Tasks      | Text2SQL · SQL2NoSQL · Documentation pipelines | Prompt builders, generators, validators                      |
| Training   | LoRA training pipeline                         | SFT dataset, LoRA trainer (TRL), prompt parity               |
| Evaluation | Benchmark & metrics engine                     | EM, exec accuracy, CodeBLEU, BERTScore, Ollama judge, MLflow |
| Deploy     | Multi-adapter API gateway                      | OpenAI-compatible API + classifier + Cloud Run               |
| Product UI | Desktop AI SQL Assistant                       | Text-to-SQL against PostgreSQL                               |


**Backup architecture diagrams** (optional slides if judges want more detail):

### System context (Level 0)

```mermaid
flowchart TB
    subgraph External["External Services & Data"]
        HF["HuggingFace Hub<br/>Base model + TEND dataset"]
        Ollama["Ollama API<br/>Semantic judge (qwen3:8b)"]
    end

    subgraph CodeGenPEFT["CodeGen PEFT / LoRA Pipeline"]
        CLI["Training & Evaluation Orchestration"]
        SRC["Core Pipeline Modules"]
        CFG["Runtime Configuration"]
    end

    subgraph Artifacts["Artifacts & Storage"]
        BASE["Base Model Cache"]
        CKPT["LoRA Adapter Store"]
        CACHE["Dataset Cache"]
        GOLD["Frozen Benchmark Set (50 examples)"]
        RES["Evaluation Results Store"]
        MLF["Experiment Tracking (MLflow)"]
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





### High-level component architecture (Level 1)

```mermaid
flowchart TB
    subgraph Config["Configuration Layer"]
        ENV["Environment Settings<br/>model, paths, Ollama"]
        YAML["Hyperparameter Config<br/>LoRA, generation, training"]
    end

    subgraph Data["Data Layer"]
        TEND["TEND Dataset Loader<br/>HF Spider + BIRD"]
        GOLD["Gold Benchmark Loader<br/>50 frozen examples"]
        PRE["Data Preprocessor"]
    end

    subgraph Model["Model Layer"]
        ML["Model Loader<br/>CodeGen + PEFT adapters"]
        CACHE["Weight Cache Manager"]
    end

    subgraph Tasks["Task Layer — 3 independent pipelines"]
        T2S["Text2SQL Pipeline<br/>Prompt · Generate · Validate · Execute"]
        S2N["SQL2NoSQL Pipeline<br/>Prompt · Generate · Evaluate"]
        N2D["Documentation Pipeline<br/>Prompt · Generate · Evaluate"]
    end

    subgraph Training["Training Layer"]
        DS["SFT Dataset Builder"]
        PF["Prompt Parity Factory"]
        LT["LoRA Trainer (TRL SFTTrainer)"]
        AV["Adapter Verifier"]
    end

    subgraph Eval["Evaluation Layer"]
        BR["Benchmark Runner"]
        MET["Metrics Engine<br/>EM, exec acc, CodeBLEU..."]
        EXP["Results Exporter"]
        JUD["Semantic Judge (Ollama)"]
        MFT["MLflow Tracker"]
    end

    subgraph Utils["Shared Utilities"]
        U1["Config · Device · Paths · Seeds · Logging"]
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





### Three-task pipeline (independent evaluation)

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
        P1["Prompt builder<br/>question + schema"]
        G1["SQL generator<br/>+ text2sql LoRA"]
        M1["Evaluation metrics"]
    end

    subgraph Task2["Task 2: SQL2NoSQL"]
        P2["NoSQL prompt builder<br/>gold sql + schemas"]
        G2["NoSQL generator<br/>+ sql2nosql LoRA"]
        M2["NoSQL evaluator"]
    end

    subgraph Task3["Task 3: NoSQL2Doc"]
        P3["Doc prompt builder<br/>gold nosql_query + schema"]
        G3["Doc generator<br/>+ nosql2doc LoRA"]
        M3["Documentation evaluator"]
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

    M1 --> OUT["Evaluation Results<br/>+ per-task detail reports"]
    M2 --> OUT
    M3 --> OUT
```





## 2.3 Extending to Cursor or VS Code (short notes for the slide)



### Why this maps cleanly to Cursor / VS Code


| Principle                   | What we built                                 | IDE implication                                           |
| --------------------------- | --------------------------------------------- | --------------------------------------------------------- |
| **OpenAI-compatible API**   | `POST /v1/chat/completions`, `GET /v1/models` | Cursor Settings → custom model base URL works today       |
| **Stateless inference**     | Server only sees the prompt                   | Extension owns workspace; model never scans the repo      |
| **Intent routing**          | Rules + embeddings → adapter                  | User speaks naturally (“write SQL…”, “convert to Mongo…”) |
| **Schema in prompt (MVP)**  | Client injects schema                         | Extension / tool retrieves schema locally, then calls API |
| **Multi-adapter, one base** | `set_adapter` hot-swap                        | One endpoint, three skills, small download footprint      |




### Cursor (works now — demo-ready)

Configure Cursor:


| Setting  | Value                                                                      |
| -------- | -------------------------------------------------------------------------- |
| Base URL | `http://localhost:8000/v1` **or** Cloud Run `https://<service>.run.app/v1` |
| Model    | `codegen-multi-adapter`                                                    |


Optional request field `"intent": "text2sql"` skips classification.

**Architecture for Cursor**

```text
Cursor IDE
   │  OpenAI-compatible chat
   ▼
Multi-Adapter API Gateway (Cloud Run or local)
   │  intent classification → adapter hot-swap → generate
   ▼
Response (+ routing metadata: intent, confidence, method)
```

**Cursor deployment summary:** OpenAI-compatible `POST /v1/chat/completions`; intent classifier (rules → MiniLM embeddings → clarify); schema in user prompt (MVP); PEFT `set_adapter` hot-swap; optional `"intent": "text2sql"` override. See **Reference Appendix K** for the full deployment plan.

### VS Code extension (designed path — impress with roadmap)

**VS Code extension spec (summary):** Local-first workspace scan, schema discovery, semantic index (BAAI/bge-small-en-v1.5), intent detection, top-K schema retrieval, prompt builder per adapter, Hugging Face OpenAI client — model stays stateless. Milestones: scaffold → SQL parser → embeddings → retrieval → HF client → Chat UI. See **Reference Appendix L** for the full technical specification.

**Design principles**

1. **Local-first** — workspace scan, schema discovery, semantic indexes stay on the machine
2. **Stateless model** — HF / Cloud Run only does inference
3. **Incremental indexing** — re-index changed files only
4. **Extensible adapters** — new tasks = new PromptBuilders, same gateway

**Extension responsibilities vs server**


| VS Code extension (local)         | Remote model (Cloud Run / HF) |
| --------------------------------- | ----------------------------- |
| Scan workspace / DB schemas       | Receive complete prompt       |
| Build semantic index              | Route intent → LoRA           |
| Detect intent (or rely on server) | Generate completion           |
| Retrieve top-K relevant tables    | Return text only              |
| Build final prompt + show Chat UI | No repo state                 |


**Talking line for judges:**  

> “We already ship the **server contract** Cursor and VS Code need. The desktop tool proves schema retrieval + execute loop today; the VS Code extension is the same pattern inside the editor.”



## 2.4 Why build a tool? (not only train a model)

Put these bullets on the slide — judges care about **impact**, not only metrics.


| Reason                     | Explanation                                                                                                                   |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Close the loop**         | Research metrics ≠ usefulness. The tool **generates → validates (SELECT-only) → executes** on real PostgreSQL and shows rows. |
| **Schema realism**         | Uses embedding-based **table selection** + Pagila/DVD schema — closer to how an IDE would inject schema.                      |
| **Product path**           | Shows the same API Cursor would call; tool is a **reference client**.                                                         |
| **Demoability**            | Live UI + activity log (`schema_loaded` → `sql_generated` → `rows_retrieved`) beats a CSV of scores.                          |
| **Safety**                 | Validation blocks non-SELECT SQL before execution — important for a student / enterprise story.                               |
| **Separation of concerns** | Tool does **not** load LoRA locally; inference is centralized in hf-deploy — same as production.                              |


**One sentence for the slide**

> We built the tool to prove that a small LoRA-tuned model can power an end-to-end Text-to-SQL workflow against a live database — the same workflow an IDE extension would use.



## Speaker notes (Slide 2)

> “The problem is multi-dialect database work with limited compute. We use one 350M CodeGen base and three LoRA adapters. Training and eval stay independent per task so one stage’s mistakes don’t poison the next. For IDEs, we expose an OpenAI-compatible gateway with intent routing — Cursor can point at Cloud Run today; a VS Code extension would keep schema indexing local and call the same API. We built a desktop tool because a model card is not enough: judges need to see generate–validate–execute on a real DB.”

---



# SLIDE 3 — TEND (Dataset) in Detail

> Published dataset: [care2achieve/tend](https://huggingface.co/datasets/care2achieve/tend)  
> TEND is a standalone companion project for execution-validated dataset generation (see **Reference Appendix M**).



## 3.1 What is TEND? (on-screen definition)

**TEND** = **T**ranslation / **E**valuation dataset for **N**atural language ↔ SQL ↔ **D**ocument (NoSQL) pipelines.

Standalone project that:

1. Takes **Spider** and **BIRD** samples (question + gold SQL + schema metadata)
2. Builds **SQL DDL** and **MongoDB schemas** deterministically
3. Converts SQL → MongoDB with a **fallback cascade** (rules → Python converter → Ollama)
4. Uses **Ollama only to generate documentation** for a successfully converted query (not as a query judge)
5. **Executes** SQL on **PostgreSQL** and Mongo on **MongoDB**, keeps rows where results **match**
6. Publishes **execution-validated gold** to Hugging Face for CodeGen training

**Why TEND exists for this capstone**

- Spider/BIRD give NL→SQL only; we need **aligned** SQL→Mongo and Mongo→docs
- Pure LLM synthetic Mongo is unreliable; **deterministic conversion first**, then execution as ground truth
- Same live DB stack supports **evaluation** of LoRA predictions (exec accuracy in results)



## 3.2 Pipeline diagram (put on slide)

```text
sample (question, sql, db_id, schema)
        │
        ▼
  SQL DDL Builder ──► sql_schema (DDL)
        │
        ▼
  Mongo Schema Builder (deterministic) ──► nosql_schema
        │
        ▼
  SQL → MongoDB conversion cascade
        │
        ├─ (1) Rule-based translators
        │         success + validates? ──yes──► nosql_query (source=rules)
        │                    │ no
        │                    ▼
        ├─ (2) SQL→NoSQL converter tool
        │         success + validates? ──yes──► nosql_query (source=converter)
        │                    │ no
        │                    ▼
        ├─ (3) LLM query generation (fallback only)
        │         success + validates? ──yes──► nosql_query (source=llm)
        │                    │ no
        │                    ▼
        └─ Marked FAILED TO CONVERT (empty / invalid nosql_query)
        │
        ▼  (only when nosql_query is valid)
  LLM documentation generator  (generation only — NOT a query judge)
        │
        ▼
  Bronze dataset tier
        │
        ▼  Execution gold filter (execution_accuracy=true)
  Gold dataset tier → Hugging Face publish
```



## 3.3 SQL→MongoDB conversion cascade (impresses judges)

**Order of preference — first success wins. No LLM-as-judge between candidates.**


| Step     | Component                 | When used                             | Examples                                                                                                                                      |
| -------- | ------------------------- | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **1**    | **Rule-based converters** | Pattern-specific Spider/BIRD SQL      | JOIN→`$lookup`, scalar AVG subqueries, `NOT IN`, INTERSECT/EXCEPT                                                                             |
| **2**    | **SQL→NoSQL Python tool** | Rules miss / fail validation          | `SQLToNoSQLTranslator` + `[sql-mongo-converter](https://pypi.org/project/sql-mongo-converter/)` → `find()`, `aggregate()`, `countDocuments()` |
| **3**    | **Ollama codegen**        | **Both** rules and Python tool failed | Complex multi-table / edge-case SQL                                                                                                           |
| **Fail** | —                         | All steps fail validation             | Row marked **failed to convert** (no usable `nosql_query`)                                                                                    |


**Validation** = structural / shell completeness checks (and, when DB env is on, execution comparison against SQL results). Failed conversions do **not** get a “best guess” from a judge.

### Role of Ollama / LLM in TEND (correct story for slides)


| Use                                                               | Yes / No                                       |
| ----------------------------------------------------------------- | ---------------------------------------------- |
| Generate MongoDB query when rules + converter fail                | **Yes** (fallback only)                        |
| Generate **documentation** for a valid Mongo query                | **Yes**                                        |
| Act as **judge** to pick between rule vs converter vs LLM queries | **No**                                         |
| Decide gold tier                                                  | **No** — gold uses **execution accuracy** only |


**Talking point:** Prefer deterministic translation; call the LLM only when needed for the query, and use it for **docs generation**, never as an arbiter of which query is “best.”

## 3.4 Dataset tiers


| Tier       | Produced by                 | Meaning                                               |
| ---------- | --------------------------- | ----------------------------------------------------- |
| **Bronze** | Dataset generation pipeline | All rows (successful conversions + failed-to-convert) |
| **Gold**   | Execution gold filter       | **Only** rows with `execution_accuracy=true`          |


Gold criterion (strict):

- Run gold SQL on **PostgreSQL**
- Run generated Mongo query on **MongoDB**
- Compare **normalized result sets**
- Keep row only if they match

No LLM-judge filter at gold stage — execution only. Rows that **failed to convert** cannot become gold.

## 3.5 Scale & HF publish stats (TEND gold export summary)


| Config    | Split | Bronze     | Gold      | Gold rate |
| --------- | ----- | ---------- | --------- | --------- |
| bird      | test  | 1,534      | 377       | 24.6%     |
| bird      | train | 9,428      | 2,096     | 22.2%     |
| spider    | test  | 1,034      | 658       | 63.6%     |
| spider    | train | 8,659      | 5,944     | 68.6%     |
| **Total** |       | **20,655** | **9,075** | **43.9%** |


**Published HF configs used by CodeGen training** (silver/gold aligned fields):


| Config                    | Train       | Test       |
| ------------------------- | ----------- | ---------- |
| spider                    | 6,730       | 859        |
| bird                      | 3,967       | 766        |
| **Combined (LoRA train)** | **~10,697** | **~1,625** |


> Note: Exact HF row counts vs local gold CSV counts can differ by export/filter version; for the presentation, use **~10.7k train / ~1.6k test** as the CodeGen training corpus size, and cite **9,075** as the execution-validated gold yield from the TEND export summary if discussing dataset construction.



## 3.6 Record schema (one row = three tasks)


| Field                   | Role                                                   |
| ----------------------- | ------------------------------------------------------ |
| `question`              | NL input (text2sql / docs context)                     |
| `sql_schema` / `schema` | DDL for prompting                                      |
| `sql` / `sql_query`     | Gold SQL (target for text2sql; input for sql2nosql)    |
| `nosql_schema`          | Mongo schema JSON                                      |
| `nosql_query`           | Gold Mongo (target for sql2nosql; input for nosql2doc) |
| `documentation`         | Gold docs (target for nosql2doc)                       |
| `db_id`                 | Database id                                            |
| `execution_accuracy`    | Gold filter flag                                       |




## 3.7 Engineering highlights (optional bullets)

- **Chunked + resumable** bronze generation (`--chunked`, 500-row chunks, auto-merge)
- **Conversion cascade** — rules → Python SQL→NoSQL tool → Ollama fallback; failed validation → failed to convert
- **Ollama for docs** (and query fallback only) — **not** used as a query judge
- **Async Ollama** with concurrency semaphore (hours-long Spider/BIRD runs)
- **Docker** PostgreSQL 16 + MongoDB 8 load from Spider/BIRD SQLite
- **Dump/restore** snapshots and gold-validation subset import for demos
- CLI: `tend-run`, `tend-bronze-to-gold`, `tend-publish-hf`, `tend-run-execution-accuracy`



## 3.8 How CodeGen uses TEND


| Use                   | Data                                                                                                    |
| --------------------- | ------------------------------------------------------------------------------------------------------- |
| LoRA training         | HF `care2achieve/tend` spider+bird **train** (~8k–10k filtered rows per task after field/token filters) |
| Training eval_loss    | spider+bird **test**                                                                                    |
| Capstone benchmark    | Frozen `data/spider_gold_validation.jsonl` (**50** examples) — fair baseline vs v1…v4                   |
| Exec accuracy in eval | Live PG/Mongo (same philosophy as TEND gold)                                                            |




## Speaker notes (Slide 3)

> “TEND is our companion system. Spider and BIRD only give us questions and SQL. We deterministically build Mongo schemas, then convert SQL to Mongo with a **cascade**: rule-based translators first, then the **SQL→NoSQL Python tool**, and **only if both fail** we call **Ollama** to generate the query. If nothing validates, we mark the row **failed to convert**. Ollama is also used to **write documentation** — it is **not** a judge picking between candidates. Finally we **keep only rows where SQL and Mongo executions return the same results**. That gold data trains all three LoRA adapters. Roughly 44% of bronze survives to gold — quality over quantity.”

---



# SLIDE 4 — Project Details, Training, Results (LoRA v4 Final)



## 4.1 Project identity (on screen)


| Item          | Detail                                                  |
| ------------- | ------------------------------------------------------- |
| Base model    | `Salesforce/codegen-350M-multi` (~350M params, code LM) |
| Method        | **PEFT LoRA** — base frozen; one adapter per task       |
| Framework     | Hugging Face Transformers + PEFT + TRL `SFTTrainer`     |
| Loss          | **Completion-only** (prompt tokens masked)              |
| Prompt parity | Training prompts == inference prompts (unit-tested)     |
| Hardware path | Local MPS (v1–v3) → **Kaggle CUDA for v4**              |
| Final version | **LoRA v4**                                             |
| Tracking      | MLflow (optional), `run_metadata.json`, results CSVs    |




## 4.2 Version progression (tell the story)


| Version        | Train samples | Epochs | LoRA                       | Device          | Story                     |
| -------------- | ------------- | ------ | -------------------------- | --------------- | ------------------------- |
| Baseline       | —             | —      | none                       | —               | Zero-shot CodeGen         |
| **v1**         | 50            | 10     | r=16, attn only            | MPS             | Smoke — proves PEFT works |
| **v2**         | 500           | 5      | r=16, attn only            | MPS             | Mid-scale                 |
| **v3**         | ~8,040        | 5*     | r=16, attn only            | MPS             | Full TEND scale           |
| **v4 (FINAL)** | ~8,040        | 5      | **r=32, α=64, attn + FFN** | **Kaggle CUDA** | Best results              |


v3 text2sql best checkpoint at epoch 2; sql2nosql/nosql2doc completed 5 epochs.

**Why v4 won**

- Same full data as v3
- Wider LoRA capacity: `r` 16→**32**, `α` 32→**64**
- Target modules expanded: `qkv_proj`, `out_proj` **+** `fc_in`**,** `fc_out` (feed-forward)
- Adapter size ~~7.5 MB → **~~40 MB** per task (still tiny vs full fine-tune)
- Trained in one Kaggle session ~**7h 34m**



### v4 training hyperparameters (actual)


| Setting                    | Value                               |
| -------------------------- | ----------------------------------- |
| Learning rate              | `2e-4`, cosine, warmup 0.05         |
| Weight decay               | 0.01                                |
| Epochs                     | 5                                   |
| Max length                 | 2048 (prompt ~1792 + target 256)    |
| Per-device batch (Kaggle)  | **2**                               |
| Grad accumulation (Kaggle) | **8**                               |
| Effective batch            | **16**                              |
| Precision                  | fp32                                |
| Seed                       | 42                                  |
| Notebook                   | `notebooks/kaggle_train_lora.ipynb` |


```yaml
lora:
  r: 32
  lora_alpha: 64
  lora_dropout: 0.05
  bias: none
  target_modules: [qkv_proj, out_proj, fc_in, fc_out]
```



## 4.3 Evaluation protocol


| Item                          | Detail                                                                                                                     |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Benchmark                     | `spider_gold_validation` — **50 frozen examples** per task                                                                 |
| Why frozen                    | Fair before/after across baseline → v4; fast; reproducible                                                                 |
| Exec accuracy                 | PostgreSQL (and Mongo for sql2nosql) result-set comparison enabled for reported v4 numbers                                 |
| Judge (CodeGen **eval** only) | `qwen3:8b` semantic scores for **documentation** (optional SQL semantics) — **not** used inside TEND to pick Mongo queries |
| Independence                  | Gold inputs per task — no prediction chaining                                                                              |


**Metrics suite**

Exact Match · Execution Accuracy · Structural similarity · Syntax validity · BLEU · ROUGE-L · BERTScore / embedding similarity · CodeBLEU · Judge score / correct rate

## 4.4 Headline results — LoRA v4 (USE THESE ON THE SLIDE)



### Progression (key metrics)


| Version     | Text2SQL exec | SQL2NoSQL exec | Doc judge (0–10) |
| ----------- | ------------- | -------------- | ---------------- |
| Baseline    | 12%           | 22%            | 0.1              |
| LoRA v1     | 20%           | 4%             | 1.5              |
| LoRA v2     | 34%           | 32%            | 3.1              |
| LoRA v3     | 54%           | 74%            | 6.4              |
| **LoRA v4** | **60%**       | **88%**        | **7.8**          |




### Text2SQL


| Metric                | Baseline | v3    | **v4**    | v4 vs base      |
| --------------------- | -------- | ----- | --------- | --------------- |
| Execution accuracy    | 12%      | 54%   | **60%**   | **+48 pp** (5×) |
| Exact match           | 0%       | 38%   | **40%**   | +40 pp          |
| Structural similarity | 0.700    | 0.910 | **0.916** | +0.216          |




### SQL2NoSQL (largest gains)


| Metric                | Baseline | v3    | **v4**    | v4 vs base      |
| --------------------- | -------- | ----- | --------- | --------------- |
| Execution accuracy    | 22%      | 74%   | **88%**   | **+66 pp** (4×) |
| Exact match           | 4%       | 58%   | **80%**   | +76 pp          |
| Structural similarity | 0.163    | 0.926 | **0.983** | +0.820          |




### Documentation


| Metric               | Baseline | v3    | **v4**    | v4 vs base                     |
| -------------------- | -------- | ----- | --------- | ------------------------------ |
| Judge score (0–10)   | 0.1      | 6.4   | **7.8**   | +7.7                           |
| Embedding similarity | 0.714    | 0.957 | **0.960** | +0.246                         |
| Exact match          | 0%       | 2%    | **2%**    | (semantic quality >> verbatim) |




### One chart suggestion

Bar chart: Execution accuracy by version for Text2SQL and SQL2NoSQL (Baseline → v4).  
Second chart: Documentation judge 0.1 → 7.8.

## 4.5 Key findings (talking points)

1. **Monotonic improvement** baseline → v4 on nearly every metric
2. **Data scale matters** (v1→v3); **LoRA capacity matters** at full scale (v3→v4)
3. **SQL2NoSQL** is the standout: 88% exec, 80% exact match, 0.98 structural similarity
4. **Documentation** improves semantically (judge 7.8) even when exact match stays low — expected for free-form text
5. **PEFT efficiency:** ~40 MB adapters vs hundreds of MB / full model copy; swappable per task
6. **v5** exists as a regularization ablation on text2sql only — final product remains **v4** for all three tasks



## 4.6 Limitations (honest — judges trust this)

- Gold validation set is **50** examples (speed/reproducibility); full TEND test (~1.6k) is available via `--full-split`
- Documentation **exact match** remains low (2%) — judge/embeddings are the right lens
- 350M model still below frontier LLMs on hard Spider/BIRD queries
- Schema must be supplied in the prompt (MVP) — IDE extension would automate retrieval
- Cloud Run cold starts + model load latency for first request



## 4.7 Reproducibility claims

- Seeds fixed (`random` / `numpy` / `torch` = 42)
- Prompt parity unit tests
- Frozen gold JSONL in repo
- Checkpoints + `run_metadata.json` + published HF adapters
- Version tracker documents every run



## Speaker notes (Slide 4)

> “We iterated five LoRA versions. Smoke runs proved the pipeline; full TEND training with attention-only LoRA got us to v3. **v4 doubled rank and alpha and adapted the feed-forward layers**, trained on Kaggle CUDA in about seven and a half hours. On the frozen 50-example gold set with execution checking, text2sql execution went from 12% to **60%**, sql2nosql from 22% to **88%**, and documentation judge from 0.1 to **7.8**. That is our final system.”

---



# SLIDE 5 — Deployments: Cloud Run, Hugging Face, Desktop Tool



## 5.1 Overview diagram

```text
┌──────────────────┐     publish      ┌─────────────────────────────────────┐
│ LoRA v4 adapters │ ───────────────► │ Hugging Face Hub (care2achieve)     │
│ (trained weights)│                  │ • codegen-350M-text2sql-lora        │
└────────┬─────────┘                  │ • codegen-350M-sql2nosql-lora       │
         │                            │ • codegen-350M-nosql2doc-lora       │
         │                            │ Dataset: care2achieve/tend          │
         │                            └─────────────────┬───────────────────┘
         │                                              │ pull weights @ start
         ▼                                              ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ Google Cloud Run — Multi-Adapter API Gateway                               │
│ OpenAI-compatible: /health, /v1/models, /v1/chat/completions               │
│ Intent routing → adapter hot-swap → CodeGen-350M + LoRA v4                 │
└───────────────┬─────────────────────────────┬──────────────────────────────┘
                │                             │
                ▼                             ▼
        Cursor / VS Code              Desktop AI SQL Assistant
        OpenAI-compatible /v1       generate → validate → execute on PG
```



## 5.2 Hugging Face artifacts



### Model adapters (weights)


| Task      | Hub repo                                                                                                                           |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| text2sql  | [https://huggingface.co/care2achieve/codegen-350M-text2sql-lora](https://huggingface.co/care2achieve/codegen-350M-text2sql-lora)   |
| sql2nosql | [https://huggingface.co/care2achieve/codegen-350M-sql2nosql-lora](https://huggingface.co/care2achieve/codegen-350M-sql2nosql-lora) |
| nosql2doc | [https://huggingface.co/care2achieve/codegen-350M-nosql2doc-lora](https://huggingface.co/care2achieve/codegen-350M-nosql2doc-lora) |


Publish command (from repo):

```bash
PYTHONPATH=hf-deploy python hf-deploy/publish/push_adapters.py --version v4
```

`hf-deploy/manifest.yaml` currently sets `checkpoint_version: v4`.

### Dataset


| Artifact | URL                                                                                                    |
| -------- | ------------------------------------------------------------------------------------------------------ |
| TEND     | [https://huggingface.co/datasets/care2achieve/tend](https://huggingface.co/datasets/care2achieve/tend) |




### Optional HF Space


| Item     | Value                                                                          |
| -------- | ------------------------------------------------------------------------------ |
| Space id | `care2achieve/codegen-multi-adapter`                                           |
| Note     | Docker Spaces may require HF PRO; **Cloud Run is the recommended hosted path** |




## 5.3 Google Cloud Run


| Item             | Detail                                                      |
| ---------------- | ----------------------------------------------------------- |
| What runs        | `hf-deploy` FastAPI multi-adapter gateway                   |
| Build            | Cloud Build → Artifact Registry → Cloud Run                 |
| Region (default) | `asia-south2` (Hyderabad)                                   |
| HTTPS            | Automatic `https://*.run.app`                               |
| Port             | 8080 in container                                           |
| Adapters         | Loaded from Hub at startup (`adapter_source: hub` in cloud) |
| Cursor base URL  | `https://<service>.run.app/v1`                              |
| Model name       | `codegen-multi-adapter`                                     |


**Why Cloud Run (judge-friendly)**


| vs VM    | Benefit                                 |
| -------- | --------------------------------------- |
| HTTPS    | Built-in — no domain/Caddy              |
| Ops      | No SSH / systemd babysitting            |
| Cost     | Scale to zero; free tier friendly       |
| Redeploy | `./deploy.sh` rebuilds + rolls revision |


Deploy (local ops — do not put secrets/URLs in slides unless live demo):

```bash
cd hf-deploy/infra/cloudrun
source env.sh && ./deploy.sh
curl -sS "${CLOUD_RUN_SERVICE_URL}/health"
```

**API behavior**


| User intent examples            | Adapter                       |
| ------------------------------- | ----------------------------- |
| “write / generate a SQL query…” | text2sql                      |
| “convert SQL to Mongo / NoSQL…” | sql2nosql                     |
| “generate documentation…”       | nosql2doc                     |
| Ambiguous                       | Clarification (no generation) |


Response includes `codegen_routing` (`intent`, `confidence`, `method`: rules vs embeddings).

## 5.4 Desktop tool — AI SQL Assistant


| Item          | Detail                                                                                                          |
| ------------- | --------------------------------------------------------------------------------------------------------------- |
| Path          | `tool/`                                                                                                         |
| UI            | CustomTkinter native desktop (no browser)                                                                       |
| Inference     | Calls hf-deploy FastAPI (local or Cloud Run) — **does not** load LoRA in-process                                |
| Database      | PostgreSQL **dvd** (Pagila rental schema) via `tool/scripts/setup_dvd_database.sh`                              |
| Flow          | NL question → schema/table selection (embeddings) → prompt → SQL → **validate SELECT** → execute → results grid |
| Extensibility | Stub tabs for SQL→NoSQL and Documentation                                                                       |
| Demo queries  | Listed below (single-table + join examples)                                                                     |


**Activity log stages (demo narrative)**

`schema_loaded` → `tables_selected` → `prompt_built` → `sql_generated` → `validation_passed` → `rows_retrieved`

**Architecture**

```text
Desktop AI SQL Assistant
├── Application shell & launcher
├── User interface layer (CustomTkinter)
├── Core services (settings, DB connection, schema, inference client, validation)
├── Text-to-SQL pipeline orchestrator
└── Task tabs (Text-to-SQL · SQL→NoSQL stub · Documentation stub)
        │
        └── shares prompt format & SQL validation with research Text2SQL module
```

Uses the same prompt-building and syntax-validation logic as the research Text2SQL pipeline.

### Demo query bank (DVD / Pagila schema)

**Single-table examples**

- List all first_name, last_name, and email from the customer table.
- Find all customers where active = 1.
- Show the title and release_year of all films.
- List all films where rating = 'PG'.
- Find films where rental_rate is greater than 2.99.
- Show all films where length is greater than 120.
- List all categories with their category_id and name.
- Show all actors with first_name and last_name.
- List all payments where amount is greater than 5.00.
- Show all rentals where return_date is NULL.

**Two-table join examples**

- Find the films acted by first_name = Penelope
- Show the title and language.name for each film. (Join: film → language)
- List the first_name, last_name, and amount for each payment. (Join: payment → customer)
- Show the title and store_id for every inventory record. (Join: inventory → film)
- List the title and category_id for every film category. (Join: film_category → film)
- Show the first_name, last_name, and film_id for every actor. (Join: film_actor → actor)
- List the address and city for every address. (Join: address → city)
- Show the city and country for every city. (Join: city → country)
- List the rental_date, return_date, first_name, and last_name of the customer for each rental. (Join: rental → customer)
- Show the payment_date, amount, and first_name of the staff who processed each payment. (Join: payment → staff)
- List the store_id and manager_staff_id along with the manager first_name and last_name. (Join: store → staff)



## 5.5 Slide layout suggestion

Three columns:

1. **Hugging Face** — 3 adapter cards + TEND dataset link
2. **Cloud Run** — OpenAI `/v1` gateway diagram
3. **Tool** — screenshot of Text-to-SQL UI + “generate → execute”



## Speaker notes (Slide 5)

> “Research adapters are not enough. We published three LoRA repos and the TEND dataset on Hugging Face. The serving layer is an OpenAI-compatible FastAPI app on **Google Cloud Run** with intent-based adapter hot-swap — Cursor can use it as a custom model. The **desktop tool** is our product proof: it pulls schema, calls the same API, validates SQL, and runs it on PostgreSQL so users see real answer rows.”

---



# SLIDE 6 — Demo Video



## On-screen content

- Title: **Demo — AI SQL Assistant + Multi-Adapter API**
- Embedded or linked video (YouTube / Drive / local file) — **TODO: paste URL**
- Optional QR code to video or Cloud Run health endpoint
- 3–5 still frames as backup if video fails



## Recommended demo script (record this)



### Part A — Desktop tool (primary, ~90–120s)

1. Show Settings: active DB `dvd` on PostgreSQL; FastAPI URL (local or Cloud Run); Test Connection + Test API
2. Text-to-SQL tab — single-table question, e.g.
  - “List all first_name, last_name, and email from the customer table.”
3. Execute → walk activity log → show SQL → show result rows
4. Harder join, e.g.
  - “Show the title and language.name for each film.”
5. Optional: attempt a non-SELECT and show **validation block**



### Part B — API / Cursor path (~30–45s)

1. `curl` `/health` and a `/v1/chat/completions` text2sql request with schema in prompt
2. Or Cursor: base URL → model `codegen-multi-adapter` → same question
3. Point out `codegen_routing` in the response JSON



### Part C — Optional one-liner on adapters

- Show HF model card for `codegen-350M-text2sql-lora` (v4) — “same weights the API loads”



## Backup if live demo / video fails

Keep open:


| Asset            | Action                                              |
| ---------------- | --------------------------------------------------- |
| Tool             | Run desktop app with hf-deploy API running          |
| Sample questions | Use demo query bank in Slide 5 section above        |
| Metrics          | LoRA v4 numbers in Slide 4 and Reference Appendix F |
| Architecture     | Diagrams in Slide 2 and Reference Appendix C        |




## Speaker notes (Slide 6)

> Narrate over the video; do not repeat every UI click. Focus on: **schema selection → generated SQL → validation → real rows**. Close with: “This is the same API an IDE would call.”

---



# SLIDE 7 — Thank You & Questions



## On screen

**Thank you**

- Project title again  
- Team names (from Slide 1)  
- Key links (short list):


| Resource            | Link                                                                                                                               |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| TEND dataset        | [https://huggingface.co/datasets/care2achieve/tend](https://huggingface.co/datasets/care2achieve/tend)                             |
| text2sql adapter    | [https://huggingface.co/care2achieve/codegen-350M-text2sql-lora](https://huggingface.co/care2achieve/codegen-350M-text2sql-lora)   |
| sql2nosql adapter   | [https://huggingface.co/care2achieve/codegen-350M-sql2nosql-lora](https://huggingface.co/care2achieve/codegen-350M-sql2nosql-lora) |
| nosql2doc adapter   | [https://huggingface.co/care2achieve/codegen-350M-nosql2doc-lora](https://huggingface.co/care2achieve/codegen-350M-nosql2doc-lora) |
| CodeGen repo / tool | **TODO**                                                                                                                           |
| Demo video          | **TODO**                                                                                                                           |


**Questions?**

Optional footer: “Happy to discuss LoRA design, execution accuracy, or IDE integration.”

## Closing line

> “Small code LMs + PEFT + execution-validated data + a real serving path can deliver useful multi-dialect database assistance — without fine-tuning a giant model.”

---



# APPENDIX — Additional Slides to Impress Judges

> **How to use:** Keep slides **1–7** for the timed talk. Put **A1–A8** after slide 7 (or in a hidden appendix deck). Jump here when a judge asks about novelty, LoRA, ablations, execution accuracy, reproducibility, failures, roadmap, or training internals.  
> **Do not** narrate all appendix slides in the main talk — that burns time.



## Appendix map (when to open each)


| Slide  | Title                           | Open when a judge asks…                     |
| ------ | ------------------------------- | ------------------------------------------- |
| **A1** | Contributions & novelty         | “What’s new?” / “Is this just fine-tuning?” |
| **A2** | Why LoRA / PEFT                 | “Why not full fine-tune / GPT-4?”           |
| **A3** | Ablation v3 → v4 (+ beam)       | “How did you improve?” / “Any ablations?”   |
| **A4** | Execution accuracy              | “How do you know SQL is correct?”           |
| **A5** | Prompt parity & reproducibility | “Can we reproduce this?”                    |
| **A6** | Failures & limitations          | “What still breaks?”                        |
| **A7** | Future work                     | “What’s next?”                              |
| **A8** | Architecture deep-dive          | “Walk through training / serving internals” |


**Priority if you only prepare 3 appendix slides:** **A1 → A4 → A3**.

**Avoid in main deck (belongs only here):** full metric matrices, long code, Cloud Run secrets/URLs, claiming **v5** as final.

---



# SLIDE A1 — Contributions & Novelty



## Slide title (on screen)

**What We Built — Beyond “Fine-Tuning a Model”**

## Core message

Most student Text-to-SQL projects stop at a notebook + BLEU. We shipped a **dataset factory**, a **reproducible PEFT research pipeline**, a **production-shaped API**, and a **real execute loop**.

## On-screen contribution matrix


| #   | Contribution                                   | Artifact                           | Why it matters                                                                 |
| --- | ---------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------ |
| 1   | **Execution-validated multi-task dataset**     | TEND → HF `care2achieve/tend`      | Aligned NL ↔ SQL ↔ Mongo ↔ docs with **result-set proof**, not LLM-only labels |
| 2   | **Three-task LoRA system on one 350M base**    | Adapters v1→**v4**                 | Small model, multi-skill, swappable adapters (~40 MB each at v4)               |
| 3   | **Independent gold evaluation + exec metrics** | Frozen 50-row gold + PG/Mongo exec | Fair version comparison; correctness beyond string match                       |
| 4   | **OpenAI-compatible multi-adapter gateway**    | Cloud Run API service              | Cursor / any SDK can call it today                                             |
| 5   | **Published Hub artifacts**                    | 3× LoRA repos + dataset            | Reusable outside our laptop                                                    |
| 6   | **Product client**                             | Desktop AI SQL Assistant           | Schema select → generate → validate → **execute** on live PostgreSQL           |
| 7   | **IDE path designed**                          | Cursor now; VS Code extension spec | Local-first schema, stateless model                                            |




## Novelty angles (talking bullets)

1. **Deterministic-first dataset construction** — rule-based SQL→Mongo, then Python SQL→NoSQL tool, Ollama **only as query fallback**; Ollama for **documentation generation** (not as a query judge); then **execution filter**
2. **Multi-dialect stack** — not Text-to-SQL alone; SQL↔NoSQL + documentation in one row
3. **PEFT as product architecture** — one base, hot-swap adapters by intent (not three full models)
4. **Research ↔ deployment continuity** — same adapters evaluated in `results/` are what Cloud Run / HF load
5. **Safety in the tool** — SELECT-only validation before execution



## What is *not* claimed as novelty (honesty impresses)

- Inventing LoRA or Spider/BIRD  
- Beating frontier LLMs on full Spider leaderboard  
- A finished VS Code Marketplace extension (spec + Cursor path exist; extension is roadmap)



## Visual suggestion

Horizontal swimlane: **TEND → Train LoRA v4 → Eval → HF → Cloud Run → Tool / Cursor**

## Speaker notes (A1)

> “If you remember one thing: we didn’t only train adapters. We built the **data that makes training trustworthy**, measured with **execution**, published weights, served an **OpenAI-compatible API**, and proved usefulness with a tool that **runs SQL on a real database**.”

---



# SLIDE A2 — Why LoRA / PEFT (ML Literacy)



## Slide title (on screen)

**Why Parameter-Efficient Fine-Tuning (LoRA)?**

## Problem with full fine-tuning (on screen)


| Full fine-tuning                  | Cost for us                    |
| --------------------------------- | ------------------------------ |
| Update ~350M parameters × 3 tasks | 3 full model copies            |
| High VRAM / long train            | Hard on student / MPS hardware |
| Catastrophic forgetting risk      | Base code skills may degrade   |
| Deploy 3 large models             | Ops and storage pain           |




## LoRA idea (one diagram)

```text
Frozen CodeGen-350M weights
        │
        │  +  low-rank update  ΔW ≈ B × A   (rank r ≪ d)
        ▼
Task adapter (text2sql | sql2nosql | nosql2doc)
        │
        ▼
Same base + tiny adapter file on disk
```



## Comparison table (put on slide)


| Aspect           | Full fine-tune                      | **LoRA (our approach)**           |
| ---------------- | ----------------------------------- | --------------------------------- |
| Trainable params | ~100% of model                      | ~0.1–1% (adapters)                |
| Storage per task | Full checkpoint                     | **~7.5 MB (v1–v3) → ~40 MB (v4)** |
| Base model       | Copied / mutated                    | **One shared frozen base**        |
| Multi-task       | Separate models or messy multi-head | **Hot-swap** `set_adapter`        |
| Overfitting risk | Higher on small data                | Lower (base frozen)               |
| Deploy           | Heavy                               | Base once + 3 adapters            |




## Our LoRA configs (evolution)


| Version        | Rank `r` | Alpha  | Target modules                  | Adapter size |
| -------------- | -------- | ------ | ------------------------------- | ------------ |
| v1–v3          | 16       | 32     | `qkv_proj`, `out_proj`          | ~7.5 MB      |
| **v4 (final)** | **32**   | **64** | **attn +** `fc_in`**/**`fc_out` | **~40 MB**   |


Still tiny vs storing three fine-tuned 350M models.

## Training mechanics (short)

- **TRL** `SFTTrainer`, causal LM  
- **Completion-only loss** — prompt tokens masked (`-100`); only SQL / Mongo / docs tokens train the loss  
- Prompt prefixed with `Task: text2sql` (etc.) so one base serves three skills  
- Device path: CUDA (Kaggle v4) > MPS > DirectML > CPU



## Why not “just use GPT-4 / cloud LLM”?


| Criterion         | Large API LLM | Our small LoRA stack                    |
| ----------------- | ------------- | --------------------------------------- |
| Cost at scale     | Per-token $   | Fixed infra / free tier friendly        |
| Data control      | Leaves org    | Local / your Cloud Run                  |
| Specialization    | General       | **Execution-validated DB dialect data** |
| Offline / air-gap | Hard          | Possible with local uvicorn             |
| Capstone learning | Black box     | Full train → eval → deploy ownership    |




## Speaker notes (A2)

> “LoRA lets us specialize a 350M code model for three database tasks without three full fine-tunes. Adapters stay small enough to publish on Hugging Face and hot-swap in one FastAPI process. That’s how research PEFT becomes a deployable multi-skill API.”

---



# SLIDE A3 — Ablation Story: v3 → v4 (+ Beam Decoding)



## Slide title (on screen)

**Scientific Iteration — From v3 to Final v4**

## Message

We did not pick hyperparameters once. **Scale first (v1→v3), then capacity (v3→v4).** Optional decoding ablation shows task-dependent beam vs greedy.

## Controlled comparison: what changed v3 → v4


| Setting           | LoRA v3                  | **LoRA v4 (final)**                             |
| ----------------- | ------------------------ | ----------------------------------------------- |
| Train samples     | ~8,040                   | **same**                                        |
| Epochs            | 5 (text2sql best @ ep 2) | **5 (all tasks complete)**                      |
| LoRA rank / alpha | 16 / 32                  | **32 / 64**                                     |
| Target modules    | attention only           | **attention + FFN (**`fc_in`**,** `fc_out`**)** |
| Effective batch   | 32                       | **16** (Kaggle GPU memory)                      |
| Device            | Local MPS                | **Kaggle CUDA (~7.5 h)**                        |


**Hypothesis:** Wider adapters + FFN targets improve structural generation even if batch size halves.

## Result of the ablation (headline)


| Task          | Metric        | v3  | **v4**  | Δ          |
| ------------- | ------------- | --- | ------- | ---------- |
| Text2SQL      | Exec accuracy | 54% | **60%** | +6 pp      |
| SQL2NoSQL     | Exec accuracy | 74% | **88%** | **+14 pp** |
| SQL2NoSQL     | Exact match   | 58% | **80%** | +22 pp     |
| Documentation | Judge (0–10)  | 6.4 | **7.8** | +1.3       |


**Takeaway:** Same data, better LoRA capacity → consistent gains — especially SQL2NoSQL.

## Full progression (context)


| Version                | Text2SQL exec | SQL2NoSQL exec | Doc judge | Change         |
| ---------------------- | ------------- | -------------- | --------- | -------------- |
| Baseline               | 12%           | 22%            | 0.1       | —              |
| v1 (50×10)             | 20%           | 4%             | 1.5       | pipeline works |
| v2 (500×5)             | 34%           | 32%            | 3.1       | more data      |
| v3 (~8k, r=16)         | 54%           | 74%            | 6.4       | full scale     |
| **v4 (~8k, r=32+FFN)** | **60%**       | **88%**        | **7.8**   | **capacity**   |




## Secondary ablation: greedy vs beam (same v4 weights)


| Task          | Metric      | Greedy  | Beam (num_beams=4) | Winner     |
| ------------- | ----------- | ------- | ------------------ | ---------- |
| Text2SQL      | Exec        | 60%     | **64%**            | Beam       |
| Text2SQL      | Exact match | 40%     | **44%**            | Beam       |
| SQL2NoSQL     | Exec        | **88%** | 82%                | **Greedy** |
| SQL2NoSQL     | Exact match | **80%** | 66%                | **Greedy** |
| Documentation | Judge       | 7.8     | **8.5**            | Beam       |


**Talking point:** Decoding is task-dependent. Product API can default greedy for Mongo translation and beam for Text2SQL/docs — or expose a generation flag.

## Note on v5 (if asked)

- v5 = **text2sql-only** regularization ablation (lower LR, higher dropout/weight decay)  
- **Not** the final multi-task release — final remains **v4** for all three adapters



## Speaker notes (A3)

> “v3 proved full-data training works. v4 asked: does more LoRA capacity help? Yes — especially on SQL→Mongo execution, plus six points on Text2SQL. Separately, beam search helps Text2SQL and docs but can hurt sql2nosql — so we treat decoding as a per-task knob, not a universal upgrade.”

---



# SLIDE A4 — Execution Accuracy Story



## Slide title (on screen)

**Execution Accuracy — How We Know Queries Are Correct**

## Why string metrics are not enough


| Metric          | What it measures        | Blind spot                                          |
| --------------- | ----------------------- | --------------------------------------------------- |
| Exact match     | String equality         | Semantically equal SQL with different wording fails |
| BLEU / CodeBLEU | N-gram / syntax overlap | High overlap, **wrong results** possible            |
| LLM judge       | Semantic opinion        | Can disagree with reality; non-deterministic        |


**Execution accuracy:** run the query; compare **result sets**.

## Where execution appears in our stack

```text
┌─────────────────────────────────────────────────────────────┐
│  TEND dataset factory                                       │
│  1) Rules → 2) SQL→NoSQL converter → 3) LLM fallback        │
│  Fail all validations → failed to convert                   │
│  LLM documentation generation (not a query judge)           │
│  Execute gold SQL on PostgreSQL + Mongo on MongoDB          │
│  Keep row only if normalized results MATCH → gold / HF      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Model evaluation (LoRA v4)                                 │
│  Predicted SQL / Mongo vs gold on live databases            │
│  → execution accuracy % on frozen 50-example benchmark      │
│  (Semantic judge scores docs — separate from TEND build)    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Desktop AI SQL Assistant                                   │
│  Validate SELECT-only → execute on PostgreSQL → show rows   │
└─────────────────────────────────────────────────────────────┘
```



## TEND gold filter (strict)

1. Execute `sql_query` on **PostgreSQL**
2. Execute `nosql_query` on **MongoDB**
3. Normalize and compare result sets
4. `execution_accuracy=true` only on match → **gold**
5. No LLM-judge gate at gold stage

**Export-scale yield:** ~**9,075 / 20,655 ≈ 43.9%** bronze → gold (quality over quantity).

## Capstone reported exec numbers (v4 greedy)


| Task      | Baseline | **LoRA v4** |
| --------- | -------- | ----------- |
| Text2SQL  | 12%      | **60%**     |
| SQL2NoSQL | 22%      | **88%**     |




## Database environment (impress with engineering)


| Component                                          | Role                                                          |
| -------------------------------------------------- | ------------------------------------------------------------- |
| Spider / BIRD SQLite sources                       | Original benchmarks                                           |
| Docker PostgreSQL 16 + MongoDB 8                   | Load + parity validation                                      |
| `run_execution_accuracy` / `export_executed_jsonl` | TEND CLI for live checks                                      |
| Gold validation subset                             | Small import (`concert_singer`, `pets_1`) for 50-sample demos |




## Judge vs execution (how we talk about both)


| Layer                                          | Where                                                        | Use                                                                       |
| ---------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------- |
| **Rules → Python converter → Ollama fallback** | TEND query build                                             | Produce Mongo query; **no LLM judge** between paths                       |
| **Ollama codegen**                             | TEND docs                                                    | **Documentation generation only** (after a valid query exists)            |
| **Execution accuracy**                         | TEND gold + CodeGen eval                                     | Ground truth for SQL/Mongo correctness (**primary claim**)                |
| **Ollama semantic judge**                      | CodeGen **evaluation** of LoRA docs (and optional semantics) | Scoring trained-model outputs — **not** part of TEND query selection      |
| **Future**                                     | —                                                            | Prefer execution everywhere for queries; keep LLM only for free-text docs |




## Speaker notes (A4)

> “Our differentiator is execution — and for Mongo conversion we stay deterministic-first. Rules, then the Python SQL→NoSQL tool, then Ollama only if both fail. We never use an LLM judge to pick a ‘best’ query. Ollama writes documentation. When we say LoRA v4 reaches 60% and 88% execution accuracy, we mean the predicted queries were run against databases — not that they merely looked like the gold string.”

---



# SLIDE A5 — Prompt Parity & Reproducibility



## Slide title (on screen)

**Reproducibility — Training Matches Inference**

## Why this slide exists

Judges (and paper reviewers) distrust gains that come from **prompt mismatch** or **cherry-picked eval sets**. We engineered against both.

## Prompt parity


| Risk                        | Our control                                                                     |
| --------------------------- | ------------------------------------------------------------------------------- |
| Train prompt ≠ serve prompt | Shared builders: `build_training_prompt()` aligned with runtime `PromptBuilder` |
| Silent format drift         | Unit test `tests/training/test_prompt_parity.py`                                |
| Task confusion              | Explicit `Task: text2sql                                                        |


**Talking line:** “If train and serve prompts diverge, LoRA gains are fake. We unit-test parity.”

## Frozen benchmark


| Property               | Detail                                                        |
| ---------------------- | ------------------------------------------------------------- |
| File                   | `data/spider_gold_validation.jsonl`                           |
| Size                   | **50** examples (version-controlled)                          |
| Use                    | Baseline + every LoRA version comparison                      |
| Why not full test only | Speed, fairness, identical examples across months of runs     |
| Escape hatch           | `--full-split` on ~1,625 TEND test rows for extended analysis |




## Seeds & config


| Control                            | Value / location                         |
| ---------------------------------- | ---------------------------------------- |
| `random` / `numpy` / `torch` seeds | **42** in `configs/default.yaml`         |
| Hyperparameters                    | YAML + run `run_metadata.json`           |
| Checkpoint layout                  | `models/checkpoints/v4/<task>/`          |
| Experiment log                     | MLflow optional; training summaries JSON |




## Software tests (quality ≠ model quality)


| Test / script             | Checks                                     |
| ------------------------- | ------------------------------------------ |
| `test_prompt_parity.py`   | Train/inference string identity            |
| `test_overfit_smoke.py`   | Tiny train writes adapter artifacts        |
| `test_adapter_load.py`    | Adapter loads and generates                |
| `verify_lora_adapters.py` | Required files present                     |
| `inspect_lora_modules.py` | Target modules exist on CodeGen            |
| `hf-deploy/tests`         | API classifier / routing (no GPU required) |
| `tool/tests`              | Desktop pipeline pieces                    |




## Artifact trail (re-run story)

```text
TEND dataset (Hugging Face)
  → LoRA training (local GPU or cloud notebook)
  → LoRA adapter artifacts saved
  → Publish adapters to Hugging Face Hub
  → Cloud Run service pulls Hub weights at startup
  → Benchmark evaluation → metrics & per-task reports
```



## Speaker notes (A5)

> “Reproducibility is part of the contribution. Same gold file for every version, fixed seeds, prompt-parity tests, and published adapters so someone else can load v4 without our training laptop.”

---



# SLIDE A6 — Failure Cases & Limitations



## Slide title (on screen)

**What Still Fails — Limitations & Example Failure Modes**

## Why show failures

Mature teams show **error analysis**. It builds trust and sets up future work.

## System limitations (on screen)


| Limitation                   | Impact                                         | Mitigation / next step                  |
| ---------------------------- | ---------------------------------------------- | --------------------------------------- |
| 350M parameter ceiling       | Hard Spider/BIRD queries still miss            | Larger code LM base; keep LoRA recipe   |
| 50-example headline bench    | Wide confidence intervals                      | Also report `--full-split` in follow-up |
| Schema-in-prompt MVP         | Server doesn’t see the repo                    | Tool / VS Code local schema retrieval   |
| Doc exact match ~2%          | Verbatim docs rare                             | Judge + embeddings; accept paraphrase   |
| Cold start on Cloud Run      | First request slow                             | Min instances / warmup / local cache    |
| Beam vs greedy tradeoff      | One decoding ≠ best for all tasks              | Per-task decoding policy                |
| Multi-step agent not shipped | NL→SQL→Mongo→docs chaining can compound errors | Execute-check between steps (future)    |




## Failure mode examples (prepare 1–2 live)

Use anonymized rows from `results/.../text2sql_details.csv` or a rehearsed example:

### Type A — Plausible but wrong SQL (exec fails)


|               | Example pattern                                                          |
| ------------- | ------------------------------------------------------------------------ |
| Symptom       | Valid syntax, wrong join / filter / aggregation                          |
| Metric signal | Syntax validity high, **execution accuracy** fails                       |
| Fix direction | More hard-join gold data; execution-in-the-loop training; schema linking |




### Type B — Mongo structural near-miss


|               | Example pattern                                        |
| ------------- | ------------------------------------------------------ |
| Symptom       | `$lookup` pipeline close to gold, different field path |
| Metric signal | High structural similarity, exec may still fail        |
| Fix direction | Richer rule hints in TEND; more join-heavy gold        |




### Type C — Documentation paraphrase


|               | Example pattern                                            |
| ------------- | ---------------------------------------------------------- |
| Symptom       | Correct meaning, different wording → exact match 0         |
| Metric signal | Judge / embedding high, EM low                             |
| Fix direction | Don’t optimize EM for docs; keep judge + human spot checks |




### Type D — Tool / product


|               | Example pattern                                         |
| ------------- | ------------------------------------------------------- |
| Symptom       | Wrong tables selected by embedding top-K → bad SQL      |
| Fix direction | Raise top-K, better embeddings, user table picker in UI |




## What we refuse to hide

- v1 sql2nosql exec dipped vs baseline at smoke scale — scale + v4 fixed the story  
- In **TEND**, we do **not** use an LLM judge to choose Mongo queries — conversion cascade + execution decide  
- In **CodeGen eval**, an Ollama semantic judge scores **documentation** (and optional semantics); query correctness claims rest on **execution**



## Speaker notes (A6)

> “v4 is strong, not perfect. Many remaining Text2SQL errors are semantically tricky joins — the SQL looks fine but the result set is wrong. That’s exactly why we measure execution. Documentation we score semantically because exact string match is the wrong objective. And in TEND itself, Ollama never judges which Mongo query wins — it only fills docs or acts as a last-resort generator.”

---



# SLIDE A7 — Future Work



## Slide title (on screen)

**Roadmap — From Capstone to Product**

## Near-term (high confidence)


| Item                      | Detail                                                                         |
| ------------------------- | ------------------------------------------------------------------------------ |
| **VS Code extension**     | Local schema index + Chat UI; call same Cloud Run `/v1` (spec already written) |
| **Per-task decoding**     | Beam for text2sql/docs; greedy for sql2nosql (from A3 ablation)                |
| **Full-split dashboards** | Publish metrics on full TEND test (~1.6k), not only gold-50                    |
| **Publish v4 Hub cards**  | Ensure Hub model cards / `manifest.yaml` match final v4 everywhere             |
| **Tool tabs**             | Finish SQL→NoSQL and Documentation tabs (stubs today)                          |




## Mid-term


| Item                               | Detail                                                           |
| ---------------------------------- | ---------------------------------------------------------------- |
| **Execute-checked agent**          | Chain NL→SQL→Mongo→docs; **run DB check between steps**          |
| **Richer schema linking**          | Column-level retrieval, multi-DB workspace support               |
| **Training on stricter gold only** | Retrain LoRA exclusively on highest-yield execution gold subsets |
| **Larger base LM**                 | e.g. 1–2B code model + same LoRA recipe; compare cost/quality    |
| **CI eval**                        | On adapter push: smoke gold-50 exec gate before Cloud Run deploy |




## Longer-term / research


| Item                                        | Detail                                |
| ------------------------------------------- | ------------------------------------- |
| Preference / DPO on exec failures           | Learn from wrong-but-fluent SQL       |
| Cross-dialect benchmarks beyond Spider/BIRD | Production schemas                    |
| On-device / edge adapters                   | MPS/DirectML product path for privacy |
| Multi-user auth on Cloud Run                | API keys, quotas                      |




## How this connects to the demo today

```text
Today:     Desktop AI SQL Assistant + Cursor base URL + HF adapters
Next:      VS Code extension (same API)
Then:      Agent with execution gates between tasks
```



## Speaker notes (A7)

> “The serving contract is already IDE-ready. Next we push schema intelligence into the editor, tune decoding per task, and only then chain tasks — with execution checks so errors don’t cascade.”

---



# SLIDE A8 — Architecture Deep-Dive (Training & Serving)



## Slide title (on screen)

**Deep Dive — Training Loop & Serving Path**

> Use only if a judge wants internals. Prefer diagrams over text walls.



## A. Training flow

```text
LoRA training orchestrator (local or cloud GPU)
        │
        ▼
Load runtime config → select device (CUDA / MPS / CPU)
        │
        ▼
For each task: text2sql → sql2nosql → nosql2doc
        │
        ├─ Load TEND train split (~10.7k → ~8k after filters)
        ├─ Filter required fields + 2048 token budget
        ├─ Build training prompt + completion target
        ├─ Load frozen base model weights
        ├─ Attach LoRA adapters (v4: r=32, attention + feed-forward)
        ├─ Supervised fine-tuning, completion-only loss, 5 epochs
        ├─ Save best adapter per task
        └─ Record training metadata (loss, counts, hyperparams)
        │
        ▼
Verify adapters → training summary report
```



## B. Evaluation flow

```text
Benchmark evaluation (LoRA v4)
        │
        ├─ Load frozen gold benchmark (50 examples)
        ├─ Per task: load matching LoRA adapter
        ├─ Generate predictions (greedy or beam decoding)
        ├─ Score: exact match, execution accuracy, structural, BLEU, CodeBLEU, judge…
        └─ Export metrics summary + per-example detail reports
```



## C. Serving flow (Cloud Run / local)

```text
POST /v1/chat/completions
        │
        ▼
Intent classifier (rules → embeddings → clarify)
        │
        ▼
Prompt builder adds Task: <intent>
        │
        ▼
PEFT set_adapter(intent)
        │
        ▼
CodeGen-350M + LoRA v4 generate
        │
        ▼
JSON response + codegen_routing {intent, confidence, method}
```



## D. Desktop tool flow

```text
User question
  → load PostgreSQL schema / embedding-based top-K table selection
  → build Text-to-SQL prompt (schema injected)
  → multi-adapter API generate
  → SELECT-only SQL validation
  → execute on sample DVD database
  → results grid + activity log
```



## Module map (if needed on a second deep-dive slide)


| Component                  | Responsibility                               |
| -------------------------- | -------------------------------------------- |
| Dataset loader             | TEND load, gold benchmark                    |
| LoRA training pipeline     | SFT dataset, trainer, prompt parity          |
| Text2SQL · SQL2NoSQL · Doc | Task-specific prompt, generate, validate     |
| Evaluation engine          | Metrics, semantic judge, experiment tracking |
| Multi-adapter API gateway  | Intent classifier, adapter router, Cloud Run |
| Desktop AI SQL Assistant   | Schema retrieval, safe execute, desktop UI   |
| TEND dataset factory       | Execution-validated dataset generation       |




## Speaker notes (A8)

> “Training freezes the base and writes three adapters. Eval never chains predictions. Serving classifies intent and hot-swaps adapters in one process. The tool is just a careful client that adds schema and execution.”

---



# Anticipated Q&A (prepare verbally)



### Why LoRA instead of full fine-tuning?

Trains ~0.1–1% of parameters; adapters ~40 MB (v4); base shared; low overfitting risk; swap adapters per task.

### Why not chain Text2SQL → SQL2NoSQL → Docs in evaluation?

Error compounding. Independent gold inputs isolate each skill. Chaining is a **product** mode for future agents, not for fair benchmarking.

### Why only 50 gold validation examples?

Reproducible, fast, fair across versions. Full TEND test (~1,625) available; training used ~8k+ rows.

### How does TEND convert SQL → MongoDB?

**Cascade, first success wins:** (1) rule-based converters → (2) SQL→NoSQL Python tool (`sql-mongo-converter`) → (3) Ollama codegen **only if both failed**. If none pass validation → **failed to convert**. Ollama generates **documentation**; it is **not** used as a judge between query candidates.

### How is execution accuracy computed?

Run predicted (or gold) SQL on PostgreSQL / Mongo on MongoDB; compare normalized result sets — same idea as TEND gold filtering.

### Why is documentation exact match low?

Free-form language; semantic judge + embeddings measure usefulness better than string equality.

### How do you plug into Cursor today?

Point Cursor’s OpenAI-compatible base URL at Cloud Run or `localhost:8000/v1`, model `codegen-multi-adapter`.

### Why build a separate tool instead of only Cursor?

Cursor proves API compatibility; the tool proves **schema retrieval + safe execute + UX** without requiring every judge to configure Cursor.

### What is the relationship between TEND and CodeGen repos?

TEND **builds and validates** the multi-task dataset (and DB env). CodeGen **trains, evaluates, deploys** LoRA adapters and the product clients.

### What would you do next with more time?

Ship VS Code extension (local index + remote inference); full-split eval dashboards; optional larger base model; agentic multi-step (NL→SQL→Mongo→docs) with execution checks between steps.

---



# Slide-building checklist

- [ ] Fill **TODO** team / date / video / repo links on slides 1, 6, 7  
- [ ] Use **v4 numbers only** as “final results” (mention v1–v3 as progression)  
- [ ] Export 1 architecture diagram + 1 results chart as high-res images  
- [ ] Record demo video with backup stills  
- [ ] Build **appendix slides A1–A8** (at least A1, A3, A4 if short on time)  
- [ ] Pull 1–2 real failure rows from evaluation detail CSVs into A6  
- [ ] Practice timing: Slides 1–7 only; appendix only on Q&A  
- [ ] Dry-run Q&A with “why LoRA?”, “why 50 examples?”, “how is gold filtered?”, “what’s novel?”

---



# One-page cheat sheet (print for yourself during talk)


| Claim               | Number / fact                                     |
| ------------------- | ------------------------------------------------- |
| Final adapters      | **LoRA v4**                                       |
| Base                | codegen-350M-multi                                |
| Train scale         | ~8,040 rows × 5 epochs (TEND)                     |
| LoRA v4             | r=32, α=64, qkv+out+fc_in+fc_out                  |
| Text2SQL exec       | **60%** greedy / **64%** beam (base 12%)          |
| SQL2NoSQL exec      | **88%** greedy (base 22%; beam 82%)               |
| Doc judge           | **7.8** greedy / **8.5** beam (base 0.1)          |
| Dataset             | TEND gold / HF care2achieve/tend                  |
| Gold yield (export) | **9,075 / 20,655 ≈ 44%**                          |
| Serve               | Cloud Run OpenAI `/v1`                            |
| HF                  | 3× `codegen-350M-*-lora`                          |
| Product             | Desktop Text-to-SQL tool → live PostgreSQL        |
| Appendix priority   | **A1 contributions → A4 execution → A3 ablation** |


---

---



# REFERENCE APPENDIX — Self-Contained Project Documentation

> Everything below duplicates project documentation so this file can be shared standalone. External links only.

---



## Reference Appendix B — Executive Summary



### Project Title

**CodeGen Fine-Tuning with PEFT & LoRA**

Fine-tuning `Salesforce/codegen-350M-multi` with Parameter-Efficient Fine-Tuning (PEFT) via LoRA on three database query tasks: Text→SQL, SQL→MongoDB, and NoSQL→Documentation.

### Problem Statement

Modern database systems span relational (SQL) and document (NoSQL) stores. Developers and analysts need to:

1. Translate natural-language questions into SQL
2. Convert SQL queries to MongoDB shell syntax
3. Generate human-readable documentation for NoSQL queries

Large language models can perform these tasks, but full fine-tuning of multi-billion-parameter models is expensive and impractical for research or edge deployment. **Small code LMs (350M parameters)** offer a lightweight alternative, but zero-shot performance on structured database tasks is often insufficient.

### Objectives


| #   | Objective                                                               | Status        |
| --- | ----------------------------------------------------------------------- | ------------- |
| 1   | Build a modular, reproducible pipeline for three database query tasks   | Complete      |
| 2   | Evaluate baseline (zero-shot) performance on a fixed benchmark          | Complete      |
| 3   | Fine-tune task-specific LoRA adapters (smoke → full scale)              | Complete      |
| 4   | Compare baseline vs fine-tuned models with automated + semantic metrics | Complete      |
| 5   | Support multiple hardware backends (CUDA, MPS, DirectML, CPU)           | Complete      |
| 6   | Full-scale LoRA training on complete TEND dataset                       | Complete (v4) |
| 7   | Deploy OpenAI-compatible API + desktop tool                             | Complete      |




### Approach

One shared base model (`codegen-350M-multi`). Each of three tasks gets its own small adapter (~few–40 MB) while base weights remain frozen. Tasks are **evaluated and trained independently** using gold supervision from TEND.

### Tech Stack


| Layer    | Technology                                                                                    |
| -------- | --------------------------------------------------------------------------------------------- |
| Language | Python 3.11                                                                                   |
| Model    | HuggingFace Transformers, PEFT, TRL SFTTrainer                                                |
| Base LM  | Salesforce/codegen-350M-multi                                                                 |
| Dataset  | TEND ([care2achieve/tend](https://huggingface.co/datasets/care2achieve/tend)) — Spider + BIRD |
| Metrics  | BLEU, ROUGE-L, BERTScore, CodeBLEU, Ollama judge, execution accuracy                          |
| Tracking | MLflow (SQLite backend)                                                                       |
| Deploy   | FastAPI, Google Cloud Run, Hugging Face Hub                                                   |
| Product  | CustomTkinter desktop tool + PostgreSQL                                                       |


---



## Reference Appendix C — System Architecture (Extended Diagrams)



### Training architecture

```mermaid
flowchart TD
    START["LoRA Training Orchestrator"] --> CFG["Load config + resolve compute device"]
    CFG --> LOOP["For each task: text2sql → sql2nosql → nosql2doc"]
    LOOP --> LOAD["Load TEND train split (~10,697 rows)"]
    LOAD --> FILTER["Filter by required fields + token budget (2048)"]
    FILTER --> BUILD["Build training prompt + completion target"]
    BUILD --> SFT["Prepare SFT dataset — completion-only loss"]
    SFT --> MODEL["Load frozen base model weights"]
    MODEL --> LORA["Apply PEFT LoRA (v4: r=32, attn + FFN)"]
    LORA --> TRAIN["Supervised fine-tuning — 5 epochs, lr=2e-4"]
    TRAIN --> SAVE["Save best adapter per task"]
    SAVE --> META["Write training metadata"]
```





### Evaluation architecture

```mermaid
flowchart TD
    START["Benchmark Evaluation Runner"] --> INIT["Load base model + task adapters"]
    INIT --> GOLD["Frozen gold benchmark — 50 examples"]
    GOLD --> RUN["Run 3 independent task pipelines"]
    RUN --> AM["Automated metrics: EM, exec acc, CodeBLEU..."]
    AM --> JUDGE["Optional semantic judge (qwen3:8b)"]
    JUDGE --> EXPORT["Metrics summary + per-task detail reports"]
```





### End-to-end lifecycle

```mermaid
sequenceDiagram
    participant Dev as Researcher
    participant Base as Baseline Evaluation
    participant Train as LoRA Training
    participant LoRA as Adapter Evaluation
    participant HF as Hugging Face Hub
    participant CR as Cloud Run

    Dev->>Base: Run baseline benchmark
    Base-->>Dev: Baseline metrics report
    Dev->>Train: Train LoRA v4 (cloud GPU)
    Train-->>Dev: Three task adapters saved
    Dev->>LoRA: Evaluate v4 on gold benchmark
    LoRA-->>Dev: v4 metrics report
    Dev->>HF: Publish adapters to Hub
    Dev->>CR: Deploy multi-adapter API
    CR-->>Dev: OpenAI-compatible HTTPS endpoint
```





### Logical architecture layers

```text
CodeGen Capstone System
├── Runtime configuration & hyperparameters
├── Research pipelines
│   ├── Text2SQL · SQL2NoSQL · Documentation (independent tasks)
│   ├── Dataset loader · Model manager · LoRA trainer · Evaluator
│   └── Frozen benchmark · Experiment tracking · Results store
├── Model artifacts
│   ├── Frozen base model (CodeGen-350M-multi)
│   └── LoRA v4 adapters (one per task)
├── Multi-adapter API gateway (OpenAI-compatible + Cloud Run)
└── Desktop AI SQL Assistant (schema · generate · validate · execute)
```

---



## Reference Appendix D — Methodology



### Research Questions

1. Can a **350M-parameter code LM** perform database query tasks zero-shot?
2. Does **LoRA fine-tuning** improve task-specific quality over the baseline?
3. How do **automated metrics** compare to an **LLM semantic judge** and **execution accuracy**?
4. Can the pipeline be **reproducible** across hardware (CUDA, MPS, CPU)?



### Task Definitions


| Task ID     | Input                     | Output              | Supervision     |
| ----------- | ------------------------- | ------------------- | --------------- |
| `text2sql`  | Question + SQL schema     | SQL query           | `sql`           |
| `sql2nosql` | Gold SQL + schemas        | MongoDB shell query | `nosql_query`   |
| `nosql2doc` | Gold Mongo query + schema | Plain-English doc   | `documentation` |


Each prompt prefixed with `Task: <task_name>`.

### Training Data Splits


| Split                  | Source                       | Size          | Purpose             |
| ---------------------- | ---------------------------- | ------------- | ------------------- |
| Train                  | TEND spider + bird train     | ~10,697 rows  | SFT                 |
| Eval (during training) | TEND test                    | ~1,625 rows   | Held-out eval_loss  |
| Benchmark              | spider_gold_validation.jsonl | **50** frozen | Capstone comparison |




### Key Design Decisions

- **Independent task evaluation** — no prediction chaining during benchmark
- **Prompt parity** — training prompts == inference prompts (unit-tested)
- **Completion-only loss** — prompt tokens masked (`-100`)
- **One base, three adapters** — PEFT hot-swap at serve time

---



## Reference Appendix E — Data & Datasets



### TEND on Hugging Face

**Repository:** [care2achieve/tend](https://huggingface.co/datasets/care2achieve/tend)


| Config       | Train rows | Test rows | Origin           |
| ------------ | ---------- | --------- | ---------------- |
| `spider`     | 6,730      | 859       | Spider benchmark |
| `bird`       | 3,967      | 766       | BIRD benchmark   |
| **Combined** | **10,697** | **1,625** | LoRA training    |




### Record Schema


| Field                   | Role                           |
| ----------------------- | ------------------------------ |
| `question`              | NL input                       |
| `schema` / `sql_schema` | SQL DDL                        |
| `sql` / `sql_query`     | Gold SQL                       |
| `nosql_schema`          | Mongo schema JSON              |
| `nosql_query`           | Gold Mongo shell query         |
| `documentation`         | Gold plain-English explanation |
| `db_id`                 | Database identifier            |




### Example Row

```json
{
  "question": "How many singers do we have?",
  "schema": "CREATE TABLE singer (...); ...",
  "sql": "SELECT count(*) FROM singer",
  "nosql_schema": "{\"singer\": {\"_id\": \"ObjectId\", ...}}",
  "nosql_query": "db.singer.count()",
  "documentation": "This query counts the total number of singers in the database.",
  "db_id": "concert_singer"
}
```



### Per-Task Required Fields


| Task      | Required inputs                                | Target          |
| --------- | ---------------------------------------------- | --------------- |
| text2sql  | `question`, `schema`                           | `sql`           |
| sql2nosql | `sql`, `schema`, `nosql_schema`                | `nosql_query`   |
| nosql2doc | `nosql_query`, `nosql_schema`, `documentation` | `documentation` |




### Token Budget


| Setting                 | Value        |
| ----------------------- | ------------ |
| Max sequence            | 2048 tokens  |
| Max target (completion) | 256 tokens   |
| Prompt budget           | ~1792 tokens |


Truncation: drop from **start** of prompt if over budget; target never truncated.

### Loading (Python)

```python
from src.datasets.tend_loader import TENDLoader, load_gold_validation

train_rows = []
for config in ("spider", "bird"):
    loader = TENDLoader(config=config)
    train_rows.extend(loader.load_split("train"))

gold_examples = load_gold_validation()  # 50 frozen
```

Via Hugging Face:

```python
from datasets import load_dataset
spider = load_dataset("care2achieve/tend", "spider")
bird = load_dataset("care2achieve/tend", "bird")
```

---



## Reference Appendix F — LoRA v4 Full Results

> **Model:** `Salesforce/codegen-350M-multi`  
> **Judge:** `qwen3:8b`  
> **Benchmark:** spider_gold_validation (50 examples/task)  
> **Execution eval:** PostgreSQL + MongoDB result-set comparison enabled



### Training Context


| Run      | Train samples | Epochs | LoRA               | Device          |
| -------- | ------------- | ------ | ------------------ | --------------- |
| Baseline | —             | —      | none               | —               |
| v1       | 50            | 10     | r=16, attn         | Local           |
| v2       | 500           | 5      | r=16, attn         | Local           |
| v3       | ~8,040        | 5      | r=16, attn         | MPS             |
| **v4**   | ~8,040        | 5      | **r=32, attn+FFN** | **Kaggle CUDA** |




### v4 LoRA Config

```yaml
lora:
  r: 32
  lora_alpha: 64
  lora_dropout: 0.05
  bias: none
  target_modules: [qkv_proj, out_proj, fc_in, fc_out]
```

Kaggle overrides: per-device batch **2**, grad accum **8**, effective batch **16**. Training time ~**7h 34m**.

### Full Text2SQL Metrics


| Metric                | Baseline | v1    | v2    | v3    | **v4**    |
| --------------------- | -------- | ----- | ----- | ----- | --------- |
| Execution accuracy    | 12%      | 20%   | 34%   | 54%   | **60%**   |
| Exact match           | 0%       | 8%    | 20%   | 38%   | **40%**   |
| Structural similarity | 0.700    | 0.792 | 0.859 | 0.910 | **0.916** |




### Full SQL2NoSQL Metrics


| Metric                | Baseline | v1    | v2    | v3    | **v4**    |
| --------------------- | -------- | ----- | ----- | ----- | --------- |
| Execution accuracy    | 22%      | 4%    | 32%   | 74%   | **88%**   |
| Exact match           | 4%       | 0%    | 8%    | 58%   | **80%**   |
| Structural similarity | 0.163    | 0.553 | 0.791 | 0.926 | **0.983** |




### Full Documentation Metrics


| Metric               | Baseline | v1    | v2    | v3    | **v4**    |
| -------------------- | -------- | ----- | ----- | ----- | --------- |
| Judge score (0–10)   | 0.1      | 1.5   | 3.1   | 6.4   | **7.8**   |
| Embedding similarity | 0.714    | 0.889 | 0.926 | 0.957 | **0.960** |
| Exact match          | 0%       | 0%    | 0%    | 2%    | **2%**    |




### Mermaid — execution accuracy by version

```mermaid
xychart-beta
    title "Execution Accuracy by Version (%)"
    x-axis ["Baseline", "v1", "v2", "v3", "v4"]
    y-axis "Accuracy" 0 --> 95
    bar "Text2SQL" [12, 20, 34, 54, 60]
    bar "SQL2NoSQL" [22, 4, 32, 74, 88]
```





### Takeaways

- Monotonic improvement baseline → v4 on nearly every metric
- v4 capacity upgrade (r 16→32, +FFN targets) yields +6 pp text2sql exec, +14 pp sql2nosql exec
- Documentation judge **7.8** — semantic quality high despite 2% exact match

---



## Reference Appendix G — Beam vs Greedy Decoding (v4)

Same v4 checkpoints; only `generation.decoding_strategy` differs.


| Setting               | Greedy  | Beam (num_beams=4) |
| --------------------- | ------- | ------------------ |
| Text2SQL exec         | 60%     | **64%**            |
| Text2SQL exact match  | 40%     | **44%**            |
| SQL2NoSQL exec        | **88%** | 82%                |
| SQL2NoSQL exact match | **80%** | 66%                |
| Doc judge             | 7.8     | **8.5**            |


**Conclusion:** Beam helps Text2SQL and documentation; greedy wins for SQL2NoSQL. Product can use per-task decoding policy.

---



## Reference Appendix H — Version History


| Version        | Train samples | Epochs            | LoRA              | Adapter size | Text2SQL exec | SQL2NoSQL exec | Doc judge |
| -------------- | ------------- | ----------------- | ----------------- | ------------ | ------------- | -------------- | --------- |
| Baseline       | —             | —                 | —                 | —            | 12%           | 22%            | 0.1       |
| v1             | 50            | 10                | r=16 attn         | ~7.5 MB      | 20%           | 4%             | 1.5       |
| v2             | 500           | 5                 | r=16 attn         | ~7.5 MB      | 34%           | 32%            | 3.1       |
| v3             | ~8,040        | 5                 | r=16 attn         | ~7.5 MB      | 54%           | 74%            | 6.4       |
| **v4 (FINAL)** | ~8,040        | 5                 | r=32 attn+FFN     | ~40 MB       | **60%**       | **88%**        | **7.8**   |
| v5             | ~8,040        | 5 (text2sql only) | v4 + stronger reg | ~40 MB       | 48%           | —              | —         |


**v5 note:** Text2sql-only regularization ablation (lower LR, higher dropout/weight decay). **Not** the final release — keep **v4** for all three tasks.

### v4 Per-Task Training Loss


| Task      | Train loss | Best eval loss | Runtime |
| --------- | ---------- | -------------- | ------- |
| text2sql  | 0.089      | 0.247          | ~2h 13m |
| sql2nosql | 0.038      | 0.034          | ~2h 18m |
| nosql2doc | 0.568      | 0.994          | ~2h 55m |


---



## Reference Appendix I — Hugging Face & Cloud Run Deployment



### Published Model Adapters


| Task      | Hub URL                                                                                                                            |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| text2sql  | [https://huggingface.co/care2achieve/codegen-350M-text2sql-lora](https://huggingface.co/care2achieve/codegen-350M-text2sql-lora)   |
| sql2nosql | [https://huggingface.co/care2achieve/codegen-350M-sql2nosql-lora](https://huggingface.co/care2achieve/codegen-350M-sql2nosql-lora) |
| nosql2doc | [https://huggingface.co/care2achieve/codegen-350M-nosql2doc-lora](https://huggingface.co/care2achieve/codegen-350M-nosql2doc-lora) |
| Dataset   | [https://huggingface.co/datasets/care2achieve/tend](https://huggingface.co/datasets/care2achieve/tend)                             |


Publish command:

```bash
PYTHONPATH=hf-deploy python hf-deploy/publish/push_adapters.py --version v4
```

`hf-deploy/manifest.yaml` sets `checkpoint_version: v4`.

### Run API Locally

**Option A — local checkpoint weights:**

```bash
pip install -r hf-deploy/requirements.txt
PYTHONPATH=hf-deploy uvicorn hf_deploy.api.app:app --host 0.0.0.0 --port 8000
```

**Option B — load adapters from Hub:**

```bash
export HF_DEPLOY_ADAPTER_SOURCE=hub
export HF_ORG=care2achieve
PYTHONPATH=hf-deploy uvicorn hf_deploy.api.app:app --host 0.0.0.0 --port 8000
```



### Endpoints


| Endpoint          | URL                                                          |
| ----------------- | ------------------------------------------------------------ |
| Health            | `GET /health`                                                |
| Chat              | `POST /v1/chat/completions`                                  |
| Models            | `GET /v1/models`                                             |
| Cursor base URL   | `http://localhost:8000/v1` or `https://<service>.run.app/v1` |
| Cursor model name | `codegen-multi-adapter`                                      |




### Example curl

```bash
curl http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "codegen-multi-adapter",
    "messages": [{
      "role": "user",
      "content": "Write a SQL query to list customer names.\n\nSchema:\ncustomers(id, name)\n\nSQL:"
    }]
  }'
```

Response includes `codegen_routing` (`intent`, `confidence`, `method`).

### Intent Routing


| User intent examples         | Adapter                       |
| ---------------------------- | ----------------------------- |
| write / generate SQL         | text2sql                      |
| convert SQL to Mongo / NoSQL | sql2nosql                     |
| generate documentation       | nosql2doc                     |
| Ambiguous                    | Clarification (no generation) |




### Google Cloud Run


| Item             | Detail                                                        |
| ---------------- | ------------------------------------------------------------- |
| Region (default) | `asia-south2` (Hyderabad)                                     |
| Container port   | 8080                                                          |
| Adapters         | Loaded from Hub at startup                                    |
| Redeploy         | `cd hf-deploy/infra/cloudrun && source env.sh && ./deploy.sh` |


**Why Cloud Run:** built-in HTTPS, scale-to-zero, no VM babysitting, one-command redeploy.

### Optional HF Space

Space id: `care2achieve/codegen-multi-adapter`  
Note: Docker Spaces may require HF PRO; **Cloud Run is the recommended hosted path**.

---



## Reference Appendix J — Desktop Tool (AI SQL Assistant)

Standalone CustomTkinter desktop app for Text-to-SQL against PostgreSQL. **Does not load LoRA locally** — calls hf-deploy FastAPI.

### Prerequisites


| Requirement                  | Notes                    |
| ---------------------------- | ------------------------ |
| Python 3.11 (conda `ai` env) | Repo environment         |
| PostgreSQL                   | DVD/Pagila sample schema |
| hf-deploy API                | Port 8000                |
| Docker (optional)            | Bundled DB setup         |




### Database Setup

```bash
chmod +x tool/scripts/setup_dvd_database.sh
./tool/scripts/setup_dvd_database.sh
```

Creates database `dvd` with Pagila rental schema (tables: `customer`, `film`, `rental`, etc.).

Connection string:

```env
DATABASE_URL=postgresql+psycopg://tend:tend@localhost:5432/dvd
```



### Quick Start

```bash
# 1. PostgreSQL + dvd data
./tool/scripts/setup_dvd_database.sh

# 2. Inference server (separate terminal)
PYTHONPATH=hf-deploy uvicorn hf_deploy.api.app:app --host 0.0.0.0 --port 8000

# 3. Desktop app
python tool/app.py
# macOS: ./tool/run.sh
```



### Flow

NL question → embedding-based table selection → prompt build → FastAPI generate → **SELECT-only validation** → execute on PostgreSQL → results grid + activity log.

### Activity Log Stages

`schema_loaded` → `tables_selected` → `prompt_built` → `sql_generated` → `validation_passed` → `rows_retrieved`

### Architecture

```text
Desktop AI SQL Assistant
├── Application shell & launcher
├── User interface layer (CustomTkinter)
├── Core services (settings, DB, schema, inference client, validation)
├── Text-to-SQL pipeline orchestrator
└── Task tabs (Text-to-SQL · SQL→NoSQL stub · Documentation stub)
```

---



## Reference Appendix K — Cursor IDE Deployment Plan



### Objective

Deploy one CodeGen base + three LoRA adapters behind an **OpenAI-compatible** API that:

1. Detects intent from natural language (no task keys)
2. Uses schema in the user prompt (MVP)
3. Prefixes prompt with `Task: <intent>`
4. Hot-swaps LoRA via PEFT `set_adapter`
5. Returns response for Cursor / any OpenAI client



### MVP Decisions


| Topic             | Decision                                                      |
| ----------------- | ------------------------------------------------------------- |
| Schema            | Included in user prompt                                       |
| Multi-step        | Not supported (one intent per request)                        |
| Adapter switching | PEFT `set_adapter` hot-swap                                   |
| Cursor API        | `POST /v1/chat/completions`                                   |
| Intent classifier | Rules fast-path + MiniLM embeddings; low confidence → clarify |




### Architecture

```text
Cursor IDE (OpenAI-compatible base URL)
    │
POST /v1/chat/completions
    │
FastAPI Gateway (local or Cloud Run)
    │
Intent Classifier (rules → embeddings → clarify)
    │
Prompt Builder (Task: <intent>)
    │
Adapter Router (set_adapter)
    │
CodeGen Base + Selected LoRA v4
    │
Response (+ codegen_routing metadata)
```



### Cursor Configuration


| Setting  | Value                                                        |
| -------- | ------------------------------------------------------------ |
| Base URL | `http://localhost:8000/v1` or `https://<service>.run.app/v1` |
| Model    | `codegen-multi-adapter`                                      |


Optional: `"intent": "text2sql"` in request body skips classification.

### Roadmap Phases


| Phase                                                 | Status |
| ----------------------------------------------------- | ------ |
| Manifest + adapter resolver + classifier + OpenAI API | Done   |
| Publish v4 adapters to Hub + Cloud Run deploy         | Done   |
| Validation layer, streaming, metrics                  | Future |


---



## Reference Appendix L — VS Code Extension Specification



### Objective

VS Code extension that works like a built-in AI model: scan workspace, discover schemas, build local semantic indexes, detect intent, retrieve relevant schemas, build prompt, call Hugging Face OpenAI endpoint, show response in Chat. **Model stays stateless.**

### Design Principles

1. **Local-first** — workspace scan, schema discovery, embeddings stay on machine
2. **Stateless model** — remote endpoint only does inference
3. **Incremental indexing** — re-index changed files only
4. **Extensible adapters** — new tasks = new PromptBuilder templates



### Extension vs Server


| VS Code extension (local)         | Remote model (Cloud Run / HF) |
| --------------------------------- | ----------------------------- |
| Scan workspace / DB schemas       | Receive complete prompt       |
| Build semantic index              | Route intent → LoRA           |
| Detect intent (or rely on server) | Generate completion           |
| Retrieve top-K relevant tables    | Return text only              |
| Build final prompt + Chat UI      | No repo state                 |




### Supported Schema Types (v1)

- `.sql`, `.ddl` files
- Future: Mongo JSON Schema, Prisma, Liquibase, Flyway



### Embedding Engine

- **Model:** BAAI/bge-small-en-v1.5 (or all-MiniLM-L6-v2)
- **Index:** hnswlib-node or similar JS ANN
- **Cache:** `.vscode/codegen/` (index.bin, metadata.json)



### Intent Detection

Initial: rule-based (`text2sql`, `sql2nosql`, `nosql2doc`). Future: small classifier.

### Prompt Templates

**Text2SQL:**

```
Task: text2sql

Translate the question into SQL.

Schema:
{{schema}}

Question:
{{question}}
```

**SQL2NoSQL:**

```
Task: sql2nosql

Schema:
{{schema}}

SQL:
{{sql}}
```

**NoSQL2Doc:**

```
Task: nosql2doc

Schema:
{{schema}}

Query:
{{query}}
```



### Configuration Settings

- `codegen.endpoint`
- `codegen.apiKey`
- `codegen.model`
- `codegen.autoIndex`
- `codegen.topK` (default 3)
- `codegen.embeddingModel`
- `codegen.maxPromptTokens`



### Milestones

1. Extension scaffold + workspace scan
2. SQL parser + metadata extraction
3. Embeddings + vector index
4. Intent + retrieval + prompt builder
5. Hugging Face OpenAI client + streaming
6. VS Code Chat integration + settings UI



### Acceptance Criteria

User types: *"How many singers do we have?"*

Extension automatically: detects `text2sql` → searches index → selects `singer` table → builds prompt → calls endpoint → streams SQL into Chat. User never manually pastes schemas.

---



## Reference Appendix M — TEND Dataset Project

**TEND** = companion system for execution-validated multi-task dataset generation. Published on Hugging Face as [care2achieve/tend](https://huggingface.co/datasets/care2achieve/tend).

### Pipeline Overview

For each Spider/BIRD sample:

1. Build SQL DDL deterministically (schema builder)
2. Build Mongo schema deterministically (schema translator)
3. Convert SQL → Mongo via **cascade** (rules → [sql-mongo-converter](https://pypi.org/project/sql-mongo-converter/) → Ollama fallback)
4. Generate documentation with Ollama (after valid query exists)
5. Execute SQL on **PostgreSQL** and Mongo on **MongoDB**
6. Keep rows where normalized result sets **match** → gold tier
7. Publish to Hugging Face



### SQL → MongoDB Translation Stages


| Stage | Component             | When used                                    |
| ----- | --------------------- | -------------------------------------------- |
| 1     | Pattern rules         | JOIN→`$lookup`, subqueries, INTERSECT/EXCEPT |
| 2     | SQL→NoSQL Python tool | Simple SELECTs via sql-mongo-converter       |
| 3     | Ollama codegen        | Both above failed                            |
| Fail  | —                     | Row marked failed to convert                 |


**Important for presentation:** Ollama generates documentation and acts as query **fallback only** — not as a judge picking between candidates in the capstone evaluation story. Gold tier uses **execution accuracy only**.

### Dataset Tiers


| Tier       | Meaning                             |
| ---------- | ----------------------------------- |
| **Bronze** | All generated rows (pass + fail)    |
| **Gold**   | Only `execution_accuracy=true` rows |




### Gold Export Stats


| Config    | Split | Bronze     | Gold      | Gold rate |
| --------- | ----- | ---------- | --------- | --------- |
| bird      | test  | 1,534      | 377       | 24.6%     |
| bird      | train | 9,428      | 2,096     | 22.2%     |
| spider    | test  | 1,034      | 658       | 63.6%     |
| spider    | train | 8,659      | 5,944     | 68.6%     |
| **Total** |       | **20,655** | **9,075** | **43.9%** |




### CLI Commands

```bash
tend-run --dataset spider --split train --chunked
tend-bronze-to-gold --dataset spider --split train
tend-publish-hf --publish
tend-run-execution-accuracy
```



### Engineering Highlights

- Chunked + resumable bronze generation (500-row chunks)
- Async Ollama with concurrency semaphore
- Docker PostgreSQL 16 + MongoDB 8
- Dump/restore snapshots for demos



### Default Ollama Models


| Role               | Default    |
| ------------------ | ---------- |
| Code generator     | `qwen3:8b` |
| Judge (TEND build) | `qwen3:8b` |


CodeGen **evaluation** uses `qwen3:8b` semantic judge for documentation scoring — separate from TEND query selection during gold filtering.

---

*End of detailed presentation guide. This file is self-contained — update TODOs (team, date, video URL), then copy each SLIDE / APPENDIX section into PowerPoint / Google Slides / Keynote.*