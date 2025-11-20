# Claude Subagent Design Notes

This subagent is a minimal Flask app used for local testing and for n8n integrations. It exposes a `POST /scan` endpoint that returns detections and a redacted text.

Replace the Skills with Presidio-based implementations for production.
