from typing import Any
import re

from click import prompt
from pydantic import SecretStr
from typer import prompt

from state import AgentState
from config import GROQ_API_KEY, QWEN_BASE_MODEL
from langchain.messages import AIMessage
from langchain_groq import ChatGroq


explain_llm = ChatGroq(
    model=QWEN_BASE_MODEL,
    api_key=SecretStr(GROQ_API_KEY),
    temperature=0.2,
    max_retries=2    
)

# def explain(state: AgentState) -> str:
    
#     return explain_code(state["output_code"])


def explain(code: str) -> str:
    prompt_text = f"""
            Explain the following code in one short paragraph of plain text.
           
            ### Code
            {code}

            ### Explanation
            """

    explain_llm_response = explain_llm.invoke(
        input=[{"role": "user", "content": prompt_text}]
    )
    
    content = explain_llm_response.content
    if isinstance(content, str):
        return clean_explanation(content)
    if isinstance(content, list):
        cleaned_parts = [
            clean_explanation(item) if isinstance(item, str) else clean_explanation(str(item))
            for item in content
        ]
        return "\n".join(part for part in cleaned_parts if part)

    return clean_explanation(str(content))


def clean_explanation(text: str) -> str:
    if not text:
        return ""

    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"\r\n?", "\n", cleaned)
    cleaned = re.sub(r"(?i)^\s*(explanation|answer|final answer)\s*[:\-]*\s*", "", cleaned)

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
    if not paragraphs:
        return re.sub(r"\s+", " ", cleaned).strip()

    last_paragraph = paragraphs[-1]
    return re.sub(r"\s+", " ", last_paragraph).strip()