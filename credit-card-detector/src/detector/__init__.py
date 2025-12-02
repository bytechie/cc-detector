"""
Credit Card Detector - Unified Detection Module

This module provides a clean, unified interface for credit card detection
and redaction functionality.
"""

from .core import CreditCardDetector
from .patterns import CardPatterns
from .validators import CardValidators

# Main exports
__all__ = [
    'CreditCardDetector',
    'CardPatterns',
    'CardValidators'
]

# Version info
__version__ = '2.0.0'