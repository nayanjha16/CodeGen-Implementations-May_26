---
license: apache-2.0
base_model: Qwen/Qwen2.5-Coder-0.5B-Instruct
tags:
  - code-generation
  - qwen2
  - nl2python
  - java2python
  - code2doc
  - multitask
library_name: transformers
pipeline_tag: text-generation
---

# {repo_id}

Multi-task fine-tuned **Qwen2.5-Coder-0.5B-Instruct** checkpoint for code generation and documentation.

## Demo

Try the model in the browser: [{space_url}]({space_url})

## Tasks

This single checkpoint handles three tasks via different prompt prefixes:

### NL → Python (`nl2py`)

```
### Instruction: Write Python for: {natural language description}
### Response:
```

### Java → Python (`java2py`)

```
### Translate Java to Python:
```java
{java code}
```
### Python:
```python
```

### Code → Documentation (`code2doc`)

```
### Generate documentation for this Python code:
```python
{python code}
```
### Documentation:
```

## Training

- **Base model:** [Qwen/Qwen2.5-Coder-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct)
- **Stage 1:** Java→Python LoRA fine-tune on AVATAR-TC
- **Stage 2:** Multi-task LoRA on NL2Py, Code2Doc, code comments, and Java2Py replay
- **Method:** LoRA (r=16, alpha=32), merged weights for inference

## Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_id = "{repo_id}"
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    torch_dtype=torch.float16,
    device_map="auto",
)

prompt = "### Instruction: Write Python for: return the factorial of n\n### Response:\n"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.2, top_p=0.95)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

For post-processing and all three task templates, see the [project repo](https://github.com) or the linked Gradio Space.

## Limitations

- Small 0.5B model; quality varies by task and input complexity
- Trained primarily on Python; Java translation quality depends on training coverage
- Not intended for production use without further evaluation
