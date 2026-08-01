
# from langgraph.graph import END, START, MessagesState
# from langgraph.graph import StateGraph
# from langchain.messages import HumanMessage

# def greeting(state: MessagesState) -> MessagesState:
#     return {"messages": [HumanMessage(content="Hello! How can I assist you today?")]}


# builder = StateGraph(MessagesState)
# builder.add_node("greeting", greeting)
# builder.set_entry_point("greeting")
# builder.add_edge(START, "greeting")
# builder.add_edge("greeting", END)

# graph  = builder.compile()

# response = graph.invoke({"messages": [HumanMessage(content="Hi there!")]})

# for message in response["messages"]:
#     print(message.content)
