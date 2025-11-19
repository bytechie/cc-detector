import json
from claude_subagent import app as subagent_app


def test_scan_endpoint(monkeypatch):
    client = subagent_app.app.test_client()
    payload = {"text": "Charge: 4111 1111 1111 1111"}
    resp = client.post("/scan", data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "detections" in data
    assert "redacted" in data
    assert "[REDACTED]" in data["redacted"] or "4111" in data["redacted"]
