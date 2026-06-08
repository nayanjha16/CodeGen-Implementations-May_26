The actions items and discussions between the group members and mentors are documented here.

[06/07/2026] (06-07-2026)


# 06/07/2026
## Notes:
1. Baseline data needs to be created for the model to convert NL->PL1 and PL1->PL2. use the same dataset and generate metrics, use AST similarity too.

1. NL tp PL approach: to use the [bigcode/the-stack-dedu](https://huggingface.co/datasets/bigcode/the-stack-dedup/viewer) dataset of C++ and Python code, generate documentation for it and then use this documentation as in put to the model to generate the code. There needs to be a mechanism to evaluate if the documentation for the code was generated that reduces error in code generation. The approach should be modified to :
    1. Data Set Code -> Model to Generate documentation -> Documentation to mode -> Generated code.
       Data Set Code compared to Generated code for code similarity and AST. Perform this three times, and keep the documentation for the code that generates the highest similarity.
    1. Need AST comparison models from Nayan (@nayanjha16)
    1. Approach: [NL->PL Approach](MentoringNotes/06-07-2026/1.png)

1. For PL1-> PL2 approach [PL1->PL2 Approach](MentoringNotes/06-07-2026/2.png)
    1. There needs to be a mechanism to have NL-> PL1 correctness before having Pl1-> PL2 conversion. Use 3 iterations logic. Else find a dataset which has for the same documentation for NL->PL1 and NL->PL2 or PL1-> PL2 conversion.

## Actions:
1. Team to follow suggested approach of three iterations from generated documentation for code generation.
2. Nayan(@nayanjha16) to provide AST comparator models.

