"""Test the unified application subagent functionality."""
import json
import pytest
from unittest.mock import patch, MagicMock
from app import CreditCardDetectorApp


@pytest.fixture
def clean_prometheus_registry():
    """Clean up Prometheus registry to avoid conflicts."""
    import prometheus_client
    # Clear any existing metrics
    prometheus_client.REGISTRY._collector_to_names.clear()
    prometheus_client.REGISTRY._names_to_collectors.clear()


@pytest.fixture
def clean_metrics(clean_prometheus_registry):
    """Clean metrics after each test."""
    # This fixture will be called after each test
    yield
    # Clean up metrics created during the test
    prometheus_client.REGISTRY._collector_to_names.clear()
    prometheus_client.REGISTRY._names_to_collectors.clear()


@pytest.fixture
def app_instance(clean_prometheus_registry):
    """Create a clean app instance for testing."""
    return CreditCardDetectorApp(mode='basic')


def test_scan_endpoint(app_instance):
    """Test the scan endpoint with unified app."""
    client = app_instance.app.test_client()

    payload = {"text": "Charge: 4111 1111 1111 1111"}
    resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

    assert resp.status_code == 200
    data = resp.get_json()

    assert "detections" in data
    assert "redacted" in data
    assert isinstance(data["detections"], list)
    assert isinstance(data["redacted"], str)

    # Test that we found the card
    assert len(data["detections"]) == 1
    assert data["detections"][0]["number"] == "4111111111111111"
    assert data["detections"][0]["valid"] == True
    assert "[REDACTED]" in data["redacted"]


def test_scan_endpoint_no_cards(monkeypatch):
    """Test the scan endpoint with no credit cards."""
    app = CreditCardDetectorApp(mode='basic')
    client = app.app.test_client()

    payload = {"text": "No credit cards here"}
    resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

    assert resp.status_code == 200
    data = resp.get_json()

    assert data["detections"] == []
    assert data["redacted"] == "No credit cards here"


def test_scan_endpoint_empty_text(monkeypatch):
    """Test the scan endpoint with empty text."""
    app = CreditCardDetectorApp(mode='basic')
    client = app.app.test_client()

    payload = {"text": ""}
    resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

    assert resp.status_code == 200
    data = resp.get_json()

    assert data["detections"] == []
    assert data["redacted"] == ""


def test_scan_endpoint_invalid_json(monkeypatch):
    """Test the scan endpoint with invalid JSON."""
    app = CreditCardDetectorApp(mode='basic')
    client = app.test_client()

    resp = client.post("/scan", data="invalid json", content_type="application/json")

    assert resp.status_code == 400


def test_scan_endpoint_missing_text(monkeypatch):
    """Test the scan endpoint with missing text field."""
    app = CreditCardDetectorApp(mode='basic')
    client = app.test_client()

    payload = {"wrong_field": "data"}
    resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

    assert resp.status_code == 400


def test_scan_endpoint_multiple_cards(monkeypatch):
    """Test the scan endpoint with multiple credit cards."""
    app = CreditCardDetectorApp(mode='basic')
    client = app.test_client()

    payload = {"text": "Cards: 4111111111111111 and 5555555555554444"}
    resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

    assert resp.status_code == 200
    data = resp.get_json()

    assert len(data["detections"]) == 2
    assert len(data["detections"]) == 2
    # Check both cards were found
    card_numbers = [d["number"] for d in data["detections"]]
    assert "4111111111111111" in card_numbers
    assert "5555555555554444" in card_numbers


def test_scan_endpoint_invalid_luhn(monkeypatch):
    """Test the scan endpoint with invalid Luhn number."""
    app = CreditCardDetectorApp(mode='basic')
    client = app.test_client()

    payload = {"text": "Invalid card: 4111111111111112"}
    resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

    assert resp.status_code == 200
    data = resp.get_json()

    assert len(data["detections"]) == 1
    assert data["detections"][0]["number"] == "4111111111111112"
    assert data["detections"][0]["valid"] == False  # Invalid Luhn


def test_scan_endpoint_different_formats(monkeypatch):
    """Test the scan endpoint with different card formats."""
    app = CreditCardDetectorApp(mode='basic')
    client = app.test_client()

    payload = {"text": "Formats: 4111111111111111, 4111-1111-1111-1111, 4111 1111 1111 1111"}
    resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

    assert resp.status_code == 200
    data = resp.get_json()

    # Should detect all three formats
    assert len(data["detections"]) == 3
    # All should be normalized to the same number
    card_numbers = [d["number"] for d in data["detections"]]
    assert all(num == "4111111111111111" for num in card_numbers)


def test_scan_endpoint_metrics_mode(monkeypatch):
    """Test the scan endpoint in metrics mode."""
    app = CreditCardDetectorApp(mode='metrics')
    client = app.test_client()

    payload = {"text": "Card: 4111111111111111"}
    resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

    assert resp.status_code == 200
    data = resp.get_json()

    # Should include scan duration in metrics mode
    assert "scan_duration_seconds" in data


def test_scan_endpoint_full_mode(monkeypatch):
    """Test the scan endpoint in full mode."""
    app = CreditCardDetectorApp(mode='full')
    client = app.test_client()

    payload = {"text": "Card: 4111111111111111"}
    resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

    assert resp.status_code == 200
    data = resp.get_json()

    # Should include scan duration in full mode
    assert "scan_duration_seconds" in data
    # Should include resource usage in full mode
    assert "resource_usage" in data


def test_scan_endpoint_resource_aware_mode(monkeypatch):
    """Test the scan endpoint in resource-aware mode."""
    app = CreditCardDetectorApp(mode='resource_aware')
    client = app.test_client()

    payload = {"text": "Card: 4111111111111111"}
    resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")

    assert resp.status_code == 200
    data = resp.get_json()

    # Should include resource usage in resource-aware mode
    assert "resource_usage" in data


def test_health_endpoint_all_modes(monkeypatch):
    """Test the health endpoint in all modes."""
    modes = ['basic', 'metrics', 'adaptive', 'resource_aware', 'full']

    for mode in modes:
        app = CreditCardDetectorApp(mode=mode)
        client = app.app.test_client()

        resp = client.get('/health')

        assert resp.status_code == 200
        data = json.loads(resp.data)

        assert "status" in data
        assert "service" in data
        assert "mode" in data
        assert data["mode"] == mode


def test_index_endpoint_all_modes(monkeypatch):
    """Test the index endpoint in all modes."""
    modes = ['basic', 'metrics', 'adaptive', 'resource_aware', 'full']

    for mode in modes:
        app = CreditCardDetectorApp(mode=mode)
        client = app.test_client()

        resp = client.get('/')

        assert resp.status_code == 200
        data = json.loads(resp.data)

        assert "service" in data
        assert "mode" in data
        assert "endpoints" in data