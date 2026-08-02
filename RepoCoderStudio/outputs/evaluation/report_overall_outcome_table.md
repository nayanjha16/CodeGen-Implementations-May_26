### Overall Baseline vs Fine-Tuned Performance

| Task                          | Primary Metric       |   Examples | Baseline   | Fine-Tuned   |    Delta | Observation                              |
|:------------------------------|:---------------------|-----------:|:-----------|:-------------|---------:|:-----------------------------------------|
| T1: Natural Language → Python | Python parse success |         20 | 90.0%      | 100.0%       | 0.1      | Python parse success improved by 0.1000. |
| T2: Natural Language → Java   | Java compile success |         20 | 70.0%      | 85.0%        | 0.15     | Java compile success improved by 0.1500. |
| T3: Python → Java             | Java compile success |         20 | 40.0%      | 85.0%        | 0.45     | Java compile success improved by 0.4500. |
| T4: Java → Python             | Python parse success |         20 | 100.0%     | 100.0%       | 0        | Python parse success was unchanged.      |
| T5: Python → Natural Language | ROUGE-L              |         20 | 0.2168     | 0.3197       | 0.102839 | ROUGE-L improved by 0.1028.              |
| T6: Java → Natural Language   | ROUGE-L              |         20 | 0.2091     | 0.2819       | 0.0728   | ROUGE-L improved by 0.0728.              |