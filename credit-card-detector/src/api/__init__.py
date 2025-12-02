"""
Credit Card Detector API Module

Unified API endpoints with clean separation of concerns.
"""

from .endpoints import create_app
from .schemas import ScanRequest, ScanResponse

__all__ = ['create_app', 'ScanRequest', 'ScanResponse']