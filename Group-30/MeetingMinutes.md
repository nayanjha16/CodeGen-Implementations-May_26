The actions items and discussions between the group members and mentors are documented here.

- [07/04/2026](#07042026)
- [06/27/2026](#06272026)
- [06/13/2026](#06122026)
- [06/07/2026](#06072026)


***
**Detailed Notes**

> # 07/04/2026
> 1. Team demonstrated the completed work along with details of fine tuning and User Interface that uses ASR for prompting for NL->PL
> 1. Nayan Suggested to:
>    - See how relative scoring and be improved
>    - Incorporate design patterns
>    - Decouple syntax and semantics training
>    - What inputs we can borrow om Facebook paper or the first paper that was shared
> ## Actions
> 1. See how relative scoring and be improved
> 2. Incorporate design patterns
> 3. Decouple syntax and semantics training
> 4. What inputs we can borrow om Facebook paper or the first paper that was 
---
---
> # 06/27/2026
> 1. The codgen-350m-multi is code completion model. It does not correctly generate the code from the Natural Language description. It is repeating the documentation as code.
> 1. Pawan Suggested to:
>    - change the prompt from Natural Language to more semantic, or AST type prompt.
>    - Use a different model instead of using codegen-350m-multi
> ## Actions
> 1. Change prompt to be more AST type. <span style="color:green">[ Changed prompt to be more pseudo code,function names, param names, logic inside functions. codegen was still many a times repeating prompt. Abandoned since this was not working and also this kid of prompt is hard for humans to give. ]</span>: Closed
> 1. Use different model. <span style="color:green">[ Changed model to use _Qwen/Qwen2.5-Coder-7B-Instruct_ instead of _codgen-350m-multi_]</span>: Closed
---
---
> # 06/13/2026
> ## Notes:
> 1. Code was updated to run the code-> To determine the best documentation, generate documentation three times and for each iteration compute AST match and GraphCodeBERTScore (both averaged) between ground truth program and program generated using the documentation.
> 1. ASTs were compared using node similarity.
> 1. The Python's documentation (NL) to PL1 (C++). The current approach is flawed. There is no check or guarantees that the generated C++ Code is of some quality. The measure of quality is not defined. With this undefined input, the generated python code can be anything. To get around, find a dataset, that has C++ and python code for the same intent, better if it has the documentation for the two too. But there needs to be python and its C++ code for the ground truth. Alternatively, generate test cases for the C++ and Python code and then execute both to check that the output is same. The limitation could be how complex the code output is.
>
> ## Actions
> 1. Find a dataset that has python and C++ for the same intent.
> 1. create diagram for easy reference in discussions. Closed, added [Diagrams](#Architecture/Diagrams.md)

---
---
> # 06/07/2026
> ## Notes:
> 1. Baseline data needs to be created for the model to convert NL->PL1 and PL1->PL2. use the same dataset and generate metrics, use AST similarity too.
>
> 1. NL tp PL approach: to use the [bigcode/the-stack-dedu](https://huggingface.co/datasets/bigcode/the-stack-dedup/viewer) dataset of C++ and Python code, generate documentation for it and then use this documentation as in put to the model to generate the code. There needs to be a mechanism to evaluate if the documentation for the code was generated that reduces error in code generation. The approach should be modified to :
    1. Data Set Code -> Model to Generate documentation -> Documentation to mode -> Generated code.
       Data Set Code compared to Generated code for code similarity and AST. Perform this three times, and keep the documentation for the code that generates the highest similarity.
    1. Need AST comparison models from Nayan (@nayanjha16)
    1. Approach: [NL->PL Approach](MentoringNotes/06-07-2026/1.png)
>
> 1. For PL1-> PL2 approach [PL1->PL2 Approach](MentoringNotes/06-07-2026/2.png)
    1. There needs to be a mechanism to have NL-> PL1 correctness before having Pl1-> PL2 conversion. Use 3 iterations logic. Else find a dataset which has for the same documentation for NL->PL1 and NL->PL2 or PL1-> PL2 conversion.
>
> ## Actions:
> 1. Team to follow suggested approach of three iterations from generated > documentation for code generation. <span style="color:green">[ Closed on 06/12/2026 ]</span>
> 2. Nayan(@nayanjha16) to provide AST comparator models. <span style="color:green">[ Obsolete by use of node similarity for AST comparison ]</span>: Closed
