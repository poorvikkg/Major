"""
pipeline/services/notifier.py
-----------------------------
Backward-compatibility shim.

The notification functionality has been refactored into:
    pipeline/services/notification/

This file re-exports Notifier.
"""

from pipeline.services.notification.notifier import Notifier

__all__ = ["Notifier"]
