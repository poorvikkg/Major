"""
pipeline/services/api/__init__.py
Public API for the api sub-package.
"""

import threading
from typing import Optional

from pipeline.services.api.http_client import BackendHTTPClient
from pipeline.services.api.socket_client import BackendSocketClient

_http_client:   Optional[BackendHTTPClient]   = None
_socket_client: Optional[BackendSocketClient] = None
_client_lock    = threading.Lock()

def get_http_client() -> BackendHTTPClient:
    """Return singleton BackendHTTPClient."""
    global _http_client
    if _http_client is None:
        with _client_lock:
            if _http_client is None:
                _http_client = BackendHTTPClient()
    return _http_client

def get_socket_client() -> BackendSocketClient:
    """Return singleton BackendSocketClient (not yet connected)."""
    global _socket_client
    if _socket_client is None:
        with _client_lock:
            if _socket_client is None:
                _socket_client = BackendSocketClient()
    return _socket_client

__all__ = [
    "BackendHTTPClient",
    "BackendSocketClient",
    "get_http_client",
    "get_socket_client",
]
