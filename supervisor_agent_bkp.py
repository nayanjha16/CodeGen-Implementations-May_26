
# from typing import Any
# from langgraph.graph import END, START, MessagesState
# from langgraph.graph import StateGraph
# from langchain.messages import HumanMessage
# from code_generator import generate
# from code_explanation import explain
# from state import AgentState


# def generator_node(state: AgentState) -> dict[str, Any]:
#     result = generate(state)
#     return {
#         "generated_code": result
#     }

# def explain_node(state: AgentState) -> dict[str, Any]:
#     explanation = explain(state)
#     return {
#         "explanation": explanation
#     }


# builder = StateGraph(AgentState)
# builder.add_node("generator_node", generator_node)
# builder.add_node("explain_node", explain_node)
# builder.set_entry_point("generator_node")
# builder.add_edge(START, "generator_node")
# builder.add_edge("generator_node", "explain_node")
# builder.add_edge("explain_node", END)

# graph  = builder.compile()

# query = "Please write a Python function to calculate the sum of two numbers."
# response = graph.invoke({
#     "messages": [HumanMessage(content=query)],
#     "query": query,
#     "translation": False,
#     "source_language": "",
#     "target_language": "",
#     "source_code": "",
#     "generated_code": "",
#     "explanation": ""
# })

# for message in response["messages"]:
#     print(message.content)

# print("Output Code: \n")    
# print(response["generated_code"])
# print("Explanation: \n")
# print(response["explanation"])

# def invoke_graph(query: str) -> dict[str, Any]:
#     response = graph.invoke({
#         "messages": [HumanMessage(content=query)],
#         "query": query,
#         "translation": False,
#         "source_language": "",
#         "target_language": "",
#         "source_code": "",
#         "generated_code": "",
#         "explanation": ""
#     })
#     return response