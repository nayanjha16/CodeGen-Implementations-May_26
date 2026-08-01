+---------------------------------------------------------------+
| FRONTEND LAYER |
|---------------------------------------------------------------|
| Streamlit Application |
| |
| • User Interface |
| • Prompt Input |
| • Conversation History |
| • Display Generated Code / Translation / Explanation |
hits /router api
+------------------------------+--------------------------------+
|
| REST API Request
v
+---------------------------------------------------------------+
| AGENTIC AI SYSTEM LAYER | entry - /router api
|---------------------------------------------------------------|
| FastAPI + LangGraph Orchestrator |
| |
| • Router Agent - extracts the intent and returns the structred output - hits chatgroq qwen model. extracts the intent even from the previous conversation within the session. exposed as /router fast api for the frontend app|
Supervisor agent - forwards the request to appropriate agent
| • Generator Agent - hits /generate|
| • Translator Agent - hits /translate|
| • Explanation Agent - hits chatgroq qwen model|
| • Compiler - compiles the code - 2 tools for python, java compilation.|
Repair Agent - hits /repair api incase compilation failed |

| • Validation Agent - executes test cases & returns the pass % - 2 tools for python, java execution- each tool hits chatgroq qwen model for testcase generation |
| |
| |
| Controls workflow and maintains conversation state(InMemorySaver) |
integrated with langsmith to see agent flow/calls
+------------------------------+--------------------------------+
|
| Model/API Calls
v
+---------------------------------------------------------------+
| BACKEND FINE-TUNED MODEL LAYER | entry - /generate, /translate, /repair
|---------------------------------------------------------------|
| Fast api + NGROK(custom host name) + collab
| Fine-tuned StarCoder2-3B | the below 3 apis hits the finetuned model
| apis: /generate, /translate, /repair
| Returns generated code, translated code, repair code |
+---------------------------------------------------------------+
