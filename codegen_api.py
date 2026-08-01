# Streamed response emulator
import random
import time

import requests

from config import FAST_API_URL


def response_generator():
    response = random.choice([
        "Hello there! How can I assist you today?",
        "Hi, human! Is there anything I can help you with?",
        "Do you need help?",
    ])
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


def invoke_router_agent(user_query, thread_id) -> dict:
    """
    Sends a prompt to the Router Agent and returns the response as a JSON-compatible dictionary.
    """
    try:
        response = requests.post(
            f"{FAST_API_URL}/router",
            json={"user_query": user_query, "thread_id": thread_id},
            timeout=300,
        )
        response.raise_for_status()

        payload = response.json()
        if isinstance(payload, dict):
            return payload
        return {"data": payload}

    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred while invoking the Router Agent: {e}"}

    except ValueError as e:
        return {"error": f"Invalid JSON response from Router Agent: {e}"}
    