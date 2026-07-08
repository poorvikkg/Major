"""
pipeline/services/camera_manager.py
-----------------------------------
Backward-compatibility shim.

The camera functionality has been refactored into:
    pipeline/services/camera/

This file re-exports CameraManager so that existing imports
continue to work without modification.
"""

from pipeline.services.camera.camera_manager import CameraManager

__all__ = ["CameraManager"]
