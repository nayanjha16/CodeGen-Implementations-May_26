# CodeGen-Implementations-May_26

Problem statement

Text to Python
Text to Java
Python to Java
Java to Python

Model used: starcoder2-3B

starcoder2 base model is trained for code completion not for following instructions. so we are finetuning it to follow the instructions.

Pass@k evaluation metrics for Python Generation on MBPP data set

Pass@1 for text to python

| Metric             | Value      |
| ------------------ | ---------- |
| Total Solved       | **429**    |
| Total Problems     | **974**    |
| Overall Pass@1     | **0.4405** |
| Overall Pass@1 (%) | **44.05%** |

max_new_tokens=300, do_sample=True, temperature=0.2, top_p=0.95

Pass@10 for text to python

| Metric              | Value      |
| ------------------- | ---------- |
| Total Solved        | **71**     |
| Total Problems      | **100**    |
| Overall Pass@10     | **0.7100** |
| Overall Pass@10 (%) | **71.00%** |

max_new_tokens=300, do_sample=True, temperature=0.7
