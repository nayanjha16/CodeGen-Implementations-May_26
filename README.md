# CodeGen-Implementations-May_26

## Project Overview

This repository contains the implementation and evaluation pipeline for fine-tuning the StarCoder2-3B model for code generation and translation tasks across Python and Java.

## Directory Structure

| Directory / File                  | Description                                                                                                                                    |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `archive/`                        | Archived notebooks, scripts, and older experiment outputs that were kept for reference.                                                        |
| `checkpoint/`                     | Training checkpoints and saved adapter/model states from fine-tuning runs.                                                                     |
| `datasets/`                       | Custom and benchmark datasets used for instruction tuning and evaluation.                                                                      |
| `evaluation/`                     | Scripts and notebooks used to evaluate generated code using metrics such as Pass@k, compilation rate, AST similarity, and CodeBERT similarity. |
| `finetune/`                       | Fine-tuning scripts, training setup, and model adaptation code.                                                                                |
| `papers/`                         | Research papers or related documentation referenced by the project.                                                                            |
| `benchmark_evaluation_results.md` | Summary of benchmark evaluation outcomes.                                                                                                      |
| `custom_dataset_details.md`       | Notes and metrics related to the custom dataset.                                                                                               |
| `finetune_details.md`             | Detailed summary of the fine-tuning setup, configuration, and results.                                                                         |

## Notes

- The project is centered around LoRA-based parameter-efficient fine-tuning.
- The repository includes both training and evaluation artifacts for code generation and translation workflows.
- The `archive/` folder preserves earlier implementation attempts and experiments.
