"""Minimal Claude Subagent Flask app.

Endpoints:
- POST /scan  -> accepts JSON {"text": "..."} and returns JSON {detections, redacted}
"""
from flask import Flask, request, jsonify
from claude_subagent.skills import detect_credit_cards, redact_credit_cards

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


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
