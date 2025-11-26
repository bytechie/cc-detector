"""Test the unified application health endpoint."""
import pytest
import json
from unittest.mock import patch, MagicMock
from app import CreditCardDetectorApp


def test_check_presidio_service_healthy():
    """Test healthy Presidio service check."""
    # Create app instance to access the _check_presidio_service method
    app = CreditCardDetectorApp(mode='basic')

    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = app._check_presidio_service("http://localhost:3000", "test-service")

        assert result["name"] == "test-service"
        assert result["status"] == "healthy"
        assert result["url"] == "http://localhost:3000"


def test_check_presidio_service_unhealthy():
    """Test unhealthy Presidio service check."""
    app = CreditCardDetectorApp(mode='basic')

    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = app._check_presidio_service("http://localhost:3000", "test-service")

        assert result["name"] == "test-service"
        assert result["status"] == "unhealthy"
        assert result["url"] == "http://localhost:3000"
        assert "error" in result


def test_check_presidio_service_unreachable():
    """Test unreachable Presidio service check."""
    app = CreditCardDetectorApp(mode='basic')

    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Connection failed")

        result = app._check_presidio_service("http://localhost:3000", "test-service")

        assert result["name"] == "test-service"
        assert result["status"] == "unreachable"
        assert result["url"] == "http://localhost:3000"
        assert "error" in result


def test_health_endpoint_basic_mode():
    """Test health endpoint in basic mode."""
    with patch('requests.get') as mock_get:
        # Mock both Presidio services as healthy
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        app = CreditCardDetectorApp(mode='basic')

        with app.app.test_client() as client:
            response = client.get('/health')

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["status"] == "ok"
            assert data["service"] == "claude-subagent"
            assert "dependencies" in data
            assert data["dependencies"]["analyzer"]["status"] == "healthy"
            assert data["dependencies"]["anonymizer"]["status"] == "healthy"


def test_health_endpoint_metrics_mode():
    """Test health endpoint in metrics mode."""
    with patch('requests.get') as mock_get:
        # Mock both Presidio services as healthy
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        app = CreditCardDetectorApp(mode='metrics')

        with app.app.test_client() as client:
            response = client.get('/health')

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["status"] == "ok"
            assert data["service"] == "claude-subagent"
            assert data["mode"] == "metrics"
            assert "dependencies" in data


def test_health_endpoint_adaptive_mode():
    """Test health endpoint in adaptive mode."""
    with patch('requests.get') as mock_get:
        # Mock both Presidio services as healthy
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        app = CreditCardDetectorApp(mode='adaptive')

        with app.app.test_client() as client:
            response = client.get('/health')

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["status"] == "ok"
            assert data["service"] == "claude-subagent-adaptive"
            assert data["mode"] == "adaptive"
            assert "adaptive_skills" in data


def test_health_endpoint_resource_aware_mode():
    """Test health endpoint in resource-aware mode."""
    with patch('requests.get') as mock_get:
        # Mock both Presidio services as healthy
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        app = CreditCardDetectorApp(mode='resource_aware')

        with app.app.test_client() as client:
            response = client.get('/health')

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["status"] == "ok"
            assert data["service"] == "claude-subagent"
            assert data["mode"] == "resource_aware"


def test_health_endpoint_full_mode():
    """Test health endpoint in full mode."""
    with patch('requests.get') as mock_get:
        # Mock both Presidio services as healthy
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        app = CreditCardDetectorApp(mode='full')

        with app.app.test_client() as client:
            response = client.get('/health')

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["status"] == "ok"
            assert data["service"] == "claude-subagent"
            assert data["mode"] == "full"
            assert "adaptive_skills" in data


def test_health_endpoint_with_dependencies_down():
    """Test health endpoint with degraded dependencies."""
    with patch('requests.get') as mock_get:
        # Mock one service as unhealthy
        def side_effect(*args, **kwargs):
            if "3001" in args[0]:  # anonymizer port
                mock_response = MagicMock()
                mock_response.status_code = 500
                return mock_response
            else:  # analyzer port
                mock_response = MagicMock()
                mock_response.status_code = 200
                return mock_response

        mock_get.side_effect = side_effect

        app = CreditCardDetectorApp(mode='basic')

        with app.app.test_client() as client:
            response = client.get('/health')

            assert response.status_code == 200
            data = json.loads(response.data)

            assert data["status"] == "degraded"
            assert "message" in data


def test_health_endpoint_timestamp():
    """Test health endpoint includes timestamp."""
    with patch('requests.get') as mock_get:
        # Mock both Presidio services as healthy
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        app = CreditCardDetectorApp(mode='basic')

        with app.app.test_client() as client:
            response = client.get('/health')

            assert response.status_code == 200
            data = json.loads(response.data)

            assert "timestamp" in data
            # Verify timestamp is a valid ISO format string
            import datetime
            datetime.datetime.fromisoformat(data["timestamp"])