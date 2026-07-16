# CodeGen-Implementations-May_26

Problem statement

Text to Python

Text to Java

Python to Java

Java to Python

Model used: starcoder2-3B

starcoder2 base model is trained for code completion not for following instructions. so we are finetuning it to follow the instructions.

Original Dataset java, python translation pairs: Mean AST Similarity Score: 0.5424

original java compilation rate: 100%

-----------------------------------------------Text to Python--------------------------------------------------------------------

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

---

| Metric                    | Text → Python  |  Text → Java   | Java → Python  | Python → Java  |
| :------------------------ | :------------: | :------------: | :------------: | :------------: |
| **Dataset**               | Custom Dataset | Custom Dataset | Custom Dataset | Custom Dataset |
| **Pass@1**                |   **53.01%**   |   **49.70%**   |       —        |       —        |
| **Java Compilation Rate** |       —        |       —        |       —        |   **91.87%**   |
| **CodeBERT Similarity**   |   **0.8516**   |   **0.9485**   |     0.9180     |     0.8809     |
| **AST Similarity**        |   **0.7038**   |   **0.7384**   |     0.6000     |   **0.7487**   |
| **BLEU Score**            |   **0.2869**   |   **0.6961**   |     0.3929     |     0.5319     |
| **ROUGE-1**               |   **0.5473**   |   **0.8026**   |     0.6262     |     0.6620     |
| **ROUGE-2**               |   **0.3279**   |   **0.7116**   |     0.4454     |     0.4809     |
| **ROUGE-L**               |   **0.5014**   |   **0.7813**   |     0.5794     |     0.6052     |
| **Composite Score**       |   **0.6530**   |   **0.8192**   |     0.6824     |     0.7297     |

--------------------------------------------Text to Java----------------------------------------------------------------------

evaluated on custom dataset

Pass@1: 49.70%

Mean AST Similarity Score (Text-to-Java): 0.7384

Mean BLEU Score (Text-to-Java): 0.6961

Mean ROUGE-1 Score (Text-to-Java): 0.8026

Mean ROUGE-2 Score (Text-to-Java): 0.7116

Mean ROUGE-L Score (Text-to-Java): 0.7813

Mean CodeBERT Similarity Score (Text-to-Java): 0.9485

Mean Text to Java Translation Score: 0.8192

--------------------------------------------Java to Python-----------------------------------------------------------------

evaluated on custom dataset

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

evaluated on custom dataset

Java Compilation Rate: 91.87%

Mean Python to Java CodeBERT Similarity Score: 0.8809

Mean Python to Java AST Similarity Score: 0.7487

Mean Python to Java ROUGE-L Score: 0.6052

Mean Python to Java ROUGE-1 Score: 0.6620

Mean Python to Java ROUGE-2 Score: 0.4809

Mean Python to Java BLEU Score: 0.5319

Mean Python to Java Composite Translation Score: 0.7297

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
