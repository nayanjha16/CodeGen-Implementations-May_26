Model used: starcoder2-3B

starcoder2 base model is trained for code completion not for following instructions. so we are finetuning it to follow the instructions.

MBPP is unknown dataset for the finetuned model

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

Custom dataset metrics:

| **Metric**               | **Text → Python (Base)** | **Text → Python (Fine-Tuned)** | **Text → Java (Base)** | **Text → Java (Fine-Tuned)** | **Java → Python (Base)** | **Java → Python (Fine-Tuned)** | **Python → Java (Base)** | **Python → Java (Fine-Tuned)** |
| :----------------------- | :----------------------: | :----------------------------: | :--------------------: | :--------------------------: | :----------------------: | :----------------------------: | :----------------------: | :----------------------------: |
| **Dataset**              |      Custom Dataset      |         Custom Dataset         |     Custom Dataset     |        Custom Dataset        |      Custom Dataset      |         Custom Dataset         |      Custom Dataset      |         Custom Dataset         |
| **Pass@1 (%)**           |         **0.60**         |           **53.01**            |        **0.00**        |          **49.70**           |         **0.90**         |           **65.97**            |         **0.00**         |           **55.72**            |
| **Compilation Rate (%)** |            —             |               —                |           —            |              —               |            —             |               —                |         **1.81**         |           **94.28**            |
| **CodeBERT Similarity**  |        **0.6773**        |           **0.8516**           |       **0.6788**       |          **0.9485**          |        **0.6186**        |           **0.9180**           |        **0.6514**        |           **0.9219**           |
| **AST Similarity**       |        **0.0123**        |           **0.7038**           |       **0.5456**       |          **0.7384**          |        **0.0455**        |           **0.6000**           |        **0.5660**        |           **0.7593**           |
| **BLEU Score**           |        **0.0557**        |           **0.2869**           |       **0.0661**       |          **0.6961**          |        **0.0721**        |           **0.3929**           |        **0.0646**        |           **0.6881**           |
| **ROUGE-1**              |        **0.1909**        |           **0.5473**           |       **0.1728**       |          **0.8026**          |        **0.2153**        |           **0.6262**           |        **0.1932**        |           **0.7884**           |
| **ROUGE-2**              |        **0.0839**        |           **0.3279**           |       **0.0786**       |          **0.7116**          |        **0.1145**        |           **0.4454**           |        **0.0810**        |           **0.6774**           |
| **ROUGE-L**              |        **0.1701**        |           **0.5014**           |       **0.1225**       |          **0.7813**          |        **0.1869**        |           **0.5794**           |        **0.1330**        |           **0.7564**           |
| **Composite Score**      |        **0.2945**        |           **0.6530**           |       **0.4202**       |          **0.8192**          |        **0.2904**        |           **0.6824**           |        **0.4193**        |           **0.8074**           |

Key Improvements for Text → Python
| Metric | Base | Fine-Tuned | Improvement |
| ----------------------- | -----: | ---------: | ---------------------------: |
| **Pass@1** | 0.60% | **53.01%** | **+52.41 percentage points** |
| **AST Similarity** | 0.0123 | **0.7038** | **+0.6915** |
| **CodeBERT Similarity** | 0.6773 | **0.8516** | **+0.1743** |
| **Composite Score** | 0.2945 | **0.6530** | **+0.3585** |

Key Improvements for Text → Java
| Metric | Base | Fine-Tuned | Improvement |
| ----------------------- | -----: | ---------: | ---------------------------: |
| **Pass@1** | 0.00% | **49.70%** | **+49.70 percentage points** |
| **AST Similarity** | 0.5456 | **0.7384** | **+0.1928** |
| **CodeBERT Similarity** | 0.6788 | **0.9485** | **+0.2697** |
| **Composite Score** | 0.4202 | **0.8192** | **+0.3990** |

Key Improvements for Java → Python
| Metric | Base | Fine-Tuned | Improvement |
| ----------------------- | -----: | ---------: | ---------------------------: |
| **Pass@1** | 0.90% | **65.97%** | **+65.07 percentage points** |
| **AST Similarity** | 0.0455 | **0.6000** | **+0.5545** |
| **CodeBERT Similarity** | 0.6186 | **0.9180** | **+0.2994** |
| **Composite Score** | 0.2904 | **0.6824** | **+0.3920** |

Key Improvements for Python → Java
| Metric | Base | Fine-Tuned | Improvement |
| ----------------------- | -----: | ---------: | ---------------------------: |
| **Pass@1** | 0.00% | **55.72%** | **+55.72 percentage points** |
| **Compilation Rate** | 1.81% | **94.28%** | **+92.47 percentage points** |
| **AST Similarity** | 0.5660 | **0.7593** | **+0.1933** |
| **CodeBERT Similarity** | 0.6514 | **0.9219** | **+0.2705** |
| **Composite Score** | 0.4193 | **0.8074** | **+0.3881** |

composite score is calculated as weighted sum of the metrics.

```
composite_score = (
    0.35 * codebert_similarity_score +
    0.25 * ast_similarity_score +
    0.15 * rougeL_score +
    0.10 * rouge1_score +
    0.05 * rouge2_score +
    0.10 * bleu_score
)
```
