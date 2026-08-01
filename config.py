import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

FAST_API_URL = os.getenv("FAST_API_URL", "http://localhost:8080")
