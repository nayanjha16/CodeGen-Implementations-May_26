# RustGen

Teach **Salesforce/codegen-350M-multi** to write Rust. The base model scores ~1.3% on Rust
HumanEval; we improve it with three ingredients:

1. a **monolingual Rust corpus** (bigcode/starcoderdata, `rust` subset) used twice — for
   continued pre-training of the base model, and as the **RAG index** queried at inference time;
2. **validated `{English, Python, Rust}` triples** (MBPP translate-and-filter + Rosetta Code)
   used for LoRA fine-tuning, each triple giving an English→Rust and a Python→Rust training view;
3. an **evaluation harness** that compiles generated Rust with `rustc`, runs humaneval-rs test
   suites, and reports pass@1 (training data is MBPP-based, eval is HumanEval-based — disjoint
   by construction).

This repo is the *product*: a library + Gradio demo every workstream plugs into. It runs
**today** with a deterministic mock translator; the real model drops in via one config value.

## Quickstart

```bash
git clone <repo-url> && cd <repo>
pip install -e .            # core deps only (gradio, numpy)
python -m rustgen.app.demo  # launches the Gradio UI with the mock backend
```

Optional extras:

```bash
pip install -e ".[dev]"     # pytest
pip install -e ".[rag]"     # scikit-learn, for the TF-IDF retriever
pip install -e ".[ml]"      # torch/transformers/peft, for the real model
```

Run the tests (the harness test auto-skips if `rustc` is missing):

```bash
pytest
```

Run the eval loop end-to-end against the bundled 2-problem sample (needs `rustc` —
install via [rustup](https://rustup.rs)):

```bash
python -m rustgen.eval.runner --limit 2
```

## Mock → real model: one config change

Everything reads `rustgen.config.Config`. The defaults use the mock backend; to switch to
the fine-tuned model, change the backend (and point at the trained adapter):

```bash
RUSTGEN_BACKEND=hf RUSTGEN_ADAPTER_PATH=models/lora-v1 python -m rustgen.app.demo
```

or in code: `Config(backend="hf", adapter_path="models/lora-v1")`. No other edits — the UI,
eval runner, and RAG plumbing are identical for both backends, and the active backend is
displayed in the demo.

## How the notebooks relate to this repo

Heavy training/eval runs live in Colab notebooks under `notebooks/`. They *produce
artifacts* that drop into the gitignored directories here:

- `data/pairs.jsonl`, `data/rust_corpus.jsonl` — generated/validated training triples and
  the Rust corpus slice (the latter powers `rag_backend="tfidf"`);
- `models/lora-v1/` — LoRA adapters from fine-tuning, referenced by `Config.adapter_path`.

## Layout

```
rustgen/translator/   Translator ABC + mock and HF backends, get_translator(config)
rustgen/rag/          Retriever ABC (mock + TF-IDF) and the single prompt format
rustgen/eval/         rustc compile-and-test harness + pass@1 runner (CLI)
rustgen/app/demo.py   Gradio demo
tests/                pytest suite + 2-problem humaneval-rs-style fixture
```
