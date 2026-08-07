from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.onprem.compute import Server
from diagrams.onprem.container import Docker
from diagrams.onprem.database import PostgreSQL
from diagrams.programming.language import Python, Java
from diagrams.custom import Custom
from diagrams.onprem.network import Nginx

with Diagram("LangGraph Agent Architecture", show=False, filename="architecture_diagram"):
    user = User("User / API")
    
    with Cluster("LangGraph Pipeline"):
        router = Server("Router Node")
        
        with Cluster("Generation"):
            codegen = Server("Qwen2.5-0.5B\n(Codegen)")
            rag = Server("RAG Index\n(Optional)")
            
        with Cluster("Execution & Fix"):
            sandbox = Docker("Docker Sandbox")
            judge = Server("LLM Judge")
            fixer = Server("AST Fixer")
            
    user >> Edge(label="Prompt (NL/Java)") >> router
    router >> Edge(label="Route Task") >> codegen
    codegen << Edge(label="Retrieve context") << rag
    
    codegen >> Edge(label="Generated Python") >> sandbox
    sandbox >> Edge(label="Execution Trace") >> judge
    
    judge >> Edge(label="Pass/Fail") >> fixer
    fixer >> Edge(label="Feedback Loop") >> codegen
    
    judge >> Edge(label="Final Code") >> user
