### Table: Failure Analytics Summary

| Task   | Baseline Main Failure   | Fine-Tuned Main Failure   | Observation                                                                                                            |
|:-------|:------------------------|:--------------------------|:-----------------------------------------------------------------------------------------------------------------------|
| T1     | low_similarity          | None observed             | Fine-tuning removed baseline empty-code and low-similarity failures, leading to fully parseable Python outputs.        |
| T2     | None observed           | java_compile_error        | Java compile failures reduced substantially after fine-tuning; remaining errors are mostly syntax-level issues.        |
| T3     | low_similarity          | java_compile_error        | Translation fidelity improved strongly, but some Java compilation failures remain, motivating lightweight Java repair. |
| T4     | None observed           | python_syntax_error       | Java-to-Python translation remained stable with only isolated syntax failure.                                          |
| T5     | None observed           | None observed             | Explanation outputs became closer to reference task descriptions.                                                      |
| T6     | None observed           | None observed             | Java explanation quality improved, with no major failure mode observed.                                                |