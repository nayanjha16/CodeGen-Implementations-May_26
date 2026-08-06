import asyncio
from gradio.components import Chatbot
chatbot = Chatbot()
try:
    asyncio.run(chatbot.postprocess([{'role': 'user', 'content': 'hello'}, {'role': 'assistant', 'content': 'world'}]))
    print("Dicts worked")
except Exception as e:
    print("Dicts failed:", e)

try:
    asyncio.run(chatbot.postprocess([['hello', 'world']]))
    print("Tuples worked")
except Exception as e:
    print("Tuples failed:", e)
