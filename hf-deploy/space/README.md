---
title: CodeGen Multi-Adapter API
emoji: 🧩
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: OpenAI-compatible multi-LoRA CodeGen API (text2sql / sql2nosql / nosql2doc)
---

# CodeGen Multi-Adapter API

OpenAI-compatible FastAPI gateway that:

1. Classifies user intent from natural language
2. Hot-swaps the matching LoRA adapter
3. Generates with `Salesforce/codegen-350M-multi`

## Adapters

- [care2achieve/codegen-350M-text2sql-lora](https://huggingface.co/care2achieve/codegen-350M-text2sql-lora)
- [care2achieve/codegen-350M-sql2nosql-lora](https://huggingface.co/care2achieve/codegen-350M-sql2nosql-lora)
- [care2achieve/codegen-350M-nosql2doc-lora](https://huggingface.co/care2achieve/codegen-350M-nosql2doc-lora)

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/health` | Load status |
| GET | `/v1/models` | Model list |
| POST | `/v1/chat/completions` | OpenAI-compatible chat |

## Cursor / client

- Base URL: `https://care2achieve-codegen-multi-adapter.hf.space/v1`
- Model: `codegen-multi-adapter`

Include schema in the user message. One task per request.

## Example

```bash
curl https://care2achieve-codegen-multi-adapter.hf.space/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "codegen-multi-adapter",
    "messages": [
      {
        "role": "user",
        "content": "Write a SQL query to list customer names.\n\nSchema:\ncustomers(id, name)\n\nSQL:"
      }
    ]
  }'
```

Cold start on CPU can take several minutes while the base model and adapters download.
