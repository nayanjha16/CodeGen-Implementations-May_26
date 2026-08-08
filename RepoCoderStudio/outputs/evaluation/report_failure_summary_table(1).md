### Failure Analytics Summary

| Task   | Baseline Main Failure   |   Baseline Failure Rate | Fine-Tuned Main Failure   |   Fine-Tuned Failure Rate |   Failure-Rate Delta | Observation                      |
|:-------|:------------------------|------------------------:|:--------------------------|--------------------------:|---------------------:|:---------------------------------|
| T1     | low_similarity          |                    0.45 | low_similarity            |                      0.1  |                -0.35 | Failure rate decreased by 35.0%. |
| T2     | java_compile_error      |                    0.4  | java_compile_error        |                      0.15 |                -0.25 | Failure rate decreased by 25.0%. |
| T3     | java_compile_error      |                    0.7  | java_compile_error        |                      0.15 |                -0.55 | Failure rate decreased by 55.0%. |
| T4     | low_similarity          |                    0.15 | low_similarity            |                      0.1  |                -0.05 | Failure rate decreased by 5.0%.  |
| T5     | None observed           |                    0    | None observed             |                      0    |                 0    | Failure rate was unchanged.      |
| T6     | None observed           |                    0    | None observed             |                      0    |                 0    | Failure rate was unchanged.      |