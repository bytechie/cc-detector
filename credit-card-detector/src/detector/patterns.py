"""
Credit Card Detection Patterns

Common patterns and utilities for credit card detection.
"""

import re
from typing import Dict, List


class CardPatterns:
    """Credit card pattern matching utilities."""

    # Basic card number pattern (13-19 digits with optional separators)
    BASIC_PATTERN = re.compile(r'(?:\d[ -]?){13,19}\d')

    # Card type patterns
    CARD_PATTERNS = {
        'visa': r'^4[0-9]{12}(?:[0-9]{3})?$',
        'mastercard': r'^5[1-5][0-9]{14}$',
        'amex': r'^3[47][0-9]{13}$',
        'discover': r'^6(?:011|5[0-9]{2})[0-9]{12}$',
        'diners': r'^3(?:0[0-5]|[68][0-9])[0-9]{11}$',
        'jcb': r'^35[0-9]{14}$',
        'unionpay': r'^62[0-5][0-9]{13,16}$'
    }

    # Common credit card separators
    SEPARATORS = r'[ -]'

    @classmethod
    def find_all(cls, text: str) -> List[str]:
        """Find all potential card numbers in text."""
        matches = cls.BASIC_PATTERN.finditer(text)
        return [match.group() for match in matches]

    @classmethod
    def normalize(cls, card_number: str) -> str:
        """Remove separators and normalize card number."""
        return re.sub(r'\D', '', card_number)

    @classmethod
    def is_valid_length(cls, card_number: str) -> bool:
        """Check if card number has valid length."""
        normalized = cls.normalize(card_number)
        return 13 <= len(normalized) <= 19

    @classmethod
    def get_card_type(cls, card_number: str) -> str:
        """Detect card type from number."""
        normalized = cls.normalize(card_number)

        for card_type, pattern in cls.CARD_PATTERNS.items():
            if re.match(pattern, normalized):
                return card_type

        return 'unknown'

    @classmethod
    def get_all_patterns(cls) -> Dict[str, str]:
        """Get all card type patterns."""
        return cls.CARD_PATTERNS.copy()