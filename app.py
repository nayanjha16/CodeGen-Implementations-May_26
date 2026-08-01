import re
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM
from transformers import BitsAndBytesConfig
from peft import PeftModel
from langchain.messages import AIMessage
from langchain_groq import ChatGroq
from pydantic import SecretStr

import torch

from config import HF_TOKEN, STARCODER_BASE_MODEL, QWEN_BASE_MODEL, GROQ_API_KEY, HF_TOKEN
from model_loader import get_starcoder

app = FastAPI()

@app.on_event("startup")
def startup():
    global tokenizer, model
    (tokenizer, model) = get_starcoder()
    

# explain_llm = ChatGroq(
#     model=QWEN_BASE_MODEL,
#     api_key=SecretStr(GROQ_API_KEY),
#     temperature=0.2,
#     max_retries=2    
# )
#ChatPromptTemplate(

class Request(BaseModel):
    query: str
    task: str
    source_language: str
    target_language: str
    source_code: str
    output_code: str    

@app.post("/generate")
def generate(req: Request) -> str:

    prompt_text = f""" 
        Generate the code for the following instruction.
        ### Instruction:
        {req.query}

        ### Response
        """

    result = invoke_model(prompt_text)
    return result
             
@app.post("/translate")
def translate(req: Request) -> str:

    prompt_text = f"""
    {req.source_language} to {req.target_language}
    
    ### Instruction  
    {req.source_code}

    ### Response
    """

    result = invoke_model(prompt_text)
    return result

@app.post("/repair")
def repair(req: Request) -> str:

    prompt_text = f"""
    ### Instruction
    The following code has compilation errors. Please fix and generate the corrected code.
    problem statement for the code: {req.query}

    ### Input
    {req.output_code}
    ### Response
    """
    result = invoke_model(prompt_text)
    return result
    
def invoke_model(prompt_text: str) -> str:
    
    inputs = tokenizer(
        prompt_text,
        return_tensors="pt"
    ).to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=768,
         do_sample=True,
        temperature=0.2,
        top_p=0.95,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id
    )

    result = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    return result.split("### Response")[1].strip()

if __name__ == "__main__":    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")

# def clean_explanation(text: str) -> str:
#     if not text:
#         return ""

#     cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
#     cleaned = re.sub(r"\r\n?", "\n", cleaned)
#     cleaned = re.sub(r"(?i)^\s*(explanation|answer|final answer)\s*[:\-]*\s*", "", cleaned)

#     paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
#     if not paragraphs:
#         return re.sub(r"\s+", " ", cleaned).strip()

#     last_paragraph = paragraphs[-1]
#     return re.sub(r"\s+", " ", last_paragraph).strip()


# @app.post("/explain")
# def explain(req: Request) -> str:
#     prompt_text = f"""
#             Explain the following code in one short paragraph of plain text.
           
#             ### Code
#             {req.output_code}

#             ### Explanation
#             """

#     explain_llm_response = explain_llm.invoke(
#         input=[{"role": "user", "content": prompt_text}]
#     )
    
#     content = explain_llm_response.content
#     if isinstance(content, str):
#         return clean_explanation(content)
#     if isinstance(content, list):
#         cleaned_parts = [
#             clean_explanation(item) if isinstance(item, str) else clean_explanation(str(item))
#             for item in content
#         ]
#         return "\n".join(part for part in cleaned_parts if part)

#     return clean_explanation(str(content))
