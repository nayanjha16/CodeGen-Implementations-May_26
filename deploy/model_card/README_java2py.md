---
license: apache-2.0
base_model: Qwen/Qwen2.5-Coder-0.5B-Instruct
tags:
  - code-generation
  - qwen2
  - java2python
  - code-translation
library_name: transformers
pipeline_tag: text-generation
---

# {repo_id}

Java→Python fine-tuned **Qwen2.5-Coder-0.5B-Instruct** checkpoint (Stage 1 LoRA, merged for inference).

## Demo

Related multi-task demo: [{space_url}]({space_url})

## Task

### Java → Python (`java2py`)

```
### Translate Java to Python:
```java
{java code}
```
### Python:
```python
```

## Training

- **Base model:** [Qwen/Qwen2.5-Coder-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct)
- **Data:** AVATAR-TC / Java→Python pairs
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

java = "public class Hello { public static void main(String[] args) { System.out.println(\"hi\"); } }"
prompt = f"### Translate Java to Python:\\n```java\\n{java}\\n```\\n### Python:\\n```python\\n"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.2, top_p=0.95)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## Limitations

- Small 0.5B model; translation quality varies with input complexity
- Prefer the multi-task checkpoint for NL→Python / Code2Doc: [Saikrishna2511/qwen-multitask](https://huggingface.co/Saikrishna2511/qwen-multitask)
- Not intended for production use without further evaluation
