### Table: Overall Baseline vs Fine-Tuned Performance Across Tasks

| Task                          | Baseline   | Fine-Tuned   | Observation                                                                                                                             |
|:------------------------------|:-----------|:-------------|:----------------------------------------------------------------------------------------------------------------------------------------|
| T1: Natural Language → Python | 70%        | 100%         | Significant improvement in executable Python generation; Python parse success reached 100%.                                             |
| T2: Natural Language → Java   | 40%        | 80%          | Java compilation success doubled after fine-tuning, with corresponding improvements in CodeBLEU-lite and CSR.                           |
| T3: Python → Java             | 50%        | 50%          | Primary compilation success remained unchanged, but translation quality improved substantially because CodeBLEU-lite and CSR increased. |
| T4: Java → Python             | 90%        | 90%          | Primary success remained stable while translation quality improved, showing refinement without regression.                              |
| T5: Python → Natural Language | Improved   | Improved     | ROUGE-L, SacreBLEU, and semantic similarity all increased, producing clearer program explanations.                                      |
| T6: Java → Natural Language   | Improved   | Improved     | Consistent improvements across all text-generation metrics, indicating better natural language summarization of Java programs.          |