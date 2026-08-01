from gettext import translation
from os import stat
from typing import Any
from langgraph.graph import END, START, MessagesState
from langgraph.graph import StateGraph
from code_generator import generate, translate, repair
from code_explanation import explain
from state import AgentState, Language, Task
from router import invoke_router
from compiler_agent import compile_code
from python_validation_agent import  validate_python_code
from java_validation_agent import validate_java_code
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage
from util import get_code_by_task

def generator_node(state: AgentState) -> dict[str, Any]:
    gencode = generate(state)    
    return {
        "generated_code": gencode,
        "messages": [
            AIMessage(content=gencode)
        ]
    }

def translation_node(state: AgentState) -> dict[str, Any]:
    trnscode = translate(state)    
    return {
        "translated_code": trnscode,
        "messages": [
            AIMessage(content=trnscode)
        ]
    }

def explain_node(state: AgentState) -> dict[str, Any]:
    code = None
    if state.router.task == Task.GENERATE:
        code = state.generated_code
    elif state.router.task == Task.TRANSLATE:
        code = state.translated_code     
    else:
        code = state.router.source_code
    
    if code is None:
        print(f"task: {state.router.task}, generated_code: {state.generated_code}, translated_code: {state.translated_code}, source_code: {state.router.source_code}")
        raise ValueError("No code available for explanation.")
     
    explanation = explain(code)
    return {
        "explanation": explanation,
        "messages": [
            AIMessage(content=explanation)
        ]
    }
    
def router_node(state: AgentState) -> dict[str, Any]:
    router_output = invoke_router(state)
    
    return {
        "router": router_output
    }

def supervisor_node(state: AgentState) -> dict[str, Any]:
    return {}

def compiler_node(state: AgentState) -> dict[str, Any]:
    # return {
    #     "compilation_success": True,
    #     "compiler_error": None
    # }
    compilation_success = compile_code(state)

    return {
        "compilation_success": compilation_success,
        "compiler_error": None if compilation_success else "Compilation failed."
    }

def repair_node(state: AgentState) -> dict[str, Any]:
    repair_output = repair(state)
    if state.router.task == Task.TRANSLATE:
        translated_code = repair_output
        return {
            "translated_code": translated_code,
            "repair_attempts": state.repair_attempts + 1
        }
    elif state.router.task == Task.GENERATE:
        generated_code = repair_output
        return {
            "generated_code": generated_code,
            "repair_attempts": state.repair_attempts + 1
        }
    
    return {}

def validation_node(state: AgentState) -> dict[str, Any]:
    code = get_code_by_task(state)
    if code is None:
        raise ValueError("No code available for validation.")
    target_language = state.router.target_language
    if target_language == Language.JAVA:
        pass_percentage = validate_java_code(state.user_query, code)
    else:
        pass_percentage = validate_python_code(state.user_query, code)
    return {"pass_percentage": pass_percentage}

def supervisor_router(state):

    task = state.router.task

    if task == Task.TRANSLATE:
        return "translation"

    elif task == Task.GENERATE:
        return "generation"

    elif task == Task.EXPLAIN:
        return "explanation"

    else:
        return "end"


MAX_REPAIR_ATTEMPTS = 1    
def compiler_router(state: AgentState) -> str:
    # if state.compilation_success is False and state.repair_attempts < MAX_REPAIR_ATTEMPTS:
    #     return "repair"
    #return "success"
    if state.compilation_success:
        return "success"

    if state.repair_attempts < MAX_REPAIR_ATTEMPTS:
        return "repair"

    return "failed"
    
builder = StateGraph(AgentState)

builder.add_node("router", router_node)

builder.add_node("supervisor", supervisor_node)

builder.add_node("translation", translation_node)

builder.add_node("generation", generator_node)

builder.add_node("compiler", compiler_node)

builder.add_node("repair", repair_node)

builder.add_node("validation", validation_node)

builder.add_node("explanation", explain_node)

builder.set_entry_point("router")

builder.add_edge("router", "supervisor")

builder.add_conditional_edges(
    "supervisor",
    supervisor_router,
    {
        "translation": "translation",
        "generation": "generation",
        "explanation": "explanation",
        "end": END
    }
)

builder.add_edge("generation", "compiler")

builder.add_edge("translation", "compiler")

builder.add_conditional_edges("compiler",
    compiler_router,
    {
        "success": "validation",
        "repair": "repair",
        "failed": "explanation"
    }
)

builder.add_edge("repair", "compiler")

builder.add_edge("validation", "explanation")

builder.add_edge("explanation", END)

memory = InMemorySaver()
graph  = builder.compile(checkpointer=memory)

print(graph.get_graph().draw_mermaid())

png = graph.get_graph().draw_mermaid_png()

with open("graph.png", "wb") as f:
    f.write(png)

def invoke_graph(state: AgentState) ->AgentState:
    response = graph.invoke(state, config={
        "configurable": {
            "thread_id": state.thread_id
        }
    })
    return response