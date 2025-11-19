"""Enhanced Claude Subagent Flask app with Prometheus metrics.

Endpoints:
- POST /scan  -> accepts JSON {"text": "..."} and returns JSON {detections, redacted}
- GET /health -> returns health status with dependency checks
- GET /metrics -> Prometheus metrics endpoint
"""
import os
import requests
import time
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from skills.core import detect_credit_cards, redact_credit_cards

app = Flask(__name__)

# Prometheus Metrics
# Request counters
REQUEST_COUNT = Counter('credit_card_detector_requests_total',
                        'Total requests to credit card detector',
                        ['method', 'endpoint', 'status'])
SCAN_REQUESTS = Counter('credit_card_scan_requests_total',
                       'Total credit card scan requests',
                       ['has_detections'])

# Performance metrics
REQUEST_DURATION = Histogram('credit_card_detector_request_duration_seconds',
                           'Request duration in seconds',
                           ['method', 'endpoint'])
SCAN_DURATION = Histogram('credit_card_scan_duration_seconds',
                         'Credit card scan duration in seconds')

# Detection metrics
DETECTIONS_TOTAL = Counter('credit_card_detections_total',
                           'Total credit cards detected',
                           ['valid_luhn'])
CARDS_IN_TEXT = Histogram('credit_cards_found_per_scan',
                         'Number of credit cards found per scan')

# System metrics
ACTIVE_CONNECTIONS = Gauge('credit_card_detector_active_connections',
                          'Number of active connections')
LATEST_SCAN_TIMESTAMP = Gauge('credit_card_detector_latest_scan_timestamp',
                             'Timestamp of latest scan')

# Performance tracking
@app.before_request
def before_request():
    request.start_time = time.time()
    ACTIVE_CONNECTIONS.inc()

@app.after_request
def after_request(response):
    request_duration = time.time() - request.start_time
    REQUEST_DURATION.labels(method=request.method, endpoint=request.endpoint).observe(request_duration)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint, status=response.status_code).inc()
    ACTIVE_CONNECTIONS.dec()
    return response

def _check_presidio_service(url: str, service_name: str) -> dict:
    """Check if a Presidio service is healthy."""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            return {"name": service_name, "status": "healthy", "url": url}
        else:
            return {"name": service_name, "status": "unhealthy", "url": url, "error": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"name": service_name, "status": "unreachable", "url": url, "error": str(e)}

@app.route("/health", methods=["GET"])
def health():
    """Health check with dependency status."""
    health_status = {
        "status": "ok",
        "service": "claude-subagent",
        "dependencies": {}
    }

    # Check Presidio Analyzer (optional dependency)
    analyzer_url = os.environ.get("PRESIDIO_ANALYZER_URL", "http://localhost:3000")
    health_status["dependencies"]["analyzer"] = _check_presidio_service(analyzer_url, "presidio-analyzer")

    # Check Presidio Anonymizer (optional dependency)
    anonymizer_url = os.environ.get("PRESIDIO_ANONYMIZER_URL", "http://localhost:3001")
    health_status["dependencies"]["anonymizer"] = _check_presidio_service(anonymizer_url, "presidio-anonymizer")

    # Determine overall health
    unhealthy_deps = [dep for dep in health_status["dependencies"].values()
                      if dep["status"] not in ["healthy", "unreachable"]]

    if unhealthy_deps:
        health_status["status"] = "degraded"
        health_status["message"] = f"Some dependencies are unhealthy: {[dep['name'] for dep in unhealthy_deps]}"

    return jsonify(health_status)

@app.route("/scan", methods=["POST"])
def scan():
    """Scan text for credit card numbers with performance tracking."""
    start_time = time.time()

    try:
        data = request.get_json(force=True)
        text = data.get("text", "")

        # Perform detection with timing
        detections = detect_credit_cards.detect(text)
        scan_duration = time.time() - start_time

        # Update metrics
        SCAN_DURATION.observe(scan_duration)
        CARDS_IN_TEXT.observe(len(detections))
        LATEST_SCAN_TIMESTAMP.set(time.time())

        # Track detection counts
        valid_cards = sum(1 for d in detections if d['valid'])
        invalid_cards = len(detections) - valid_cards

        if valid_cards > 0:
            DETECTIONS_TOTAL.labels(valid_luhn='true').inc(valid_cards)
        if invalid_cards > 0:
            DETECTIONS_TOTAL.labels(valid_luhn='false').inc(invalid_cards)

        # Track scan requests
        SCAN_REQUESTS.labels(has_detections='true' if detections else 'false').inc()

        # Perform redaction
        redacted = redact_credit_cards.redact(text, detections)

        response = jsonify({
            "detections": detections,
            "redacted": redacted,
            "metrics": {
                "scan_duration_seconds": scan_duration,
                "cards_detected": len(detections),
                "valid_cards": valid_cards,
                "invalid_cards": invalid_cards
            }
        })

        return response

    except Exception as e:
        # Track errors
        SCAN_REQUESTS.labels(has_detections='error').inc()
        return jsonify({"error": str(e)}), 500

@app.route("/metrics", methods=["GET"])
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("SUBAGENT_PORT", 5000))
    app.run(host="0.0.0.0", port=port)