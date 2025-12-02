"""
Credit Card Detector - Core Functionality

Unified detection and redaction functionality with a clean, simple interface.
"""

import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# Import from existing modules
try:
    from src.core.detect_credit_cards import detect as _detect_cards
    from src.core.redact_credit_cards import redact as _redact_cards
except ImportError:
    # Fallback for development
    from ..core.detect_credit_cards import detect as _detect_cards
    from ..core.redact_credit_cards import redact as _redact_cards


@dataclass
class Detection:
    """Represents a single credit card detection."""
    number: str
    start: int
    end: int
    raw: str
    valid: bool
    card_type: Optional[str] = None


@dataclass
class ScanResult:
    """Represents the result of a credit card scan."""
    detections: List[Detection]
    redacted: str
    scan_duration: float
    cards_found: int
    valid_cards: int


class CreditCardDetector:
    """
    Unified Credit Card Detector with clean, simple interface.

    Features:
    - Credit card detection and validation
    - Text redaction (redact or mask modes)
    - Performance timing
    - Simple result objects
    """

    def __init__(self, validation: bool = True, card_type_detection: bool = False):
        """
        Initialize the detector.

        Args:
            validation: Enable Luhn validation
            card_type_detection: Enable card type detection (Visa, MasterCard, etc.)
        """
        self.validation = validation
        self.card_type_detection = card_type_detection
        self._patterns = self._get_patterns()

    def detect(self, text: str) -> List[Detection]:
        """
        Detect credit cards in text.

        Args:
            text: Text to scan for credit cards

        Returns:
            List of Detection objects
        """
        detections = []

        # Use existing detection logic
        raw_detections = _detect_cards(text)

        for detection in raw_detections:
            # Skip invalid cards if validation is enabled
            if self.validation and not detection.get('valid', True):
                continue

            # Create Detection object
            card_detection = Detection(
                number=detection['number'],
                start=detection['start'],
                end=detection['end'],
                raw=detection['raw'],
                valid=detection['valid'],
                card_type=self._detect_card_type(detection['number']) if self.card_type_detection else None
            )
            detections.append(card_detection)

        return detections

    def redact(self, text: str, mode: str = "redact") -> str:
        """
        Redact credit cards from text.

        Args:
            text: Text containing credit cards to redact
            mode: "redact" for [REDACTED] or "mask" for ****-****-****-1234

        Returns:
            Redacted text
        """
        detections = self.detect(text)
        if not detections:
            return text

        # Convert to dict format for existing redaction function
        detection_dicts = [
            {
                'number': d.number,
                'start': d.start,
                'end': d.end,
                'raw': d.raw,
                'valid': d.valid
            }
            for d in detections
        ]

        return _redact_cards(text, detection_dicts, mode)

    def scan(self, text: str, redact_mode: str = "redact") -> ScanResult:
        """
        Complete scan with detection and redaction.

        Args:
            text: Text to scan
            redact_mode: "redact" or "mask"

        Returns:
            ScanResult with all information
        """
        start_time = time.time()

        # Detect cards
        detections = self.detect(text)

        # Redact text
        redacted = self.redact(text, redact_mode)

        # Calculate timing
        duration = time.time() - start_time
        valid_count = sum(1 for d in detections if d.valid)

        return ScanResult(
            detections=detections,
            redacted=redacted,
            scan_duration=duration,
            cards_found=len(detections),
            valid_cards=valid_count
        )

    def _get_patterns(self) -> Dict[str, str]:
        """Get card type patterns."""
        return {
            'visa': r'^4[0-9]{12}(?:[0-9]{3})?$',
            'mastercard': r'^5[1-5][0-9]{14}$',
            'amex': r'^3[47][0-9]{13}$',
            'discover': r'^6(?:011|5[0-9]{2})[0-9]{12}$',
            'diners': r'^3(?:0[0-5]|[68][0-9])[0-9]{11}$',
            'jcb': r'^35[0-9]{14}$'
        }

    def _detect_card_type(self, number: str) -> Optional[str]:
        """Detect credit card type from number."""
        import re

        for card_type, pattern in self._patterns.items():
            if re.match(pattern, number):
                return card_type

        return 'unknown'


# Convenience functions for backward compatibility
def detect_credit_cards(text: str) -> List[Dict]:
    """Simple detection function - backward compatibility."""
    detector = CreditCardDetector()
    detections = detector.detect(text)

    return [
        {
            'number': d.number,
            'start': d.start,
            'end': d.end,
            'raw': d.raw,
            'valid': d.valid
        }
        for d in detections
    ]


def redact_credit_cards(text: str, detections: List[Dict], mode: str = "redact") -> str:
    """Simple redaction function - backward compatibility."""
    return _redact_cards(text, detections, mode)