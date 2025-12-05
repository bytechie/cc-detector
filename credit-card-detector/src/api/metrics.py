"""
Prometheus Metrics Integration

Provides custom metrics for the Credit Card Detector service.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from functools import wraps
import time
import logging

# Custom metrics for the Credit Card Detector
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

CREDIT_CARD_DETECTIONS = Counter(
    'credit_card_detections_total',
    'Total credit card numbers detected',
    ['valid', 'card_type']
)

SCAN_DURATION = Histogram(
    'credit_card_scan_duration_seconds',
    'Time taken to scan text for credit cards',
    buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25]
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections_total',
    'Number of active connections'
)

SERVICE_UPTIME = Gauge(
    'service_uptime_seconds',
    'Service uptime in seconds'
)

logger = logging.getLogger(__name__)


def track_request_metrics(func):
    """Decorator to track request metrics."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()

        # Increment active connections
        ACTIVE_CONNECTIONS.inc()

        try:
            # Extract Flask request from args if available
            from flask import request
            method = getattr(request, 'method', 'UNKNOWN')
            endpoint = getattr(request, 'endpoint', 'unknown')

            # Call the original function
            response = func(*args, **kwargs)

            # Extract status code from response
            if hasattr(response, 'status_code'):
                status_code = str(response.status_code)
            elif isinstance(response, tuple) and len(response) > 1:
                status_code = str(response[1])
            else:
                status_code = '200'

            # Record metrics
            duration = time.time() - start_time
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
            REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

            return response

        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            REQUEST_COUNT.labels(method='UNKNOWN', endpoint='error', status_code='500').inc()
            REQUEST_DURATION.labels(method='UNKNOWN', endpoint='error').observe(duration)
            logger.error(f"Request error in metrics tracking: {e}")
            raise

        finally:
            # Decrement active connections
            ACTIVE_CONNECTIONS.dec()

    return wrapper


def record_credit_card_detection(detection):
    """Record credit card detection metrics."""
    try:
        valid_str = 'true' if detection.get('valid', False) else 'false'
        card_type = detection.get('card_type', 'unknown')

        CREDIT_CARD_DETECTIONS.labels(valid=valid_str, card_type=card_type).inc()

    except Exception as e:
        logger.error(f"Error recording detection metrics: {e}")


def record_scan_duration(duration, cards_found):
    """Record scan operation metrics."""
    try:
        SCAN_DURATION.observe(duration)

        # Record detection count
        for _ in range(cards_found):
            CREDIT_CARD_DETECTIONS.labels(valid='unknown', card_type='unknown').inc()

    except Exception as e:
        logger.error(f"Error recording scan metrics: {e}")


def get_metrics():
    """Generate Prometheus metrics."""
    try:
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return "Error generating metrics", 500, {'Content-Type': 'text/plain'}


def initialize_metrics():
    """Initialize metrics on service startup."""
    try:
        # Set initial uptime
        SERVICE_UPTIME.set(0)

        # Set initial active connections
        ACTIVE_CONNECTIONS.set(0)

        logger.info("Prometheus metrics initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing metrics: {e}")


def update_uptime(start_time):
    """Update service uptime metric."""
    try:
        uptime = time.time() - start_time
        SERVICE_UPTIME.set(uptime)
    except Exception as e:
        logger.error(f"Error updating uptime: {e}")