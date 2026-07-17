---
title: Qwen Multitask Code Assistant
emoji: 🐍
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "5.9.1"
app_file: app.py
pinned: false
license: apache-2.0
models:
  - Saikrishna2511/qwen-multitask
---

# Qwen Multitask Code Assistant

Interactive demo for the multi-task fine-tuned Qwen2.5-Coder-0.5B model.

## Tasks

| Tab | Description |
|-----|-------------|
| **NL → Python** | Generate Python from a natural language description |
| **Java → Python** | Translate Java source code to Python |
| **Code → Documentation** | Generate documentation for Python code |

## Configuration

Set the **`MODEL_ID`** repository variable in Space Settings to your uploaded model, e.g.:

```
Saikrishna2511/qwen-multitask
```

The deploy script sets this automatically. If unset, the Space loads `Saikrishna2511/qwen-multitask` by default.

## Model

Upload the merged checkpoint with:

```bash
python scripts/upload_model_to_hf.py \
  --repo-id Saikrishna2511/qwen-multitask \
  --space-id Saikrishna2511/qwen-multitask-demo \
  --create-repo
```

Model card: [Saikrishna2511/qwen-multitask](https://huggingface.co/Saikrishna2511/qwen-multitask)

## Hardware

- **CPU (free):** works but slow (~30–60s per request)
- **GPU T4 (recommended):** ~2–5s per request
