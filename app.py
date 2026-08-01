from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typer import prompt
from router import RouterOutput, invoke_router
from typing import Optional
from codegen_agent import invoke_graph
from state import AgentState, RouterInput
import uvicorn
from langchain_core.messages import HumanMessage

app = FastAPI()

@app.post("/router")
def translate(input: RouterInput) -> AgentState:
    if input.user_query is None:
        raise HTTPException(status_code=400, detail="user_query is required")
    
    state = prepare_state(input.user_query, input.thread_id)
        
    return invoke_graph(state)

def prepare_state(user_query: str, thread_id: Optional[str] = None) -> AgentState:
    """
    Prepare the initial state for the agent based on the user query.

    Args:
        user_query (str): The user's query.
        
    Returns:
        AgentState: The initial state of the agent.
    """    
    return AgentState(user_query=user_query,
                      thread_id=thread_id, 
                      messages=[HumanMessage(content=user_query)], 
                      repair_attempts=0)

# from groq import Groq

#     client = Groq(api_key="")

#     models = client.models.list()

#     for model in models.data:
#         print(model.id)

if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")