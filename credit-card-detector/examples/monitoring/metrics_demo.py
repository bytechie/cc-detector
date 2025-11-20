#!/usr/bin/env python3
"""
Enhanced Credit Card Detection Demo with Prometheus Metrics
Standalone version for monitoring demonstration
"""

import os
import sys
import time
import json
import re
import requests
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Add the claude_subagent directory to Python path
sys.path.append('./claude_subagent')

app = Flask(__name__)

# Credit card detection logic
_PATTERN = re.compile(r'(?:\d[ -]?){13,19}\d')

def _luhn(number: str) -> bool:
    if not number.isdigit():
        return False
    digits = [int(d) for d in number]
    total = 0
    reverse = digits[::-1]
    for i, d in enumerate(reverse):
        if i % 2 == 1:
            dbl = d * 2
            if dbl > 9:
                dbl -= 9
            total += dbl
        else:
            total += d
    return total % 10 == 0

def detect_credit_cards(text: str):
    """Detect credit card numbers in text."""
    results = []
    for m in _PATTERN.finditer(text):
        raw = m.group(0)
        digits = re.sub(r"\D", "", raw)
        if not (13 <= len(digits) <= 19):
            continue
        valid = _luhn(digits)
        results.append({
            "start": m.start(),
            "end": m.end(),
            "raw": raw,
            "number": digits,
            "valid": valid,
        })
    return results

def redact_credit_cards(text: str, detections):
    """Redact detected credit cards from text."""
    redacted = text
    for detection in reversed(detections):
        start, end = detection["start"], detection["end"]
        redacted = redacted[:start] + "[REDACTED]" + redacted[end:]
    return redacted

# Prometheus Metrics
REQUEST_COUNT = Counter('credit_card_detector_requests_total',
                        'Total requests to credit card detector',
                        ['method', 'endpoint', 'status'])
SCAN_REQUESTS = Counter('credit_card_scan_requests_total',
                       'Total credit card scan requests',
                       ['has_detections'])

REQUEST_DURATION = Histogram('credit_card_detector_request_duration_seconds',
                           'Request duration in seconds',
                           ['method', 'endpoint'])
SCAN_DURATION = Histogram('credit_card_scan_duration_seconds',
                         'Credit card scan duration in seconds')

DETECTIONS_TOTAL = Counter('credit_card_detections_total',
                           'Total credit cards detected',
                           ['valid_luhn'])
CARDS_IN_TEXT = Histogram('credit_cards_found_per_scan',
                         'Number of credit cards found per scan')

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
        "version": "2.0.0-metrics",
        "dependencies": {}
    }

    # Check Presidio Analyzer (optional dependency)
    analyzer_url = os.environ.get("PRESIDIO_ANALYZER_URL", "http://localhost:3000")
    health_status["dependencies"]["analyzer"] = _check_presidio_service(analyzer_url, "presidio-analyzer")

    # Check Presidio Anonymizer (optional dependency)
    anonymizer_url = os.environ.get("PRESIDIO_ANONYMIZER_URL", "http://localhost:3001")
    health_status["dependencies"]["anonymizer"] = _check_presidio_service(anonymizer_url, "presidio-anonymizer")

    return jsonify(health_status)

@app.route("/scan", methods=["POST"])
def scan():
    """Scan text for credit card numbers with performance tracking."""
    start_time = time.time()

    try:
        data = request.get_json(force=True)
        text = data.get("text", "")

        # Perform detection with timing
        detections = detect_credit_cards(text)
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
        redacted = redact_credit_cards(text, detections)

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

@app.route("/", methods=["GET"])
def index():
    """Root endpoint with service info."""
    return jsonify({
        "service": "Credit Card Detector with Enhanced Metrics",
        "version": "2.0.0",
        "endpoints": {
            "/health": "Health check",
            "/scan": "Credit card detection (POST)",
            "/metrics": "Prometheus metrics"
        },
        "monitoring": {
            "prometheus": "http://localhost:9090",
            "grafana": "http://localhost:3002"
        }
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("SUBAGENT_PORT", 5000))
    print(f"🚀 Starting Credit Card Detector with Enhanced Metrics")
    print(f"📊 Metrics available at: http://localhost:{port}/metrics")
    print(f"🔍 Health check at: http://localhost:{port}/health")
    print(f"💚 Grafana dashboard: http://localhost:3002")
    app.run(host="0.0.0.0", port=port)