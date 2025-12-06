"""
Simplified Pytest Configuration and Fixtures for Credit Card Detection

This module provides basic pytest configuration for testing the credit card detection system.
"""

import pytest
import asyncio
import tempfile
import shutil
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Generator, Optional
import json
import time
import logging
from unittest.mock import Mock, AsyncMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_text_with_cards() -> str:
    """Sample text containing credit card numbers."""
    return """
    Customer payment information:
    Visa card: 4111111111111111 expires 12/25
    Mastercard: 5555555555554444 expires 09/24
    Contact: customer@example.com
    """


@pytest.fixture
def sample_text_no_cards() -> str:
    """Sample text without credit card numbers."""
    return """
    Regular transaction information:
    Customer bought items for $45.67 using cash.
    Contact: customer@example.com
    Phone: 555-123-4567
    """


@pytest.fixture
def mock_presidio_response():
    """Mock response from Presidio services."""
    return {
        "status": 200,
        "data": {
            "analyzer_healthy": True,
            "anonymizer_healthy": True
        }
    }


@pytest.fixture
def credit_card_test_numbers() -> Dict[str, Dict[str, Any]]:
    """Test credit card numbers with expected validation results."""
    return {
        "visa_valid": {
            "number": "4111111111111111",
            "valid": True,
            "type": "Visa"
        },
        "mastercard_valid": {
            "number": "5555555555554444",
            "valid": True,
            "type": "Mastercard"
        },
        "amex_valid": {
            "number": "378282246310005",
            "valid": True,
            "type": "American Express"
        },
        "discover_valid": {
            "number": "6011111111111117",
            "valid": True,
            "type": "Discover"
        },
        "invalid_luhn": {
            "number": "4111111111111112",
            "valid": False,
            "type": "Invalid"
        }
    }


@pytest.fixture
def api_test_data() -> List[Dict[str, Any]]:
    """Sample API test data."""
    return [
        {
            "name": "Basic Detection",
            "text": "Pay with Visa 4111111111111111",
            "expected_detections": 1,
            "expected_redacted": "Pay with Visa [REDACTED]"
        },
        {
            "name": "Multiple Cards",
            "text": "Cards: 4111111111111111, 5555555555554444",
            "expected_detections": 2,
            "expected_redacted": "Cards: [REDACTED], [REDACTED]"
        },
        {
            "name": "No Cards",
            "text": "Regular text with no payment information",
            "expected_detections": 0,
            "expected_redacted": "Regular text with no payment information"
        },
        {
            "name": "Formatted Cards",
            "text": "Card numbers: 4111-1111-1111-1111, 4242 4242 4242 4242",
            "expected_detections": 2,
            "expected_redacted": "Card numbers: [REDACTED], [REDACTED]"
        }
    ]


# Test configuration
@pytest.fixture(autouse=True)
def configure_logging():
    """Configure logging for tests."""
    logging.basicConfig(level=logging.WARNING)


@pytest.fixture
def mock_requests():
    """Mock requests module for external service calls."""
    with patch('requests.get') as mock_get:
        # Default successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def clean_app():
    """Create a clean Flask app instance for testing."""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

    from api.endpoints import create_app
    from utils.config import load_config

    # Load configuration for testing
    config = load_config(None, 'development')
    config.config['app']['debug'] = True
    config.config['app']['testing'] = True

    # Create app with minimal configuration
    app = create_app(config)

    # Set testing mode
    app.config['TESTING'] = True

    return app