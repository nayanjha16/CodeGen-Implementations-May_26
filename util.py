from state import AgentState, Task
from typing import Optional

def get_code_by_task(state: AgentState) -> Optional[str]:
    code = None
    if state.router.task == Task.GENERATE:
        code = state.generated_code
    elif state.router.task == Task.TRANSLATE:
        code = state.translated_code
    
    return code