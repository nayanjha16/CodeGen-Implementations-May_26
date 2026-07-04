# Group-30 CodeGen Training

This folder contains the training pipeline for fine-tuning Qwen2.5-Coder-7B with LoRA adapters.

## Table of Contents

- [Overview](#overview)
- [Dataset Configuration](#dataset-configuration)
- [Issues Faced and Learnings](#issues-faced-and-learnings)
- [Usage](#usage)
- [Related Files](#related-files)
- [Summary Metrics](#summary-metrics)

## Overview

The training process consists of three main phases:
1. **Baseline Computation** - Establish initial accuracy metrics
2. **LoRA Fine-tuning** - Train adapters for NL→Python and Python→C++ tasks
3. **Validation** - Evaluate the fine-tuned models



## Dataset Configuration

The dataset is split into three equal parts:
- **Baseline**: First `num_records // 3` records
- **LORA Training**: Middle `num_records // 3` records  
- **Validation**: Last `num_records // 3` records

## Issues Faced and Learnings

| Issues Faced | Learnings |
|--------------|-----------|
| Dataset is very important. Lack of Dataset for for PL1 to PL2 for same intent.| Create documentation for PL1 and generate program in PL2. Use PL2 as source for conversion to PL1. Original Pl1 is then ground truth|
| Conversion attempt from Python program in dataset to C++| Python program used packages which has no equivalent in C++. Switched to generate documentation from C++, from that documentation generate Python and then convert this Python to C++ |
| codegen-350m-multi: Generating code gave index out of bounds exceptions. <br>-Reading for exceptions lead to adding hooks to print and limit the position tokens generate. <br> -Tried rope_scaling.<br> -Printed tensors and CUDA:x on which they were. Tensors on CUDA:1 were garbage values. <br> -Tried limiting max_tokens in generate to model.max - input token, add eos and pad token ids which were said to be known issue with codegen <br><br>**Nothing Worked** | used options<br> - CUDA_LAUNCH_BLOCKING to Force CPU to wait for GPU<br> - TORCH_USE_CUDA_DSA to Described debug output from GPU<br> - CUDA_VISIBLE_DEVICES to Force on single GPU (CUDA:0)|
| codegen-350m-multi: The model is code completion. It does not understand NL to convert to PL. Was repeating documentation | Wrong model to work with, switched to Qwen/Qwen2.5-Coder-7B-Instruct|
| Memory constraints with 7B model | Use 4-bit quantization (BitsAndBytes) to reduce VRAM usage from ~14GB to ~4GB |
| Out of Memory when fine tuning | Added code to empty CUDA cache and run garbage collection. Didn't resolve the problem, but it allowed more records to be used|
| Qwen 7B model: Needs large number of records to fine tune, we could do only max 33 records and then hit GPU out of memory| No Solution|
| Dataset streaming slow on HuggingFace | Cache dataset locally to avoid repeated downloads and enable faster iteration |
| Baseline computation, Fine-Tuning and Validation Set| Updated design to create a cached record of N records (command line param) and use N/3 for baseline, N/3 for fine-tuning and N/3 for validation. Added command line option to purge the N record cache|
| Design Issue. Using the Qwen/Qwen2.5-Coder-7B-Instruct to<br>- Generated documentation<br> - Generate Code from documentation to PL<br> -Act as LLM Judge| No solution for using a different model. Constrained by Memory|
| Score threshold tuning | Use 0.3 as threshold for LLM judge to identify poor generations |
| Correctness of code generated from NL. Reading suggested using LLM Judge, _Didn't want to venture into compilation and testing_ | Used Qwen as LLM Judge to measure code against ducumentation on these metrics: <br> -compiles: true/false<br> -logic_correct: true/false<br> -handles_edge_cases true/false<br> -issues: list of issues<br> -Judge verdict correct/incorrect/partially_correct<br> -explanation of code<br> - a final score [0,1]
| Whisper ASR model large download | Load whisper-base instead of larger models for faster startup |
| Code extraction from markdown blocks | Parse with ``` delimiters and detect language tags |
| Dataset record distribution | Ensure consistent split across baseline, LORA, and validation phases |
| DataSet Cache management complexity | Implement automatic cache directory structure with num_records in path |
| LoRA adapter loading conflicts | Use `PeftModel` with multiple adapters and `set_adapter()` for switching |
| CUDA out of memory during training | Reduce batch size, use gradient accumulation|
| Tokenizer padding issues | Set `pad_token_id = eos_token_id` for decoder-only models |
| Multi-GPU device mapping | Use `device_map="auto"` for automatic tensor distribution |



## Usage

```bash
# Run with default 10 records
python codegen_30.py

# Run with 300 records
python codegen_30.py -n 300

# Clean cached dataset and run with 300 records
python codegen_30.py -n 300 -c
```

**Arguments:**
| Argument | Description |
|----------|-------------|
| `-n, --num-records` | Number of records in the dataset (default: 10) |
| `-c, --clean` | Clean the cached dataset before running |

## Related Files

- **Application**: `../Application/app.ipynb` - Web interface using trained adapters
- **Model**: `../model/` - Saved LoRA adapter zip files
- **Architecture**: `../../Architecture/Diagrams.md` - System diagrams

## Summary Metrics