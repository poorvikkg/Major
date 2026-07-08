"""
pipeline/services/api.py
------------------------
Backward-compatibility shim.

The API clients have been refactored into:
    pipeline/services/api/

This file re-exports the classes and singletons.
"""

from pipeline.services.api.http_client import BackendHTTPClient
from pipeline.services.api.socket_client import BackendSocketClient
from pipeline.services.api import get_http_client, get_socket_client

__all__ = [
    "BackendHTTPClient",
    "BackendSocketClient",
    "get_http_client",
    "get_socket_client",
]
