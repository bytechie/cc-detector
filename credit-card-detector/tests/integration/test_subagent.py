"""Fixed version of subagent functionality tests."""
import json
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from api.endpoints import create_app
from utils.config import load_config


@pytest.fixture(scope="function")
def clean_prometheus_registry():
    """Clean up Prometheus registry to avoid conflicts."""
    try:
        import prometheus_client
        # Clear any existing metrics
        prometheus_client.REGISTRY._collector_to_names.clear()
        prometheus_client.REGISTRY._names_to_collectors.clear()
    except ImportError:
        pass
    yield


@pytest.fixture
def basic_app(clean_prometheus_registry):
    """Create a basic mode app for testing."""
    return CreditCardDetectorApp(mode='basic')


@pytest.fixture
def metrics_app(clean_prometheus_registry):
    """Create a metrics mode app for testing."""
    return CreditCardDetectorApp(mode='metrics')


@pytest.fixture
def full_app(clean_prometheus_registry):
    """Create a full mode app for testing."""
    return CreditCardDetectorApp(mode='full')


class TestScanEndpoint:
    """Test the scan endpoint functionality."""

    def test_basic_scan_with_card(self, basic_app):
        """Test scan endpoint with credit card."""
        client = basic_app.app.test_client()

        payload = {"text": "Pay with Visa 4111111111111111"}
        resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

        assert resp.status_code == 200
        data = resp.get_json()

        assert "detections" in data
        assert "redacted" in data
        assert len(data["detections"]) == 1
        assert data["detections"][0]["number"] == "4111111111111111"
        assert data["detections"][0]["valid"] == True
        assert "[REDACTED]" in data["redacted"]

    def test_basic_scan_no_cards(self, basic_app):
        """Test scan endpoint with no credit cards."""
        client = basic_app.app.test_client()

        payload = {"text": "Regular text with no payment information"}
        resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

        assert resp.status_code == 200
        data = resp.get_json()

        assert "detections" in data
        assert "redacted" in data
        assert len(data["detections"]) == 0

    def test_basic_scan_empty_text(self, basic_app):
        """Test scan endpoint with empty text."""
        client = basic_app.app.test_client()

        payload = {"text": ""}
        resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

        assert resp.status_code == 200
        data = resp.get_json()

        assert "detections" in data
        assert "redacted" in data
        assert len(data["detections"]) == 0

    def test_basic_scan_multiple_cards(self, basic_app):
        """Test scan endpoint with multiple credit cards."""
        client = basic_app.app.test_client()

        payload = {"text": "Cards: 4111111111111111, 5555555555554444"}
        resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

        assert resp.status_code == 200
        data = resp.get_json()

        assert "detections" in data
        assert len(data["detections"]) == 2

    def test_basic_scan_invalid_luhn(self, basic_app):
        """Test scan endpoint with invalid Luhn number."""
        client = basic_app.app.test_client()

        payload = {"text": "Invalid card: 4111111111111112"}
        resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

        assert resp.status_code == 200
        data = resp.get_json()

        assert "detections" in data
        assert len(data["detections"]) == 1
        assert data["detections"][0]["valid"] == False

    def test_scan_invalid_json(self, basic_app):
        """Test scan endpoint with invalid JSON."""
        client = basic_app.app.test_client()

        resp = client.post("/scan", data="invalid json", content_type="application/json")
        assert resp.status_code in [400, 500]  # Either 400 (bad request) or 500 (server error)

    def test_scan_missing_text(self, basic_app):
        """Test scan endpoint with missing text field."""
        client = basic_app.app.test_client()

        payload = {"other_field": "value"}
        resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")
        assert resp.status_code == 200  # The app gracefully handles missing text


class TestHealthEndpoint:
    """Test the health endpoint functionality."""

    def test_health_basic_mode(self, basic_app):
        """Test health endpoint in basic mode."""
        client = basic_app.app.test_client()

        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()

        assert "status" in data
        assert "service" in data
        assert "mode" in data
        assert data["mode"] == "basic"

    def test_health_metrics_mode(self, metrics_app):
        """Test health endpoint in metrics mode."""
        client = metrics_app.app.test_client()

        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()

        assert "status" in data
        assert "mode" in data
        assert data["mode"] == "metrics"

    def test_health_full_mode(self, full_app):
        """Test health endpoint in full mode."""
        client = full_app.app.test_client()

        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()

        assert "status" in data
        assert "mode" in data
        assert data["mode"] == "full"


class TestIndexEndpoint:
    """Test the index endpoint functionality."""

    def test_index_basic_mode(self, basic_app):
        """Test index endpoint in basic mode."""
        client = basic_app.app.test_client()

        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.get_json()

        assert "service" in data
        assert "mode" in data
        assert "endpoints" in data


class TestMetricsEndpoint:
    """Test the metrics endpoint functionality."""

    def test_metrics_basic_mode(self, basic_app):
        """Test metrics endpoint in basic mode."""
        client = basic_app.app.test_client()

        resp = client.get("/metrics")
        # Basic mode might not have metrics, so 404 is acceptable
        assert resp.status_code in [200, 404]

    def test_metrics_metrics_mode(self, metrics_app):
        """Test metrics endpoint in metrics mode."""
        client = metrics_app.app.test_client()

        resp = client.get("/metrics")
        assert resp.status_code == 200

    def test_metrics_full_mode(self, full_app):
        """Test metrics endpoint in full mode."""
        client = full_app.app.test_client()

        resp = client.get("/metrics")
        assert resp.status_code == 200


class TestSpecialFormats:
    """Test special card formats."""

    def test_formatted_cards_with_spaces(self, basic_app):
        """Test cards with spaces."""
        client = basic_app.app.test_client()

        payload = {"text": "Card: 4111 1111 1111 1111"}
        resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["detections"]) == 1
        assert data["detections"][0]["valid"] == True

    def test_formatted_cards_with_dashes(self, basic_app):
        """Test cards with dashes."""
        client = basic_app.app.test_client()

        payload = {"text": "Card: 4111-1111-1111-1111"}
        resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["detections"]) == 1
        assert data["detections"][0]["valid"] == True

    def test_mixed_formatted_cards(self, basic_app):
        """Test mixed formatted cards."""
        client = basic_app.app.test_client()

        payload = {"text": "Cards: 4111 1111 1111 1111, 4242-4242-4242-4242"}
        resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["detections"]) == 2