# Change Summary — text2sql-ui-tool (through UI skeleton)

**Date:** 2026-07-16

## Architectural changes

- New Streamlit application under `tool/` with adapter-based tab extensibility
- Inference is FastAPI-only; no local LoRA/torch in tool runtime
- Schema selection via local sentence-transformers embeddings before prompt build

## API changes

- None to existing repo APIs; new HTTP client to hf-deploy `/v1/chat/completions`

## Schema changes

- Local settings file: `tool/.local/settings.json` (gitignored)

## Migration details

- N/A — greenfield under `tool/`
