# Fine-Tuning Overview

## Project Summary

This project fine-tunes the StarCoder2-3B language model using LoRA (Low-Rank Adaptation) for programming tasks involving code generation and code translation between Python and Java.

The fine-tuned model is integrated into the Agentic AI system to improve the quality of generated code relative to the base model.

## Base Model

- Model: `bigcode/starcoder2-3b`
- Architecture: Decoder-only causal language model
- Framework: Hugging Face Transformers
- Fine-tuning method: LoRA (parameter-efficient fine-tuning)
- Trainer: TRL `SFTTrainer`

## Dataset

A custom instruction-following dataset was created from paired Python and Java programs.

The dataset covers four task categories:

- Text → Python code generation
- Text → Java code generation
- Java → Python code translation
- Python → Java code translation

Each sample is converted into an instruction-response format prior to training.

### Example Prompt Format

```python
### Instruction
Write a function to find the largest number in a list.

### Response

def largest_number(nums):
    return max(nums)
```

## Data Preparation

The custom dataset was constructed by combining four source datasets:

- Text → Java
- Text → Python
- Java → Python
- Python → Java

Each sample is formatted into a single training prompt using the following template:

```text
<language>

### Instruction
<instruction>

### Response
<response>
```

## Quantization

To reduce GPU memory consumption during fine-tuning, 4-bit NF4 quantization was used through BitsAndBytes.

### Quantization Configuration

- 4-bit quantization (NF4)
- Double quantization enabled
- Compute data type: `bfloat16`

## LoRA Configuration

| Parameter      |                                  Value |
| -------------- | -------------------------------------: |
| Rank (`r`)     |                                     16 |
| Alpha          |                                     32 |
| Dropout        |                                   0.05 |
| Bias           |                                   None |
| Target Modules | `q_proj`, `k_proj`, `v_proj`, `o_proj` |
| Task Type      |                            `CAUSAL_LM` |

## Training Configuration

| Parameter                   |             Value |
| --------------------------- | ----------------: |
| Epochs                      |                 3 |
| Batch Size                  |                 1 |
| Gradient Accumulation Steps |                16 |
| Effective Batch Size        |                16 |
| Learning Rate               |            `2e-4` |
| Precision                   |            `BF16` |
| Optimizer                   | `AdamW` (default) |
| Checkpoint Saving           |       Every epoch |
| Training Framework          |  TRL `SFTTrainer` |

## Training Pipeline

1. Load the StarCoder2-3B base model.
2. Apply 4-bit quantization using BitsAndBytes.
3. Prepare the custom instruction-following dataset.
4. Configure LoRA adapters for parameter-efficient fine-tuning.
5. Fine-tune using the TRL `SFTTrainer`.
6. Save the LoRA adapter weights and training checkpoints.
7. Export the trained model artifacts as ZIP archives.

## Fine-Tuned Model Capabilities

The fine-tuned model supports:

- Text-to-Python code generation
- Text-to-Java code generation
- Java-to-Python code translation
- Python-to-Java code translation

The fine-tuned model is used by the Generator Agent and Translator Agent within the Agentic AI system, while Groq-hosted LLMs are used for routing, validation, repair, and code explanation.

## Evaluation

The fine-tuned model was evaluated on a custom benchmark using the following metrics:

- Pass@1
- Java compilation rate
- CodeBERT similarity
- AST similarity
- BLEU score
- ROUGE-1
- ROUGE-2
- ROUGE-L
- Composite translation score

The evaluation demonstrated significant improvements over the base StarCoder2-3B model across all supported code generation and translation tasks.
