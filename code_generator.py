
from typing import Any
from typing import Any

from state import AgentState, Language, Task
from api_client import generate_code, translate_code, repair_code
from util import get_code_by_task

def generate(state: AgentState) -> str:
    return generate_code(state.user_query)

def translate(state: AgentState) -> str:
    router_output = state.router
    if (
        router_output.source_code is None
        or router_output.source_language is None
        or router_output.target_language is None
    ):
        raise ValueError(
            "Router output must include source_code, source_language, and target_language for translation"
        )
    return translate_code(
        router_output.source_code,
        router_output.source_language,
        router_output.target_language,
    )
    
def repair(state: AgentState) -> str: 
    code_to_repair = get_code_by_task(state)
    
    if code_to_repair is None:
        raise ValueError("No code available for repair.")    
    repair_output = repair_code(code_to_repair)    
    return repair_output