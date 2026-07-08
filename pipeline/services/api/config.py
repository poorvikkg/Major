"""
config.py
---------
Configuration for the API module.
"""

import os

def _env(key: str, default: str) -> str:
    return os.environ.get(key, default).strip()

BACKEND_URL    = _env("BACKEND_URL",     "http://localhost:5000")
SOCKET_URL     = _env("SOCKET_URL",      BACKEND_URL)
API_KEY        = _env("BACKEND_API_KEY", "")
TIMEOUT        = int(_env("BACKEND_TIMEOUT", "5"))
MAX_RETRIES    = int(_env("BACKEND_RETRIES", "3"))
RETRY_BASE     = 0.5   # seconds — exponential backoff base
