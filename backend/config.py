import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_RELOAD = os.getenv("API_RELOAD", "false").lower() == "true"

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# RAG Configuration
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", "500"))

# Chat Configuration
MAX_CHAT_HISTORY = int(os.getenv("MAX_CHAT_HISTORY", "10"))
