import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

QWEN_BASE_MODEL = os.getenv("QWEN_BASE_MODEL", "Qwen/Qwen2.5-Coder-3B-Instruct")
LLAMA_BASE_MODEL = os.getenv("LLAMA_BASE_MODEL", "Llama-3.1-8B-Instant")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
FAST_API_URL = os.getenv("FAST_API_URL", "http://localhost:8000")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set. Create a .env file with GROQ_API_KEY=your_token")
