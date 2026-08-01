import gradio as gr
import torch
import spaces
from transformers import AutoTokenizer, AutoModelForCausalLM
import re
import subprocess

tokenizer = AutoTokenizer.from_pretrained("shibsankardhara2/Qwen2.5-Coder-1.5B-Java-CSharp_V5")
model = AutoModelForCausalLM.from_pretrained("shibsankardhara2/Qwen2.5-Coder-1.5B-Java-CSharp_V5")

def single_function(code):
    beg_count = 0
    end_count = 0
    start = 0
    for n, i in enumerate(code):
        if i == '{':
            beg_count += 1
        elif i == '}':
            end_count += 1
        if beg_count == end_count and beg_count > 0:
            start = n
            break
    if start == 0:
        return code
    return code[:start+1]

def _clean_csharp_output(code: str) -> str:
    """
    Remove spurious `virtual` / `override` modifiers the model adds to bare
    (class-less) method snippets.

    The model was trained on C# methods that usually live inside a class, where
    `public virtual ...` is common. When it translates a *standalone* Java method
    it carries the `virtual` keyword over — but `virtual`/`override` are only
    valid on members of a class, so on a bare snippet they are invalid C#.
    We therefore strip them ONLY when the snippet has no enclosing type
    declaration (class / struct / interface / record / enum).
    """
    if re.search(r"\b(class|struct|interface|record|enum)\b", code):
        return code  # real type present — leave modifiers intact
    # Drop 'virtual'/'override' after an access modifier: 'public virtual int' -> 'public int'.
    code = re.sub(r"\b(public|private|protected|internal)\s+(?:virtual|override)\s+",
                r"\1 ", code)
    # Drop a leading 'virtual'/'override' with no access modifier.
    code = re.sub(r"(^|\n)(\s*)(?:virtual|override)\s+", r"\1\2", code)
    return code

def format_code(code, language="java"):
    extension="java" if language=="java" else "cs"
    result= subprocess.run(
        ["clang-format",f"--assume-filename=file.{extension}", "--style=Google"],
        input=code, capture_output=True, text=True
    )
    return result.stdout if result.returncode == 0 else code

@spaces.GPU
def generate_code(task_type: str, nl_input: str):
    if task_type == "NL to Java" or task_type == "End to End NL to Java to C#":
        prompt = f"### Instruction:\n\n{nl_input} Write the solution in Java with proper indentation.\n\n### Response:\n\n"
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=128, eos_token_id=tokenizer.eos_token_id, pad_token_id=tokenizer.eos_token_id)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True).split("### Response:\n\n")[-1].strip()
        if task_type == "NL to Java":
            output= _clean_csharp_output(response)
            return format_code(output, language="java")
        else:
            prompt = f"### Instruction:\n\nConvert the below Java Code to C# with proper indentation\n\n{single_function(response)}\n\n### Response:\n\n"
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            outputs = model.generate(**inputs, max_new_tokens=128, eos_token_id=tokenizer.eos_token_id, pad_token_id=tokenizer.eos_token_id)
            response = tokenizer.decode(outputs[0], skip_special_tokens=True).split("### Response:\n\n")[-1].strip()
            output= _clean_csharp_output(response)
            return format_code(output, language="cs")
    elif task_type == "Java to C#":
        prompt = f"### Instruction:\n\nConvert the below Java Code to C# with proper indentation\n\n{nl_input}\n\n### Response:\n\n"
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=128, eos_token_id=tokenizer.eos_token_id, pad_token_id=tokenizer.eos_token_id)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True).split("### Response:\n\n")[-1].strip()
        output= _clean_csharp_output(response)
        return format_code(output, language="cs")
    elif task_type=="Generate Documentation":
        prompt = f"### Instruction:\n\nWrite a documentation comment with @param and @return tags for the following method:\n\n{nl_input}\n\n### Response:\n\n/**"
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        output=model.generate(**inputs,max_new_tokens=200, eos_token_id=tokenizer.eos_token_id, pad_token_id=tokenizer.eos_token_id)
        response = tokenizer.decode(output[0], skip_special_tokens=True).split("### Response:\n\n")[-1].strip()
        if not response.startswith("/**"):
            response = "/**" + response
        response = response.split("*/")[0] + "*/" if "*/" in response else response
        response = response.replace("**/", "*/")
        return response
demo = gr.Interface(
    fn=generate_code,
    inputs=[
        gr.Dropdown(label="Select Task", choices=["NL to Java", "Java to C#", "End to End NL to Java to C#", "Generate Documentation"], value="NL to Java"),
        gr.Textbox(label="Input")
    ],
    outputs=gr.Code(label="Generated Code"),
    title="CodeGen NL to Java and Java to C#"
)

demo.launch()