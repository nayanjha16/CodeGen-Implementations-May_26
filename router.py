from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from typing import Optional
from langchain_groq import ChatGroq
from pydantic import BaseModel, SecretStr
import json
from state import AgentState, RouterOutput
from config import QWEN_BASE_MODEL, GROQ_API_KEY
import json
import re
         
router_llm = ChatGroq(
    model=QWEN_BASE_MODEL,
    api_key=SecretStr(GROQ_API_KEY),
    temperature=0.2,
    max_retries=2,
    reasoning_effort="none"
)

router_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an expert AI Router for a Code Assistant.

Your job is ONLY to classify the user's request and extract structured information.

You are NOT a programming assistant.

You are ONLY a classifier.

Never solve the user's request.
Never generate code.
Never explain code.
Never summarize code.
Never answer the user's programming question.

Your only job is to return one JSON object.

If you start generating code, you have failed your task.

The conversation history is provided below. Use it to understand references such as:
- it
- this
- previous code
- above code
- generated code
- translated code
- optimize it
- explain it
- convert it

If the latest user message refers to a previous code snippet, infer the intent using the conversation history.

IMPORTANT RULES:

1. Return ONLY a valid JSON object.
2. Do NOT explain your reasoning.
3. Do NOT include <think> tags.
4. Do NOT include markdown.
5. Never invent field names.
6. If information is missing, return null.
7. Use ONLY the allowed values below.

Allowed task values:
- generate
- translate
- explain
- unknown

Allowed programming languages:
- python
- java

Classification rules:

1. If the user wants code from a problem statement:
   task = "generate"

2. If the user wants to convert code between languages:
   task = "translate"

3. If the user wants an explanation:
   task = "explain"

5. Otherwise:
   task = "unknown"

Examples:

User:
Write Java code to add two numbers.

Output:
{{
    "task":"generate",
    "source_language":null,
    "target_language":"java",
    "problem_statement":"Write Java code to add two numbers.",
    "source_code":null
}}

User:
Convert this Python code to Java.

<python code>

Output:
{{
    "task":"translate",
    "source_language":"python",
    "target_language":"java",
    "problem_statement":"Convert this Python code to Java.",
    "source_code":"<python code>"
}}

User:
Explain this Java code.

<java code>

Output:
{{
    "task":"explain",
    "source_language":"java",
    "target_language":null,
    "problem_statement":"Explain this Java code.",
    "source_code":"<java code>"
}}

Return EXACTLY this schema:

{{
    "task":"",
    "source_language":null,
    "target_language":null,
    "problem_statement":null,
    "source_code":null
}}

"""
        ),

        MessagesPlaceholder(variable_name="history"),

        (
            "human",
            "{user_query}"
        )
    ]
)

#structured_router_llm = router_llm.bind_tools([RouterOutput], tool_choice="RouterOutput")
#structured_router_llm = router_llm.with_structured_output(RouterOutput)

def invoke_router(state: AgentState) -> RouterOutput:
    """
    Invoke the router LLM to determine the intent and relevant information from the user query.

    Args:
        state (AgentState): The agent state containing the user's query.
    Returns:
        RouterOutput: The structured output containing the intent and relevant information.
    """
    user_query = state.user_query
    response = router_llm.invoke(
        router_prompt.format_messages(
            history=state.messages,
            user_query=user_query
        )
    )
    
    # Extract JSON from response (robust to surrounding text or <think> tags)
    response_text = str(response.content).strip()
    print(f"Router LLM response: {response_text}")

    if not response_text:
        raise ValueError("Router LLM returned empty response")

    # def _extract_first_json_object(s: str) -> str:
    #     start = s.find("{")
    #     if start == -1:
    #         raise ValueError("No JSON object found in response")
    #     depth = 0
    #     in_string = False
    #     escape = False
    #     for i in range(start, len(s)):
    #         ch = s[i]
    #         if ch == '"' and not escape:
    #             in_string = not in_string
    #         if ch == '\\' and not escape:
    #             escape = True
    #             continue
    #         else:
    #             escape = False
    #         if in_string:
    #             continue
    #         if ch == '{':
    #             depth += 1
    #         elif ch == '}':
    #             depth -= 1
    #             if depth == 0:
    #                 return s[start:i+1]
    #     raise ValueError("Unbalanced JSON braces in response")

    # try:
    #     json_text = _extract_first_json_object(response_text)
    # except ValueError as e:
    #     print(f"Failed to extract JSON from response: {response_text}")
    #     raise

    # try:
    #     json_data = json.loads(json_text)
    # except json.JSONDecodeError as e:
    #     print(f"Failed to parse extracted JSON: {json_text}")
    #     raise ValueError(f"Router LLM did not return valid JSON: {e}")
         
    def _extract_json(s: str) -> dict:
        """
        Extract the first valid JSON object from an LLM response.

        Handles:
        - <think>...</think>
        - ```json ... ```
        - Explanatory text before/after JSON
        - Multiple brace blocks
        """

        if not s:
            raise ValueError("Empty router response")

        # Remove reasoning blocks
        s = re.sub(r"<think>.*?</think>", "", s, flags=re.DOTALL | re.IGNORECASE)

        # Remove markdown fences
        s = re.sub(r"```json", "", s, flags=re.IGNORECASE)
        s = re.sub(r"```", "", s)

        decoder = json.JSONDecoder()

        i = 0
        while i < len(s):
            if s[i] != "{":
                i += 1
                continue

            try:
                obj, end = decoder.raw_decode(s[i:])
                return obj
            except json.JSONDecodeError:
                i += 1

        raise ValueError(
            f"No valid JSON object found.\n\nRouter response:\n{s}"
        )
    
    try:
        json_data = _extract_json(response_text)
    except Exception as e:
        print("Router raw response:\n", response_text)
        raise ValueError(f"Router LLM did not return valid JSON: {e}")
    
    return RouterOutput.model_validate(json_data)


