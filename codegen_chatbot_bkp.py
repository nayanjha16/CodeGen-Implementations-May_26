import streamlit as st
from codegen_api import invoke_router_agent, response_generator

st.title("Hello, welcome to the Code Gen chatbot!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask me to generate code for you."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = invoke_router_agent(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.write (response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})    
    
      