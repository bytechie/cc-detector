"""Minimal Claude Subagent Flask app.

Endpoints:
- POST /scan  -> accepts JSON {"text": "..."} and returns JSON {detections, redacted}
- GET /health -> returns health status with dependency checks
"""
import os
import requests
from flask import Flask, request, jsonify
from skills.core import detect_credit_cards, redact_credit_cards

app = Flask(__name__)


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
    data = request.get_json(force=True)
    text = data.get("text", "")
    detections = detect_credit_cards.detect(text)
    redacted = redact_credit_cards.redact(text, detections)
    return jsonify({"detections": detections, "redacted": redacted})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("SUBAGENT_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
