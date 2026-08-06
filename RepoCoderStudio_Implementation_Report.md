# RepoCoder Studio

## Combined Stage (Stages 1–3), Stage 4 and Stage 5

### Final Full-Run and RAG-Aware Implementation Report

**Document status:** Capstone implementation through Stage 5 completed and evaluated  
**Full-run notebook:** `notebooks/RepoCoderStudio_Fast_Corrected_Retrain.ipynb`  
**RAG-aware extension notebook:** `notebooks/RepoCoderStudio_RAG_Augmented_Retrain.ipynb`  
**Full-run profile:** Complete pipeline using a time-bounded, corrected demo data profile  
**Student model:** `Qwen/Qwen2.5-Coder-0.5B-Instruct`  
**Combined-stage adapter:** `RepoCoderStudio_FastCorrected_LoRA_v1_0`  
**Final RAG-aware adapter:** `RepoCoderStudio_RAGAware_LoRA_v1_2`  
**Report date:** 6 August 2026

---

# 1. Executive summary

RepoCoder Studio is a bilingual, repository-aware software engineering
assistant. It accepts natural-language requirements, Python code or Java code
and supports six transformations:

1. natural language to Python;
2. natural language to Java;
3. Python to Java;
4. Java to Python;
5. Python to natural-language explanation;
6. Java to natural-language explanation.

The project was developed in three connected parts.

- **Combined Stage (Stages 1–3)** created the trustworthy data, task contracts,
  fine-tuning pipeline and baseline-versus-fine-tuned evaluation framework.
- **Stage 4** added repository understanding: parsing a codebase, indexing its
  symbols, retrieving relevant code and following dependencies.
- **Stage 5** connected retrieval to generation so that the model could use
  repository evidence, explain its retrieval decision and be tested with and
  without Retrieval-Augmented Generation (RAG).

The final corrected full run is deliberately smaller than the original
capstone profile because Colab GPU time is limited. It is nevertheless a full
execution of the complete architecture: data construction, validation,
baseline evaluation, fresh LoRA training, fine-tuned evaluation, Stage 4
retrieval, Stage 5 controlled generation and the final user interface.

The run completed successfully. The approved corpus contained 537 aligned
records, expanded into 3,222 balanced task examples. Completion-only LoRA
training finished at 303 steps with 8.80 million trainable parameters. On a
held-out, identical 20-example-per-task comparison, fine-tuning improved the
primary result for T1, T2, T3, T5 and T6, and preserved T4 at 100% Python parse
success. The most material improvement was Python-to-Java compilation, which
increased from 40% to 85%.

Repository understanding also completed successfully. LedgerFlow evaluation
reached 97% Recall@5 and 0.921 MRR@5. Hybrid retrieval with cross-encoder
reranking was the best tested retrieval configuration, reaching 97% Recall@5
and 0.980 MRR@5. External RepoBench evaluation covered 100 Python and 100 Java
rows, while the controlled Stage 5 demonstration retrieved the exact hidden
transfer policy as the top source with real embeddings and explicit
provenance.

The final Stage 5 refinement addressed an important interaction discovered
during UI testing: the first LoRA adapter had learned only the plain task
prompt and had never been trained to consume a `Retrieved Context` section.
The project therefore added RAG-formatted training examples for approximately
35% of eligible T1–T4 training rows, response-safe budgeting for the longer
prompts, and a separate RAG-aware adapter. The resulting
`RepoCoderStudio_RAGAware_LoRA_v1_2` trained successfully on 2,877 retained
rows for 359 steps. It then passed two repository-grounded qualitative
benchmarks: exact LedgerFlow email-validation behaviour and the hidden
transfer-risk policy. In both cases the correct repository function was the
single top-ranked source and the fine-tuned-with-RAG arm reproduced the
repository-specific details that were absent from the user request.

The central research question is not simply whether the system can print code.
It is:

> Can a small code model be adapted for bilingual software-engineering tasks,
> and can repository retrieval improve it when the correct answer depends on
> information that is present in the repository but absent from the user
> prompt?

The implementation keeps three claims separate:

- **fine-tuning quality:** pretrained model versus fine-tuned model;
- **RAG quality:** the same model without repository evidence versus with
  repository evidence;
- **functional correctness:** whether generated code passes trusted tests in an
  isolated Docker environment.

This separation is important. Valid syntax does not prove correct business
logic, and a retrieved passage does not automatically mean that RAG helped.

---

# 2. Problem statement

General-purpose code models are useful for isolated functions, but real
software work is repository-specific. A developer may ask for a function that
must follow:

- existing business thresholds;
- naming conventions;
- shared validation rules;
- related Python or Java implementations;
- dependency relationships;
- project-specific error handling.

A pretrained model cannot be expected to know this private or local
information. Providing the whole repository in every prompt is also
impractical. It consumes too many tokens, introduces irrelevant code and makes
the answer difficult to trace.

RepoCoder Studio therefore combines two complementary techniques:

1. **Parameter-efficient fine-tuning** teaches a small model the six expected
   task formats and improves its bilingual code-transformation behaviour.
2. **Repository RAG** retrieves a small amount of relevant repository evidence
   at inference time, allowing the model to follow rules that were never part
   of its general pretraining or user prompt.

The intended system is not an autonomous coding agent. It is an evidence-aware
generation and evaluation platform for repository-grounded code generation and
evaluation.

---

# 3. Project objectives

The project was designed to meet the following objectives.

## 3.1 Functional objectives

- Support natural language, Python and Java inputs.
- Generate Python, Java or natural-language explanations.
- Fine-tune one student model across all six tasks.
- Understand both Python and Java repositories.
- Retrieve direct matches and dependency-related evidence.
- Allow users to select generic, sample-banking or public-repository examples.
- Compare baseline, fine-tuned, no-RAG and RAG outputs.
- Expose the system through both Gradio and FastAPI interfaces.
- Produce portable artifacts for cloud deployment.

## 3.2 Experimental objectives

- Use held-out splits for evaluation.
- Compare models on the same examples.
- Prevent validation or test answers from entering the RAG index.
- Keep fine-tuning benefit separate from RAG benefit.
- Report uncertainty for adaptive RAG decisions.
- Preserve raw generations as experimental evidence.
- Distinguish parsing, compilation and functional correctness.

## 3.3 Engineering objectives

- Run on a constrained Google Colab GPU.
- Resume compatible interrupted work safely.
- Refuse incompatible checkpoints and mock retrieval evidence.
- Avoid loading duplicate models and embedding models.
- Use one consistent output structure across notebook, API and Docker.
- Fail safely when Docker, Java parsing or an optional external repository is
  unavailable.

---

# 4. The project journey at a glance

The system evolved in a deliberate sequence.

```text
Raw bilingual datasets
        ↓
Normalization and semantic alignment
        ↓
Validated NL–Python–Java corpus
        ↓
Six task-specific prompt contracts
        ↓
Pretrained baseline evaluation
        ↓
Completion-only LoRA fine-tuning
        ↓
Fine-tuned evaluation
        ↓
Repository parsing and indexing
        ↓
Dense + lexical + dependency-aware retrieval
        ↓
Repository/corpus RAG
        ↓
Four-arm controlled generation
        ↓
RAG prompt-contract diagnosis
        ↓
Grounded RAG-aware LoRA refinement
        ↓
Repository-specific semantic verification
        ↓
Python/Java functional verification
        ↓
Gradio and FastAPI demonstrations
```

The stages are connected, but each has a distinct responsibility. The data
pipeline creates trustworthy training examples. Fine-tuning teaches task
behaviour. Repository retrieval supplies project knowledge. Functional testing
checks whether generated behaviour is actually correct.

---

# 5. System architecture

RepoCoder Studio uses a layered architecture.

| Layer | Responsibility |
|---|---|
| Configuration | Centralizes model, data, training, evaluation, retrieval and storage settings |
| Data ingestion | Loads XLCoST and CodeXGLUE/CodeSearchNet datasets |
| Normalization | Cleans natural language, Python, Java and dataset-specific formatting tokens |
| Alignment | Builds semantically matched NL–Python–Java records |
| Validation | Checks structure, quality, duplication and provenance |
| Task construction | Expands approved records into six supervised tasks |
| Training | Applies completion-only LoRA, then a separately versioned RAG-aware refinement using grounded evidence prompts |
| Evaluation | Generates held-out predictions and calculates task-specific metrics |
| Repository explorer | Parses repositories, extracts symbols and builds indexes |
| Retrieval engine | Combines dense, lexical, dependency and corpus retrieval |
| Generation engine | Builds prompts, applies optional context and generates responses |
| Output validation | Extracts the intended answer and checks Python/Java/NL structure |
| Functional evaluation | Runs curated Python and Java tests in isolated Docker containers |
| Presentation | Provides Gradio and FastAPI browser interfaces |

All persistent artifacts are stored beneath the project’s `outputs` directory.
The canonical fine-tuned adapter location is:

```text
outputs/adapters/<adapter-name>
```

The notebook, training code, FastAPI application, Docker images and Compose
configuration all use this same location.

---

# 6. Combined Stage: Stages 1–3

The Combined Stage establishes the foundation on which Stage 4 and Stage 5
depend. It converts heterogeneous public data into a traceable multilingual
corpus, constructs the six task families, trains a small model and evaluates
it against the original pretrained model.

## 6.1 Why a combined stage was necessary

The source datasets were not designed as one clean three-column table of
natural language, Python and Java. Different configurations contain different
fields, formatting conventions and row orders. Directly joining rows by
position would create false translations and contaminate training.

The Combined Stage therefore treats corpus construction as an engineering and
validation problem rather than a simple download step.

## 6.2 Data sources

The implementation supports:

- XLCoST Python program-level data;
- XLCoST Java program-level data;
- CodeXGLUE/CodeSearchNet Python data;
- CodeXGLUE/CodeSearchNet Java data.

The loader uses a persistent disk cache when available. A fresh full-run
package contains no previous data cache, outputs, checkpoint or adapter, so the
new experiment cannot silently inherit the earlier model.

## 6.3 Normalization

Normalization performs the following operations before alignment or training:

- standardizes whitespace;
- removes dataset formatting tokens;
- converts XLCoST newline and indentation markers;
- removes the SentencePiece visible-space marker and its common encoding
  corruption;
- normalizes Python and Java text independently;
- retains the original split and record provenance.

Normalization is versioned. Its version is included in checkpoint
compatibility so that a checkpoint trained using an older text representation
cannot be silently resumed.

## 6.4 Deterministic sampling for the corrected full run

Earlier limited runs selected the first `N` rows from each source split. This
was reproducible but potentially biased because dataset order may group similar
topics or repositories.

The corrected implementation uses seeded deterministic sampling before
applying the profile limit. Python and Java configurations use the same
split-specific seed. This provides reproducibility without always selecting a
dataset prefix.

The corrected full-run profile uses:

| Setting | Value |
|---|---:|
| Raw training limit per source configuration | 300 |
| Raw validation limit per source configuration | 60 |
| Raw test limit per source configuration | 60 |
| Final evaluation examples per task | 20 |
| Random seed | 42 |

These are source limits, not the final number of training examples. Each
approved multilingual row can generate several task examples.

## 6.5 Semantic alignment

Python and Java records are not assumed to be aligned by row number. The
alignment engine instead builds three evidence pools:

- natural-language descriptions;
- Python programs;
- Java programs.

It uses semantic similarity and structural evidence to construct candidate
triples. When embedding alignment is unavailable, exact normalized-description
matching is available as an explicit fallback rather than an invisible
approximation.

Each aligned row records:

- source dataset and configuration;
- original split;
- alignment strategy;
- alignment confidence;
- stable record identifier;
- Python structural metadata;
- Java structural metadata.

## 6.6 Validation and approval

Candidate rows pass through validation before they can become training data.
The validation layer checks:

- missing or very short fields;
- duplicate content;
- Python syntax and AST structure;
- Java structure using Tree-sitter when available;
- consistent provenance;
- alignment evidence;
- optional trusted-test metadata.

Rows are separated into approved and rejected corpora. This ensures that the
training and RAG components use traceable, explicitly accepted material.

## 6.7 Six-task construction

Each approved record is expanded into the applicable task examples.

| Task | Source | Target | Main objective |
|---|---|---|---|
| T1 | Natural language | Python | Implement a Python solution |
| T2 | Natural language | Java | Implement a Java solution |
| T3 | Python | Java | Translate behaviour into Java |
| T4 | Java | Python | Translate behaviour into Python |
| T5 | Python | Natural language | Explain Python behaviour |
| T6 | Java | Natural language | Explain Java behaviour |

Every example contains an explicit task contract. The contract identifies the
task, expected output type, response header, success criteria and forbidden
output patterns. The task ID is therefore part of the prompt instead of being
left for the model to infer.

## 6.8 Curriculum and task balance

The six tasks have different levels of difficulty and different output
modalities. If they were presented in long task-specific blocks, the model
could temporarily over-specialize and forget other task formats.

The curriculum builder:

- groups rows by task;
- shuffles training examples deterministically within each task;
- interleaves tasks using round-robin ordering;
- reports the task distribution for every split.

## 6.9 Pretrained baseline

The baseline is the original student model without a LoRA adapter. It is
evaluated before training on the same held-out examples later used for the
fine-tuned model.

This baseline is necessary because an isolated fine-tuned score does not show
whether adaptation helped. Improvement must be calculated relative to the
unchanged pretrained model.

## 6.10 LoRA fine-tuning

The project uses Low-Rank Adaptation (LoRA), which trains small adapter matrices
while keeping the original model parameters frozen. This is suitable for
Colab because it greatly reduces trainable parameters and memory consumption.

The corrected full run uses:

| Training setting | Value |
|---|---:|
| Base model | Qwen2.5-Coder-0.5B-Instruct |
| Epochs | 1 |
| Learning rate | 5e-5 |
| Per-device batch size | 1 |
| Gradient accumulation | 8 |
| LoRA rank | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0.05 |
| Loss masking | Completion only |
| Adapter name | RepoCoderStudio_FastCorrected_LoRA_v1_0 |

The lower learning rate reduces the risk of destructive adaptation observed in
the previous larger run.

## 6.11 Completion-only loss

The model sees both the instruction and answer, but loss is calculated only on
the answer. A multi-header completion collator locates the response boundary
for each of the six task contracts and masks all earlier prompt tokens.

Before training begins, the notebook checks that every retained row still
contains a complete response header after token budgeting. An invalid example
is rejected rather than allowing the trainer to learn from prompt tokens.

## 6.12 EOS termination correction

The earlier training text did not consistently supervise an explicit end of
response. This contributed to answers that repeated or continued until the
maximum token limit.

The corrected pipeline:

- appends the tokenizer’s EOS token to each completion;
- explicitly restores the final EOS label even when padding and EOS use the
  same token ID;
- passes EOS and padding IDs during generation;
- records the termination contract in the training manifest.

## 6.13 Checkpoint compatibility

Checkpoint resume is useful when Colab disconnects, but unsafe when a
checkpoint belongs to different data or prompts.

A checkpoint is resumed only when the following match:

- run mode;
- model name;
- random seed;
- split limits;
- normalized task-dataset hash;
- prompt and task-contract versions;
- normalization and EOS versions;
- LoRA and optimization settings;
- maximum sequence length.

The fresh full-run package contains no previous checkpoint, so its first
training session necessarily begins from the base model.

## 6.14 Baseline and fine-tuned evaluation

The evaluator performs task-wise seeded selection. Baseline and fine-tuned
models therefore receive the same held-out rows, prompts, output limits,
normalization and metrics.

The corrected run evaluates up to 20 examples for each of six tasks:

- up to 120 baseline generations;
- up to 120 fine-tuned generations;
- up to 240 main benchmark generations in total.

If a task has fewer than 20 valid held-out examples, all available examples are
used and the actual count is reported.

## 6.15 Metrics

Different tasks require different primary metrics.

| Tasks | Primary metric | Supporting evidence |
|---|---|---|
| T1, T4 | Python parse success | Official CodeBLEU, structural and text similarity |
| T2, T3 | Java compile success | Official CodeBLEU, structural and text similarity |
| T5, T6 | ROUGE-L | semantic and lexical similarity |

Official CodeBLEU dependencies and both Tree-sitter grammars are pinned and
validated in the installation cell. If official CodeBLEU cannot run, the
fallback remains clearly labelled `CodeBLEU-lite`.

Parse or compile success is not reported as functional correctness. Functional
claims require trusted execution tests.

---

# 7. Stage 4: Repository understanding

The Combined Stage teaches general task behaviour. Stage 4 supplies knowledge
about a particular repository.

## 7.1 Why Stage 4 is required

A repository is more than a collection of text files. Useful evidence includes:

- functions and classes;
- file paths;
- method names;
- imports and calls;
- Python and Java structure;
- dependencies between symbols;
- related migration implementations.

Stage 4 transforms this structure into a searchable evidence layer.

## 7.2 Repository catalogue

The final implementation exposes three choices.

| Repository mode | Purpose |
|---|---|
| Generic / no repository | Demonstrates the model without repository grounding |
| LedgerFlow | Controlled bilingual banking repository with hidden policy rules |
| AWS S3 public examples | Real public Python and Java code with commit provenance |

LedgerFlow is the primary controlled demonstration. The public AWS examples add
authenticity, but they are not presented as the primary causal benchmark.

## 7.3 Parsing and symbol extraction

The repository explorer:

- walks supported source files;
- parses Python with the Python AST;
- parses Java with Tree-sitter when available;
- records functions, methods and classes;
- extracts imports and calls;
- creates stable symbol metadata;
- builds a dependency graph;
- records Python-to-Java migration relationships in the sample repository.

If Tree-sitter Java is unavailable, the fallback is reported rather than
silently treated as full structural parsing.

## 7.4 Isolated repository indexes

LedgerFlow and AWS use separate parsed and embedding directories. Evidence from
one repository cannot accidentally appear when the other repository is
selected.

The two explorers reuse a single embedding-model instance, reducing memory
usage without mixing their indexes.

## 7.5 Retrieval methods

Stage 4 supports:

- **dense retrieval**, which uses semantic vector similarity;
- **lexical retrieval**, which rewards exact identifiers and terms;
- **hybrid retrieval**, which combines both signals;
- **cross-encoder reranking**, which re-scores the shortlist more precisely;
- **dependency expansion**, which adds directly related symbols.

The notebook includes a real three-arm ablation:

1. dense only;
2. dense plus lexical hybrid;
3. hybrid plus cross-encoder.

Both Python and Java queries are included. If both hybrid weights are
misconfigured as zero, the implementation falls back to dense-only ranking
instead of crashing.

## 7.6 Retrieval provenance

Every result records where and how it was found. Dependency-expanded evidence
uses:

```text
retrieval_method = dependency_expansion
provenance = repository:dependency
```

The user interface can display dense score, lexical score, final score,
retrieval method, file path and provenance.

## 7.7 Public repository handling

The AWS example repository is downloaded as a sparse checkout. The system
records its commit and preparation details. Re-running preparation is
idempotent: an existing valid checkout is reused.

The application does not allow an arbitrary user request to clone any remote
repository. Online reindexing is restricted to configured paths and controlled
administrative settings.

---

# 8. Stage 5: Repository-Augmented Generation

Stage 5 connects the Stage 4 evidence layer to the generation model.

## 8.1 What RAG means in this project

Retrieval-Augmented Generation performs three actions:

1. convert the user’s task into a retrieval query;
2. select relevant repository or approved-corpus evidence;
3. place that evidence into the model prompt before generation.

The model weights do not change during RAG. Fine-tuning changes how the model
behaves in general; RAG supplies task-specific knowledge at inference time.

## 8.2 Repository and corpus evidence

The retrieval engine can combine:

- repository-source evidence from Stage 4;
- dependency-expanded repository evidence;
- validated training-corpus evidence.

The corpus index contains approved training rows only. Validation and test rows
are excluded so that RAG cannot retrieve the exact answer being evaluated.

## 8.3 Modality-aligned corpus indexes

One mixed embedding cannot serve every source modality equally well. The
corrected corpus retriever therefore maintains:

- natural-language keys for T1 and T2;
- Python-code keys for T3 and T5;
- Java-code keys for T4 and T6.

This enables real Java corpus retrieval for T4 and T6 rather than disabling
those tasks or comparing Java code against an NL/Python-only vector space.

## 8.4 Retrieval safety

The corpus index includes several safeguards.

- Corpus text is redacted once at load time before embedding, persistence or
  preview.
- Mock embeddings fail closed for reportable results.
- The corpus SHA-256 detects content changes.
- Embedding model, dimension and split filter are validated.
- Java and Python index row counts must match their metadata.
- The repository and corpus retrievers reuse the same embedding-model instance.

## 8.5 Immutable retrieval outcome

An earlier API implementation wrote a shared “last retrieval decision,” ran a
slow generation and read the decision afterward. A concurrent request could
replace that shared state.

The corrected `resolve()` method returns one `RetrievalOutcome` containing:

- context;
- decision;
- sources;
- scores;
- method and provenance.

The API calls it once and uses that same immutable result throughout the
response.

## 8.6 Evidence budgeting

Evidence is assembled as complete blocks. A block is either fully included or
fully dropped when the character budget is reached. The implementation never
cuts code or its closing evidence marker halfway through.

## 8.7 RAG abstention

Retrieval is allowed to abstain when evidence is weak or ambiguous. The
decision includes the reason, top score and score margin.

An empty or rejected context is not labelled as successful RAG. This prevents
the system from claiming a RAG comparison when no evidence was actually used.

## 8.8 Controlled four-arm experiment

The focused Stage 5 cell generates four arms.

| Model | Evidence |
|---|---|
| Pretrained baseline | No RAG |
| Pretrained baseline | Repository RAG |
| Fine-tuned model | No RAG |
| Fine-tuned model | Repository RAG |

All four arms use the same request. Both RAG arms use the same immutable
retrieval outcome. This design separates the effect of fine-tuning from the
effect of repository evidence.

## 8.9 Hidden-policy benchmark

RAG can only demonstrate value when relevant information is missing from the
prompt. The principal LedgerFlow benchmark therefore asks the model to
implement the repository’s transfer-risk policy without giving it the exact
thresholds, weights, restricted-country list or score cap.

The no-RAG model must work without those details. The RAG model receives the
retrieved repository policy. Python and Java functional tests then check the
exact hidden rules.

This is more meaningful than a prompt that already contains every expected
constant.

## 8.10 Adaptive RAG as an optional experiment

The project can tune `top_k = 0`, `1` or `2` independently per task using the
validation split. Candidate arms are compared with paired bootstrap resampling.

The policy reports:

- mean paired delta;
- confidence interval;
- probability of positive lift;
- selection stability;
- enabled, disabled or inconclusive status.

This experiment is disabled in the time-bounded final run because it requires
hundreds of additional generations. It remains available for a later capstone
run and checkpoints each tagged evaluation row so an interruption can resume.

## 8.11 Generation and Docker verification are separated

Colab always generates and saves the Python and Java no-RAG/RAG candidates.
Docker availability controls only functional checking.

When Docker is unavailable, the notebook records:

```text
generation.status = COMPLETE
verification.status = NOT_FEASIBLE
```

This avoids discarding valid model evidence merely because Colab cannot run the
container harness.

## 8.12 Docker functional evaluation

The functional layer supports both Python and Java. It first runs known-correct
self-tests to prove that the harness works. Only then does it judge model
outputs.

Containers run with:

- no network;
- read-only filesystem;
- non-root UID and GID;
- memory, CPU and process limits;
- deterministic names;
- explicit container kill on timeout.

The Java evaluator supports package-aware compilation. Temporary directory and
file permissions are set so the non-root container can read the mounted
harness.

The EC2 merge step is reporting-only. It replaces only the Docker-dependent
sections of `functional_eval_report.json`. Skipping the merge does not affect
the adapter, generated code, RAG index, Gradio interface or FastAPI service.

## 8.13 RAG-aware fine-tuning

The first fine-tuned adapter improved the six task contracts, but it had been
trained only on the plain prompt structure:

```text
Instruction → Input → Response
```

At inference time, Stage 5 adds `Retrieved Context` and an evidence policy.
That prompt shape was unfamiliar to the first adapter. A controlled email
example showed that the base model could sometimes follow the evidence while
the fine-tuned model ignored it. This was treated as a design gap rather than
hidden as an isolated bad generation.

The correction introduced three focused components:

- `RAGPromptBuilder` renders the same evidence contract during training that
  is used during inference;
- `RAGAugmentedTaskDatasetBuilder` adds real retrieved evidence to about 35%
  of eligible T1–T4 training examples while excluding self-matches;
- `response_safe_training_rag.py` truncates only the input/context portion,
  never the supervised response, and rejects a row if the response still
  cannot fit within the 1,024-token training window.

Training context is capped at 2,000 characters, compared with the larger
inference allowance, to reduce overflow risk. Each augmented row records its
retrieved context and prompt hash. The new adapter is written to a separate
versioned path, so the original combined-stage adapter remains reproducible.

## 8.14 Focused repository-only evidence routing

The general interface can combine repository and approved-corpus evidence.
For demonstrations that explicitly ask for a private repository function,
however, unrelated corpus examples can distract a 0.5B model. The final
focused verification and UI route therefore use:

```python
top_k=1, sources=("repo",)
```

This keeps only the strongest repository result. The internal selector is
named `repo`; `repository` is the human-facing provenance label. The retrieval
engine now rejects an unknown selector with a clear error instead of silently
returning `no_evidence`. This small validation guard prevents a configuration
mistake from being misreported as a retrieval-quality failure.

---

# 9. Generation and output validation

The generation engine decodes generated token IDs only, rather than decoding
the prompt and attempting to remove it as text. It applies deterministic
generation, explicit EOS handling and task-aware output limits.

The shared extraction module:

- extracts fenced code when present;
- handles unfenced Python and Java conservatively;
- removes incomplete repeated tails;
- normalizes SentencePiece artefacts;
- preserves raw model output separately;
- never invents missing algorithms or constants.

The same extraction contract is used across baseline, fine-tuned, RAG, UI and
functional-evaluation flows.

---

# 10. User interfaces

## 10.1 Gradio notebook interface

Gradio launches as the final full-run notebook cell, after all computed
artifacts have already been saved. It reuses the models and indexes already in
memory.

The final interface allows the user to select:

- task;
- generic, LedgerFlow or AWS repository mode;
- baseline or fine-tuned model;
- no-RAG or RAG evidence mode;
- curated demonstrations for every repository and task.

For code-to-natural-language tasks, real Python or Java snippets are preloaded.
Outputs are displayed in target-language-aware code components. The UI
preserves the model's actual line layout instead of cosmetically rewriting an
incorrect generation. Retrieval decisions and evidence traces are displayed
separately from syntax validation.

The curated catalogue contains 54 demonstrations: exactly three examples for
each of the six tasks across Generic, LedgerFlow and AWS modes. An optional
single validation-guided retry is clearly labelled when it succeeds; it is a
serving reliability feature and is never counted as first-pass evaluation
performance. Repository-specific demonstrations use the focused top-1
repository route so unrelated corpus examples do not crowd out the requested
private API. A cold-session loader restores the saved v1.2 adapter and
repository indexes without rerunning training or evaluation.

## 10.2 FastAPI browser interface

The deployable application exposes:

- health status;
- task and repository catalogues;
- curated showcase examples;
- generation;
- four-arm comparison;
- controlled administrative reindexing;
- the static browser UI.

The server uses per-model locks and a bounded generation semaphore. If the LoRA
adapter is unavailable, the service can still start in baseline-only mode and
reports the adapter error clearly.

The health endpoint distinguishes repository-only RAG from repository-plus-
corpus RAG through `rag_corpus_loaded`.

The browser interface mirrors the Gradio comparison, including code-aware
Python/Java display, validation status, retry disclosure, RAG decisions,
dense/lexical/reranker scores, retrieval method, provenance and a structural
comparison summary.

## 10.3 Cloud deployment

The current deployable UI is plain HTML, CSS and JavaScript served by FastAPI.

Docker, Docker Compose and environment configuration use the same canonical
adapter and output paths as the notebook. The consolidated GCP handoff includes
the final adapter, approved corpus, corpus indexes, both repository indexes,
repository sources and the FastAPI static UI. The Docker build deliberately
excludes training caches and checkpoints from the image while retaining them
in the submission folder. Repository manifests are portable between the
Colab path and the container's `/data` path while still checking source-tree
hash, Git commit, parser version, embedding model and vector dimension.

The container honours Cloud Run's `PORT` variable, runs as a non-root user and
provides `/api/health` for readiness checking. The package is deployment-ready;
the live GCP service URL and post-deployment smoke test remain operational
deployment activities rather than missing Stage 5 implementation.

---

# 11. Final executed results

Values in this section come from the executed notebooks, saved JSON/CSV
artifacts and the final supplied verification outputs. Earlier exploratory,
failed or superseded adapter runs are not used as success evidence.

## 11.1 Execution environment

| Item | Final value |
|---|---|
| Colab runtime/GPU | Google Colab, NVIDIA Tesla T4 |
| Python version | 3.12.13 |
| Torch/CUDA version | PyTorch 2.11.0+cu128; CUDA available |
| Official Python CodeBLEU validation | Passed; `codebleu` 0.7.0 |
| Official Java CodeBLEU validation | Passed; `codebleu` 0.7.0 |
| Tree-sitter Python validation | Passed; grammar 0.21.0 |
| Tree-sitter Java validation | Passed; grammar 0.21.0 |
| Mock embeddings | `False` |
| Notebook completion status | Full corrected run completed; final Gradio interface launched |
| RAG-aware extension status | Completed; v1.2 adapter trained, restored in a fresh runtime and verified |
| Final focused retrieval mode | Repository-only top-1 with real embeddings and cross-encoder reranking |

## 11.2 Corpus and task construction

| Measure | Final result |
|---|---:|
| Candidate corpus rows | 616 |
| Approved corpus rows | 537 |
| Rejected corpus rows | 79 |
| Six-task examples produced | 3,222 |
| Training task rows before budgeting | 2,430 |
| Training task rows retained | 2,424 |
| Validation task rows | 366 |
| Test task rows | 426 |
| Response-header preflight failures | 0 |
| Maximum retained sequence length | 1,021 tokens within a 1,024-token limit |

Every approved record produced all six tasks: 537 examples per task, with
405/61/71 train/validation/test records per task before sequence budgeting.
Only six training rows were excluded by the response-preserving token policy,
giving 99.75% retention.

Evidence files:

```text
outputs/approved_corpus/approved_corpus.jsonl
outputs/rejected_corpus/rejected_corpus.jsonl
outputs/task_datasets/task_dataset.jsonl
outputs/reports/training_sequence_budget_report.json
outputs/reports/task_dataset_summary_v2_3.json
```

## 11.3 Training outcomes

### 11.3.1 Combined-stage adapter

| Measure | Final result |
|---|---:|
| Adapter path | `outputs/adapters/RepoCoderStudio_FastCorrected_LoRA_v1_0` |
| Base model | `Qwen/Qwen2.5-Coder-0.5B-Instruct` |
| Trainable parameters | 8,798,208 |
| Total parameters | 502,830,976 |
| Trainable percentage | 1.7497% |
| LoRA configuration | rank 16, alpha 32, dropout 0.05 |
| Learning rate / epochs | 5×10⁻⁵ / 1 epoch |
| Global training steps | 303 |
| Initial logged loss | 1.6619 at step 10 |
| Final logged loss | 1.0805 at step 300 |
| Aggregate training loss | 1.1626 |
| Training runtime | 1,255 seconds (approximately 20.9 minutes) |
| Training completed without incompatible resume | Yes; fresh compatible run |
| EOS supervision recorded | `supervised_eos_v1` |

Training used completion-only loss masking with explicit task contracts. This
means prompt tokens were not treated as target answers, and supervised EOS
tokens taught the model where responses should stop.

Evidence files:

```text
outputs/reports/training_history.csv
outputs/reports/training_summary.json
outputs/adapters/RepoCoderStudio_FastCorrected_LoRA_v1_0/trained_model_manifest.json
```

### 11.3.2 RAG-aware adapter

| Measure | Final result |
|---|---:|
| Adapter path | `outputs/adapters/RepoCoderStudio_RAGAware_LoRA_v1_2` |
| Base model | `Qwen/Qwen2.5-Coder-0.5B-Instruct` |
| Plain training rows before augmentation | 2,430 |
| Added grounded RAG-formatted rows | 567 (35% of eligible T1–T4 training rows) |
| Training rows before response-safe budgeting | 2,997 |
| Retained training rows | 2,877 (approximately 96.0%) |
| Rows excluded to protect the response boundary | 120 |
| Validation rows | 366 |
| Trainable parameters | 8,798,208 |
| Total parameters | 502,830,976 |
| Trainable percentage | 1.7497% |
| Global training steps | 359 |
| Training duration | 1,391 seconds (approximately 23.2 minutes) |
| First logged loss | 1.5917 at step 10 |
| Final logged loss | 0.8960 at step 350 |
| Minimum logged loss | 0.7190 at step 330 |
| Evaluation during training | Disabled to avoid Colab CUDA OOM; post-training verification used instead |
| Loss masking | Completion tokens only |
| Prompt contract | `rag_prompt_contract_v1.2` |
| Training manifest | `training_manifest_rag_v1.2` |
| Grounded task dataset | `task_dataset_rag_grounded.jsonl` |
| Adapter isolation | New versioned path; combined-stage adapter not overwritten |

The loss remained finite and generally declined while the adapter weights
were confirmed finite. More importantly, the adapter was restored in a fresh
runtime and used successfully by the unchanged generation and validation
stack. Training loss is evidence that optimization ran correctly; the
repository-grounded benchmarks below provide the behaviour-level evidence.

Evidence files:

```text
outputs/reports/training_history.csv
outputs/reports/training_summary.json
outputs/adapters/RepoCoderStudio_RAGAware_LoRA_v1_2/trained_model_manifest.json
```

## 11.4 Baseline versus fine-tuned results

| Task | Primary metric | Examples | Baseline | Fine-tuned | Delta | Interpretation |
|---|---|---:|---:|---:|---:|---|
| T1: NL → Python | Python parse success | 20 | 90% | 100% | +10 pp | Improved to full structural success |
| T2: NL → Java | Java compile success | 20 | 70% | 85% | +15 pp | Clear improvement |
| T3: Python → Java | Java compile success | 20 | 40% | 85% | +45 pp | Largest improvement |
| T4: Java → Python | Python parse success | 20 | 100% | 100% | 0 pp | Preserved full structural success |
| T5: Python → NL | ROUGE-L | 20 | 0.2168 | 0.3197 | +0.1028 | Better explanations |
| T6: Java → NL | ROUGE-L | 20 | 0.2091 | 0.2819 | +0.0728 | Better explanations |

Across the four code-output tasks, average primary structural success increased
from 75.0% to 92.5%. For T1–T3, official CodeBLEU also improved; T4 retained
100% parse success but had lower similarity scores, showing why structural and
reference-similarity measures are reported separately. Main failure rates
decreased by 35 percentage points for T1, 25 points for T2, 55 points for T3
and 5 points for T4. Neither model produced empty predictions in this
evaluation.

Evidence files:

```text
outputs/evaluation/baseline_prediction_logs.jsonl
outputs/evaluation/finetuned_prediction_logs.jsonl
outputs/evaluation/baseline_vs_finetuned_comparison.csv
outputs/evaluation/report_overall_outcome_table.csv
```

## 11.5 Stage 4 repository results

### Repository summaries

| Repository | Files | Functions/methods | Classes | Mock embeddings | Notes |
|---|---:|---:|---:|---|---|
| LedgerFlow | 21 | 74 | 9 | False | Controlled bilingual banking fixture; 912 lines |
| AWS S3 public examples | 170 | 794 | 144 | False | Public Python/Java repository subset; 27,726 lines |

### LedgerFlow retrieval evaluation

| Metric | Result |
|---|---:|
| Precision@5 | 0.232 |
| Recall@5 | 0.970 |
| MRR@5 | 0.921 |
| Queries evaluated | 50 hand-labelled queries |

### External RepoBench retrieval

| Language | Rows | Top-1 | Top-3 | MRR | Random top-1 | Honest interpretation |
|---|---:|---:|---:|---:|---:|---|
| Python | 100 | 0.350 | 0.830 | 0.601 | 0.322 | Top-1 modestly above chance; strong top-3 |
| Java | 100 | 0.300 | 0.900 | 0.599 | 0.364 | Top-1 below candidate chance; strong top-3 |

Bootstrap 95% intervals were [0.26, 0.44] for Python top-1 and [0.22, 0.39]
for Java top-1. The external benchmark therefore supports a useful candidate
retrieval claim, especially at top-3, but not a claim that Java top-1 ranking
is solved.

## 11.6 Retrieval ablation

| Arm | Precision@5 | Recall@5 | MRR@5 | Reranker applied | Interpretation |
|---|---:|---:|---:|---|---|
| Dense only | 0.238 | 0.940 | 0.906 | No | Strong baseline retrieval |
| Hybrid | 0.245 | 0.950 | 0.927 | No | Lexical evidence improves exact-symbol queries |
| Hybrid + cross-encoder | 0.279 | 0.970 | 0.980 | Yes | Best tested configuration |

The detailed cross-language ablation includes NL, Python and Java queries.
Every displayed hybrid-plus-cross-encoder row records
`reranker_applied=True`, proving that reranking was exercised rather than
merely configured.

Evidence files:

```text
outputs/evaluation/hybrid_vs_cross_encoder_ablation.csv
outputs/evaluation/hybrid_vs_cross_encoder_quality.csv
```

## 11.7 Stage 5 RAG results

The approved-corpus index contains 405 training-split rows. Separate
natural-language, Python and Java indexes each contain all 405 eligible rows,
using `sentence-transformers/all-MiniLM-L6-v2` with
`mock_embeddings=False`. Validation and test records are excluded from the
RAG corpus to prevent answer leakage.

### RAG-aware verification 1: repository email validation

The prompt requested LedgerFlow's `validate_email` implementation without
including its exact regular expression. Repository-only top-1 retrieval
returned:

| Field | Final value |
|---|---|
| RAG context used | `True` |
| Retrieval decision | `evidence_accepted` |
| Top source | `validate_email` in `utils/validators.py` |
| Top score | 0.8128 |
| Score margin | 0.8128 |
| Additional evidence | None; one complete repository block only |

The four arms exposed a useful progression:

| Arm | Observed result |
|---|---|
| Baseline, no RAG | Produced a generic valid regex, not the repository contract |
| Baseline + RAG | Ended without usable Python in this run, even after guarded retry |
| Fine-tuned, no RAG | Produced generic validation with a different function name and no repository-specific stripping behaviour |
| Fine-tuned + RAG | Produced `validate_email`, the exact `^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$` pattern and `email.strip()` |

The automated benchmark recorded:

```text
Fine-tuned/With RAG reproduces the repository's exact regex pattern: True
Email benchmark success: True
```

This is stronger than a syntax-only comparison: the successful arm recovered
specific implementation details available only in the retrieved repository
evidence.

### RAG-aware verification 2: hidden transfer-risk policy

The second prompt requested `transfer_risk_score` but intentionally omitted
all private thresholds, weights, restricted countries and the score cap.
Repository-only top-1 retrieval returned:

| Field | Final value |
|---|---|
| RAG context used | `True` |
| Retrieval decision | `evidence_accepted` |
| Top source | `transfer_risk_score` in `policies/transfer_policy.py` |
| Top score in notebook verification | 0.8836 |
| Retrieval method shown in UI | `dense+lexical+cross_encoder` |
| Provenance | `repository` |

The final fine-tuned-with-RAG output preserved every checked repository rule:

- amount thresholds of 100,000 and 250,000;
- corresponding weights of 25 and 40;
- customer-tenure weight of 20 for fewer than 30 days;
- the exact high-risk set `IR`, `KP`, `SY` and weight 30;
- the untrusted-device weight of 15;
- input normalization with `strip().upper()`;
- the final `min(score, 100.0)` cap.

The automated benchmark recorded:

```text
Top retrieved source is policies/transfer_policy.py: True
Exact policy constants/countries preserved: True
```

The Gradio four-arm view made the comparison visually clear. Baseline/no-RAG
returned a placeholder, and fine-tuned/no-RAG produced a long syntactically
valid but invented country policy. Fine-tuned-with-RAG produced the compact,
correct repository implementation. Structural `PASS` labels in the UI are
explicitly separated from semantic correctness; the repository-rule checks
support the grounding claim.

### Java demonstration boundary

The Java `FraudDetector` example confirmed that the UI, Java retrieval,
validation and retry paths operate, but the fine-tuned-with-RAG retry produced
an unrelated one-line class. A compile/structural pass after retry therefore
was not counted as a semantic RAG success. This result is retained as an honest
model-capacity limitation, while the two Python cases above are the completed
and reproducible Stage 5 grounding demonstrations.

Evidence files:

```text
outputs/reports/stage5_four_arm_repository_demo.json
outputs/reports/rag_grounded_retrain_v1_2_verification.json
outputs/adapters/RepoCoderStudio_RAGAware_LoRA_v1_2/trained_model_manifest.json
```

## 11.8 Functional RAG evaluation

Generation results should be recorded even when Docker is unavailable.

| Language | No-RAG generation | RAG generation | Docker status | Pass-rate lift |
|---|---|---|---|---:|
| Python | Saved | Saved; exact policy was top-1 | NOT_FEASIBLE in Colab | Not calculated |
| Java | Saved | Saved; `TransferPolicy.java` method was top-1 | NOT_FEASIBLE in Colab | Not calculated |

Python and Java no-RAG/RAG candidates were generated successfully and retained.
In both languages the RAG arm retrieved the intended policy first with
cross-encoder reranking. Docker was unavailable in the Colab runtime, so the
report correctly records functional execution as `NOT_FEASIBLE` rather than
converting structural validation into a functional claim. The standalone
non-root, no-network Docker evaluator remains included for execution on EC2 or
another Docker-capable host.

Evidence file:

```text
outputs/reports/functional_eval_report.json
```

## 11.9 UI and deployment evidence

| Check | Result |
|---|---|
| Gradio launched from final notebook cell | Passed; public interface URL created |
| Generic/no-RAG examples available | Yes |
| LedgerFlow examples available | Yes |
| AWS examples available | Yes |
| Curated catalogue coverage | 54 examples; three per repository/task section |
| Python code-aware display | Passed; complete multi-line validated output shown |
| Java code-aware display | Implemented; raw model layout is preserved rather than cosmetically rewriting generated code |
| Retrieval decision and provenance visible | Passed |
| Cross-encoder scores visible | Passed |
| Four-arm controlled comparison | Passed; selectable baseline/fine-tuned and no-RAG/RAG arms |
| Guarded retry visibility | Passed; retries are labelled and remain UI-only |
| Fine-tuned + RAG Python showcase | Passed for email validation and hidden transfer policy |
| Java semantic showcase | Mixed; structural retry worked, but the tested fine-tuned output was not repository-correct |
| Cold-session artifact restoration | Implemented in `src/gradio_runtime.py` |
| FastAPI browser UI parity | Implemented |
| FastAPI health endpoint | Implemented; deployment smoke test pending |
| GCP container handoff | Prepared and internally audited |
| Live GCP URL | Deployment activity after submission handoff |

The final UI is a demonstration surface, not a score-manipulation layer.
Validation-guided retries are explicitly labelled and are excluded from the
saved first-pass quantitative evaluation.

---

# 12. Security, reliability and auditability

The final design includes the following safeguards.

- Secret-like corpus content is redacted before embedding or persistence.
- Mock embeddings fail closed for reported retrieval results.
- RAG indexes training rows only.
- Repository indexes are isolated by repository.
- Retrieval outcomes are immutable per request.
- API model generation is lock-protected and concurrency-bounded.
- Administrative reindexing is restricted and disabled by default in
  production.
- Docker execution is non-root, no-network, read-only and resource-limited.
- Raw model outputs are retained separately from extracted/scored outputs.
- Manifests and hashes make artifact lineage visible.
- Incompatible checkpoints are ignored rather than force-loaded.
- Results are written to separate baseline, fine-tuned and tagged RAG files.

---

# 13. What was learned during the full journey

## 13.1 Data quality matters more than dataset size alone

The early assumption that more rows would automatically produce a stronger
model was incomplete. Incorrect alignment, dataset-order bias or malformed
training completions can make a larger run worse. A smaller clean experiment is
more defensible than a larger noisy one.

## 13.2 Fine-tuning and RAG solve different problems

Fine-tuning is appropriate for learning task format, language transformation
and response discipline. RAG is appropriate for repository-specific facts.
Trying to make fine-tuning memorize every repository rule would be expensive,
stale and difficult to audit.

## 13.3 A fair comparison requires identical examples

Baseline and fine-tuned results cannot be compared honestly if they use
different random subsets, prompt versions or extraction logic. Persisting the
held-out dataset and applying seeded task-wise selection is therefore part of
the experimental design, not a minor implementation detail.

## 13.4 Termination is part of model quality

The earlier run showed that a model can learn useful content while producing
poor final outputs because it does not stop correctly. EOS supervision,
completion-only masking and generated-token-only decoding are essential parts
of the model pipeline.

## 13.5 Compilation is not correctness

A Java class can compile while using the wrong threshold. Python can parse
while implementing incorrect business logic. Structural metrics are useful,
but the project learned to reserve functional claims for trusted tests.

## 13.6 RAG needs a task that actually requires retrieval

If the prompt already contains all policy values, no-RAG has the same
information as RAG. The hidden-policy benchmark is a better causal test because
the repository contains information that is deliberately absent from the
request.

## 13.7 Retrieval must be observable

A single similarity score is insufficient for debugging. The final system
shows source path, dense score, lexical score, method, provenance and the
accept/abstain decision. This makes it possible to explain why context was or
was not supplied.

## 13.8 Uncertainty cannot be fixed by more bootstrap samples

Bootstrap resampling measures uncertainty in the examples that were actually
observed. It cannot manufacture information missing from a small validation
set. Inconclusive is an honest result and must remain distinct from evidence
that RAG is harmful.

## 13.9 Infrastructure should not suppress model evidence

Docker is necessary for safe functional verification but unnecessary for
generation. Separating those actions allowed Colab to save useful candidates
even when Docker was unavailable.

## 13.10 One canonical artifact path prevents deployment confusion

The earlier presence of both `outputs/trained_model` and `outputs/adapters`
made it unclear which model the notebook, API and Docker image should load.
Standardizing on `outputs/adapters/<name>` simplified training, restart,
serving and deployment.

## 13.11 A notebook is also a presentation document

A technically correct notebook can still be difficult to assess when cells
depend on hidden state or optional cells raise errors. The final notebook makes
profiles visible, restores state from artifacts, skips optional experiments
cleanly and launches the UI only after results are saved.

## 13.12 Fine-tuning and RAG must share the same prompt contract

Manual Gradio testing first revealed a negative interaction: the original
fine-tuned adapter could follow the plain task prompt but ignored an unfamiliar
`Retrieved Context` section. The base model sometimes used the same evidence
more effectively. The failure was traced to a prompt-distribution mismatch,
not to FAISS retrieval: the training corpus contained only
`Instruction → Input → Response`, while inference added retrieved evidence and
an evidence policy.

The project corrected this rather than treating it as future work. The final
training flow includes grounded RAG-formatted examples for eligible code tasks,
stores the retrieved context in row metadata, preserves the supervised
response during token budgeting, and trains a separate v1.2 adapter. Fresh
runtime restoration then demonstrated that fine-tuned-with-RAG reproduced both
the exact LedgerFlow email-validation pattern and the complete hidden transfer
policy.

The broader lesson is that fine-tuning and RAG are not independent modules at
the prompt boundary. A model must be trained on the evidence structure it will
encounter in production. Retrieval can be perfectly correct and still fail to
improve generation when that contract is unfamiliar.

## 13.13 Retrieval source names are part of the executable contract

The retrieval selector uses `repo`, while result provenance is displayed as
`repository`. Confusing those values once produced an empty result that looked
like a retrieval miss. The final engine validates selectors and fails loudly
on unknown values. Configuration vocabulary deserves the same validation as
model and index manifests because a silent typo can invalidate an experiment.

## 13.14 Structural validation must not be presented as semantic success

The UI correctly showed that a placeholder Python function and an unrelated
Java class can be syntactically valid. The final presentation therefore labels
the comparison as structural, exposes retry status, preserves raw output and
uses repository-specific semantic checks for the mentor-facing success claim.
Formatting or compilation can support a result, but neither is allowed to
convert incorrect business logic into a reported win.

---

# 14. Limitations

The principal limitations are bounded and do not prevent completion of the
Stage 5 capstone scope.

1. The student model has 0.5 billion parameters and serves six heterogeneous
   tasks; larger models may improve semantic and long-context reliability.
2. The corrected run evaluates 20 held-out examples per task. The improvements
   are strong project evidence, while a larger repeated study would provide
   narrower uncertainty intervals.
3. LedgerFlow is a controlled hidden-policy repository. The AWS repository and
   RepoBench add public evidence, but broader repository-level generation
   benchmarks remain valuable future work.
4. Standalone `javac` cannot verify SDK-dependent Java without the repository's
   dependency classpath. Such cases require repository-aware builds.
5. Docker functional verification was not available in Colab and remains a
   separate host-dependent verification step.
6. The live GCP URL and post-deployment smoke test are operational deployment
   activities, not part of the completed Stage 5 claim.
7. The six-task quantitative table evaluates the combined-stage
   `FastCorrected_LoRA_v1_0` adapter. The later RAG-aware v1.2 adapter was
   validated with two focused Python repository-grounding cases rather than a
   second full six-task sweep, because repeating the entire generation matrix
   would exceed the remaining Colab GPU budget.
8. Java retrieval, compilation and UI paths are implemented, but the tested
   fine-tuned Java RAG example remained semantically unreliable. It is reported
   as a model-capacity/generalization limitation, not as a successful Java RAG
   claim.
9. The email and transfer-policy demonstrations are controlled qualitative
   evidence. They establish that the corrected integration can work, but they
   do not replace a larger multi-repository statistical generation study.

---

# 15. GCP Deployment

The deployment target is Google Cloud Run using the existing FastAPI container.
Deployment is deliberately separated from the completed modeling claim: Stage
5 is complete and locally/cloud-notebook verified, while creation of a public
GCP URL is an operational handoff.

## 15.1 Deployment architecture

The proposed production flow is:

```text
Browser
  → Cloud Run HTTPS endpoint
  → FastAPI application
  → baseline model and RAG-aware LoRA adapter
  → persisted LedgerFlow/corpus FAISS indexes
  → structured generation, validation and provenance response
```

The same service supports the browser interface and JSON API, preventing a
separate demonstration backend from diverging from deployment behaviour.

## 15.2 Container contract

The supplied Docker assets provide:

- a deterministic application image;
- Cloud Run's injected `PORT` environment variable;
- a non-root runtime user;
- `/api/health` readiness reporting;
- explicit adapter and index paths under the project artifact root;
- deployment defaults pinned to `RepoCoderStudio_RAGAware_LoRA_v1_2`,
  `rag_prompt_contract_v1.2` and `training_manifest_rag_v1.2`;
- image-build checks for the v1.2 weights and manifest, followed by runtime
  manifest checks against the configured model and prompt contract;
- baseline/fine-tuned and no-RAG/RAG request handling;
- retrieval scores, method, provenance and decision metadata.

The service must fail closed if the configured adapter, manifest or real
embedding index is absent. Docker-based generated-code evaluation remains a
separate sandboxed process and is not run inside the web request path.

## 15.3 Artifact strategy

Model and index artifacts are larger and more persistent than application
source code. A deployment should therefore either bake a validated immutable
artifact set into the image or download a versioned set from a private Google
Cloud Storage bucket during controlled startup. The following paths must stay
consistent:

```text
outputs/adapters/RepoCoderStudio_RAGAware_LoRA_v1_2/
outputs/repositories/ledgerflow/
outputs/corpus_index/
outputs/approved_corpus/
```

The manifest fingerprints are checked before service readiness so the API
cannot silently combine an adapter with the wrong dataset or prompt contract.

## 15.4 Operational deployment steps

1. Create a GCP project and enable Artifact Registry and Cloud Run.
2. Build the supplied Dockerfile and push the tagged image to Artifact
   Registry.
3. Provide the validated adapter/index artifacts through the chosen immutable
   image or private-bucket strategy.
4. Deploy the image to Cloud Run with sufficient memory and request timeout.
5. Set only required environment variables and secrets through Cloud Run,
   never in the image or repository.
6. Verify `/api/health` reports the expected adapter, repository index,
   corpus-index status and `mock_embeddings=False`.
7. Run one no-RAG request and the two successful repository-grounded smoke
   tests before publishing the endpoint.

CPU-only serving is possible for the 0.5B model but may have higher latency.
For an interactive production experience, an appropriate GPU-capable Cloud Run
configuration or another GCP GPU service should be evaluated against cost and
cold-start constraints.

## 15.5 Current status

The Dockerfile, FastAPI service, browser UI parity, health endpoint and
artifact-loading paths are implemented. A public GCP URL and its post-deploy
smoke-test evidence have not yet been added to the saved outputs. The report
therefore describes the system as **GCP deployment-ready**, not already live.

---

# 16. Principal implementation files

| Area | Principal files |
|---|---|
| Configuration | `src/config.py` |
| Dataset loading | `src/dataset_loader.py` |
| Corpus construction | `src/corpus_builder.py` |
| Semantic alignment | `src/semantic_alignment_engine.py` |
| Validation | `src/validation_engine.py` |
| Task and prompt construction | `src/task_builder.py`, `src/prompt_builder.py`, `src/registry.py` |
| RAG-aware prompt and dataset construction | `src/prompt_builder_rag.py`, `src/task_builder_rag.py` |
| RAG-aware response-safe budgeting | `src/response_safe_training_rag.py` |
| Curriculum | `src/curriculum_builder.py` |
| Training | `src/trainer.py`, `src/completion_collator.py` |
| Checkpoints and manifests | `src/checkpoint_manager.py`, `src/artifact_manifest.py` |
| Generation | `src/generation_engine.py`, `src/code_extraction.py` |
| Metrics and comparison | `src/metric_engine.py`, `src/evaluator.py`, `src/comparison_engine.py` |
| Statistical evaluation | `src/statistical_evaluation.py`, `src/rag_policy.py` |
| Stage 4 explorer | `src/repo_explorer/` |
| Repository catalogue | `src/repository_catalog.py` |
| Corpus RAG | `src/corpus_retriever.py` |
| Unified retrieval | `src/retrieval_engine.py` |
| Functional evaluation | `src/functional_execution_eval.py`, `scripts/repocoder_docker_eval.py` |
| Gradio UI and cold restoration | `src/gradio_showcase.py`, `src/gradio_runtime.py` |
| FastAPI and browser UI | `app/main.py`, `app/schemas.py`, `app/static/` |
| Curated demonstrations | `src/demo_showcases.py` |
| Container deployment | `Dockerfile`, `.dockerignore`, `docker-compose.yml` |
| Full-run notebook | `notebooks/RepoCoderStudio_Fast_Corrected_Retrain.ipynb` |
| RAG-aware extension notebook | `notebooks/RepoCoderStudio_RAG_Augmented_Retrain.ipynb` |

---

# 17. Conclusion

RepoCoder Studio progressed from a bilingual fine-tuning experiment into a
completed repository-aware code-generation and evaluation platform through
Stage 5.

The Combined Stage created traceable multilingual data, six explicit task
contracts and a parameter-efficient training pipeline. Stage 4 converted
Python and Java repositories into searchable, dependency-aware evidence. Stage
5 connected that evidence to controlled generation, abstention, provenance and
functional verification.

The corrected full run completed the entire pipeline and produced measurable
improvement. Fine-tuning improved five of six task-primary metrics and
preserved the sixth, including a 45-percentage-point improvement in
Python-to-Java compilation. Stage 4 achieved 97% Recall@5 on LedgerFlow, and
cross-encoder reranking produced the strongest tested retrieval result at
0.980 MRR@5. Stage 5 retrieved the hidden transfer policy as the top source and
made the evidence, score, method and provenance visible to users.

The final RAG-aware extension closed the prompt-contract gap discovered during
UI testing. Its separately versioned v1.2 adapter trained on 2,877 retained
rows and was restored successfully in a fresh runtime. With one complete
repository evidence block, it reproduced the exact LedgerFlow email-validation
behaviour and every checked hidden transfer-policy rule. These outcomes provide
a concrete end-to-end demonstration of the intended design: fine-tuning teaches
the task contract, retrieval supplies private repository knowledge, and the
combined system uses that knowledge in generated code.

The project also produces the artifacts expected of a complete engineering
capstone: an executed notebook, validated datasets, a trained LoRA adapter,
evaluation logs, repository and corpus indexes, an isolated functional-test
harness, Gradio and FastAPI interfaces, and a GCP-ready Docker handoff.

The result is not presented as an autonomous production coding agent. It is a
well-scoped, reproducible and auditable bilingual repository-aware assistant
whose claims are supported by saved evidence. The Combined Stage, Stage 4 and
Stage 5 are complete. The FastAPI container and artifact contract are ready for
GCP deployment; creation and verification of a public Cloud Run endpoint remain
the final operational handoff rather than an unverified claim in this report.
