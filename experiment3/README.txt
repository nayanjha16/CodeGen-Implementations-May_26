Text-to-SQL Multi-LLM Benchmark
===============================

CodeGen Capstone Project 6 - Task 2. Compares codegen-350M-multi, Qwen3-Coder-30B-A3B,
deepseek-coder-33b, and Codestral-22B on text-to-SQL across zero-shot, one-shot, and
fine-tuned scenarios using Spider and BIRD, with EX/TS/VES/Component-F1/BLEU/BERTScore/
LLM-Judge metrics.


Setup (Apple Silicon)
---------------------

    uv venv --python 3.12 .venv && source .venv/bin/activate
    uv pip install -e ".[dev,mlx]"      # add ",hf" to enable the HuggingFace fallback
    python scripts/setup_data.py        # extracts Spider + BIRD from RawDataset/ (no download)

BIRD full dev (release dev_20240627) ships locally as RawDataset/bird_data.zip;
scripts/setup_data.py extracts it (including the nested dev_databases.zip) to
data/bird/dev_20240627/.

Model cache location
~~~~~~~~~~~~~~~~~~~~~~
Model weights (HuggingFace + MLX) are kept inside the project at models/hf-cache/
(gitignored, ~50 GB) instead of the global ~/.cache/huggingface. text2sql/__init__.py
sets HF_HOME to this path on import, so anything that goes through "import text2sql"
(run_experiments.py, the fine-tune CLI, the test suite) downloads and loads from here
automatically - including the mlx_lm.lora subprocess, which inherits the env var.

If you run a script that loads a model without importing text2sql first, export it
yourself (the in-code default uses setdefault, so a shell value always wins):

    export HF_HOME="$PWD/models/hf-cache"


Run
---

    # single experiment
    python run_experiments.py --model qwen3-coder-30b --scenario zero_shot --dataset spider

    # fine-tune (spider | bird | combined)
    python run_experiments.py --finetune --model qwen3-coder-30b --dataset spider

    # evaluate a fine-tuned model
    python run_experiments.py --model qwen3-coder-30b --scenario finetuned_spider --dataset spider

    # run the whole matrix (resumable) then build the report
    python run_experiments.py --all
    python run_experiments.py --report

Results: results/raw/*.json, results/reports/comparison.csv, results/reports/charts/*.png.
The matrix is 40 evaluations (4 models x 5 scenarios x 2 datasets). experiments/config.yaml
defaults to sample_size: 200 (sample-first); set it to null for full dev sets.


Tests
-----

    pytest                  # fast suite (real-model tests skipped)
    pytest -m needs_model   # real-model smoke tests (downloads weights)


Note: This is an evaluation export. The large artifacts (models/, data/, RawDataset/)
are not included; regenerate the datasets locally with scripts/setup_data.py and the
model weights via the fine-tune commands above. The results/ directory (raw eval JSON,
comparison report, and charts) is included.
