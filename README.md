# CodeGen-Implementations-May_26

Problem statement

Text to Python

Text to Java

Python to Java

Java to Python

Model used: starcoder2-3B

starcoder2 base model is trained for code completion not for following instructions. so we are finetuning it to follow the instructions.
Original Dataset java, python translation pairs: Mean AST Similarity Score: 0.5424

---------------------------------------------Text to Python----------------------------------------------------------------------

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

--------------------------------------------Java to Python-----------------------------------------------------------------

After finetuning

java to python translation scores:

Mean CodeBERT Similarity Score: 0.9180

Mean AST Similarity Score: 0.6000

Mean ROUGE-L Score: 0.5794

Mean ROUGE-1 Score: 0.6262

Mean ROUGE-2 Score: 0.4454

Mean BLEU Score: 0.3929

Mean composite Translation Score: 0.6824

The `translation_score` is calculated using the following weighted sum:

```
translation_score = (
    0.35 * codebert_similarity_score +
    0.25 * ast_similarity_score +
    0.15 * rougeL_score +
    0.10 * rouge1_score +
    0.05 * rouge2_score +
    0.10 * bleu_score
)
```

--------------------------------------------Python to Java-----------------------------------------------------------------------

Mean Python to Java CodeBERT Similarity Score: 0.8797

Mean Python to Java AST Similarity Score: 0.7011

Mean Python to Java ROUGE-L Score: 0.5929

Mean Python to Java ROUGE-1 Score: 0.6503

Mean Python to Java ROUGE-2 Score: 0.4695

Mean Python to Java BLEU Score: 0.5161

Generated Java Compilation Rate: 70.48%

Mean Python to Java Translation Score: 0.7122

The `translation_score` is calculated using the following weighted sum:

```
translation_score = (
    0.35 * codebert_similarity_score +
    0.25 * ast_similarity_score +
    0.15 * rougeL_score +
    0.10 * rouge1_score +
    0.05 * rouge2_score +
    0.10 * bleu_score
)
```
