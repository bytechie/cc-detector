"""
API Request/Response Schemas

Data validation and serialization for API endpoints.
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Dict
from datetime import datetime


@dataclass
class Detection:
    """Credit card detection result."""
    number: str
    start: int
    end: int
    raw: str
    valid: bool
    card_type: Optional[str] = None


@dataclass
class ScanRequest:
    """API scan request."""
    text: str
    redact_mode: Optional[str] = "redact"
    validation: Optional[bool] = True
    card_type_detection: Optional[bool] = False

    def __post_init__(self):
        """Validate request parameters."""
        if not self.text:
            raise ValueError("Text cannot be empty")
        if len(self.text) > 100000:
            raise ValueError("Text too long (maximum 100,000 characters)")
        if self.redact_mode not in ["redact", "mask"]:
            raise ValueError("Invalid redact_mode (must be 'redact' or 'mask')")


@dataclass
class ScanResponse:
    """API scan response."""
    detections: List[Detection]
    redacted: str
    scan_duration_seconds: float
    cards_found: int
    valid_cards: int
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "detections": [
                {
                    "number": d.number,
                    "start": d.start,
                    "end": d.end,
                    "raw": d.raw,
                    "valid": d.valid,
                    "card_type": d.card_type
                }
                for d in self.detections
            ],
            "redacted": self.redacted,
            "scan_duration_seconds": self.scan_duration_seconds,
            "cards_found": self.cards_found,
            "valid_cards": self.valid_cards,
            "timestamp": self.timestamp
        }


@dataclass
class HealthResponse:
    """Health check response."""
    status: str
    service: str
    version: str
    timestamp: str
    mode: Optional[str] = None
    components: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            "status": self.status,
            "service": self.service,
            "version": self.version,
            "timestamp": self.timestamp
        }
        if self.mode:
            result["mode"] = self.mode
        if self.components:
            result["components"] = self.components
        return result


@dataclass
class ErrorResponse:
    """Error response."""
    error: str
    message: str
    timestamp: str
    request_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        result = {
            "error": self.error,
            "message": self.message,
            "timestamp": self.timestamp
        }
        if self.request_id:
            result["request_id"] = self.request_id
        return result