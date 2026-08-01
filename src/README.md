# Qwen2.5-Coder NL → Java → C# Code Generation Pipeline

Production-style refactor of `nl-java-c-final-working-v5.ipynb` into a modular Python
project. Two-stage parameter-efficient fine-tuning (LoRA) on
`unsloth/Qwen2.5-Coder-1.5B-Instruct-bnb-4bit`:

| Stage | Task | Dataset | Adapter |
|-------|------|---------|---------|
| 1 | Natural Language → Java | `code_search_net` (java) | LoRA adapter on the base model |
| 2 | Java → C# | XLCoST / CodeTransOcean / CodeXGLUE (auto-fallback) | separate LoRA adapter |

```
Natural Language --(Stage 1 adapter)--> Java --(Stage 2 adapter)--> C#
```

**Environment:** designed for a single T4 GPU (16 GB VRAM) using 4-bit quantization, FP16,
gradient checkpointing and 8-bit paged optimizers.

## Project structure

```
codegen_pipeline/
├── config/
│   └── config.py                # All hyperparameters and paths (single source of truth)
├── data/
│   ├── dataset.py                # Dataset loading + validation (both stages)
│   ├── preprocessing.py          # Cleaning, dedup, splitting, prompt-column construction
│   └── prompt_templates.py       # Prompt builders shared by training AND inference
├── models/
│   ├── model_loader.py           # Base model + LoRA loading (Unsloth)
│   ├── train_java_model.py       # Stage 1 training pipeline
│   ├── train_translation_model.py # Stage 2 training pipeline
├── inference/
│   └── pipeline.py                # Independent NL -> Java -> C# inference pipeline
├── evaluation/
│   ├── metrics.py                # BLEU, Exact Match
│   ├── codebleu.py                # CodeBLEU, CodeBERTScore
│   ├── compile_validation.py     # Syntax accuracy, AST similarity, compilation rate
│   └── evaluate.py                # Orchestrates predictions + full metric report
├── utils/
│   ├── logger.py                  # Structured logging setup
│   ├── helpers.py                 # Seeding, GPU/memory utilities
│   └── io_utils.py                # HF token retrieval, JSON persistence
├── main.py                        # CLI entry point (train / infer / evaluate)
└── requirements.txt
```

## Setup

```bash
cd codegen_pipeline
pip install -r requirements.txt
```

Run everything from inside `codegen_pipeline/` so the top-level packages
(`config`, `data`, `models`, `inference`, `evaluation`, `utils`) resolve correctly, or add
the folder to `PYTHONPATH`.

## Usage

### Train

```bash
python main.py train --stage 1      # NL -> Java only
python main.py train --stage 2      # Java -> C# only
python main.py train --stage both   # both stages sequentially (default)
```

Each stage saves its LoRA adapter + tokenizer under `CFG.SAVE_DIR`
(`./saved_models/stage1_nl2java_adapter`, `./saved_models/stage2_java2csharp_adapter`).

### Run inference

```bash
python main.py infer "write a function to check if a number is prime"
```

Loads the published fine-tuned models (`CFG.HF_REPO` / `CFG.HF_REPO_STAGE2` by default,
overridable with `--stage1-repo`/`--stage2-repo`) and prints the chained
`{natural_language, java, csharp}` result as JSON.

### Evaluate

```bash
python main.py evaluate
```

Generates predictions on held-out Stage 1 (`code_search_net` test split) and Stage 2
(validation split of the auto-selected Java/C# corpus) samples, then reports:
BLEU, CodeBLEU (+ dataflow-excluded variant), CodeBERTScore, Exact Match, Syntax
Accuracy, AST Similarity and Compilation Rate.

## Configuration

All hyperparameters (LoRA rank/alpha, batch size, learning rate, sample counts, dataset
names, Hugging Face repos, etc.) live in `config/config.py`'s `Config` dataclass. Edit
values there rather than passing scattered flags through the codebase.

## Key refactoring decisions

- **Single prompt-template module** (`data/prompt_templates.py`): the exact same builder
  functions are used for training and inference so the two formats can never drift apart.
- **Inference is fully decoupled from training**: `inference/pipeline.py` only loads
  already fine-tuned/merged models and never imports the training modules.
- **`main.py` is orchestration-only**: it dispatches to `models.train_*`,
  `inference.pipeline`, or `evaluation.evaluate` and contains no domain logic itself.
- `inference/` and `models/` are separate top-level packages so training code can
  evolve without any risk of an inference-time import pulling training deps in.
- **Structured logging replaces ad-hoc `print()` calls** throughout, configured once in
  `utils/logger.py`.
- **Evaluation metrics are split by concern**: general text metrics (`metrics.py`),
  code-similarity metrics (`codebleu.py`), and structural/compilation checks
  (`compile_validation.py`), combined by `evaluate.py`.
- Original notebooks are left in the repository root for reference and are not required
  to run this package.
