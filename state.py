from typing import Optional
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class RouterInput(BaseModel):
    user_query:  str
    thread_id: Optional[str] = None

class Task(str, Enum):
    GENERATE = "generate"
    TRANSLATE = "translate"
    EXPLAIN = "explain"    
    UNKNOWN = "unknown"

class Language(str, Enum):
    JAVA = "java"
    PYTHON = "python"

class RouterOutput(BaseModel):
    task: Task
    source_language: Optional[Language] = None
    target_language: Optional[Language] = None
    source_code: Optional[str] = None
    problem_statement: Optional[str] = None
    
class AgentState(BaseModel):

    messages: Annotated[list[BaseMessage], add_messages]
    
    thread_id: Optional[str] = None
    # Original user query
    user_query: str

    # Router output
    router: RouterOutput = RouterOutput(
        task=Task.UNKNOWN,
        source_language=None,
        target_language=None,
        source_code=None,
        problem_statement=None
    )

    # Outputs from downstream agents
    translated_code: Optional[str] = None

    generated_code: Optional[str] = None

    explanation: Optional[str] = None

    compilation_success: Optional[bool] = None

    compiler_error: Optional[str] = None
    
    pass_percentage: Optional[float] = None

    evaluation: Optional[dict] = None
    
    repair_attempts: int