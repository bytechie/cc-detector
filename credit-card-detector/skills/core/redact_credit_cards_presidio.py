"""Presidio-backed anonymizer wrapper with local fallback.

If the Presidio anonymizer service is available it will be used; otherwise fall back to the simple local redactor.
"""
import requests
from typing import List, Dict

try:
    from claude_subagent.skills import redact_credit_cards as local_redact
except Exception:
    local_redact = None

ANON_URLS = [
    "http://presidio-anonymizer:3001/anonymize",
    "http://localhost:3001/anonymize",
]


def redact(text: str, detections: List[Dict], mode: str = "redact") -> str:
    # presupposes detections from analyzer (list of {start,end,entity_type,...})
    # Build a simple anonymizer payload expected by Presidio anonymizer
    try:
        for url in ANON_URLS:
            try:
                payload = {
                    "text": text,
                    # If the analyzer output is not provided, Presidio can extract entities itself
                    # but here we pass empty analysis_result to allow default behavior
                    "anonymizers_config": {
                        "DEFAULT": {"type": "replace", "new_value": "[REDACTED]"}
                    },
                }
                resp = requests.post(url, json=payload, timeout=3)
                if resp.status_code == 200:
                    body = resp.json()
                    return body.get("text", body.get("result", text))
            except Exception:
                continue
    except Exception:
        pass

    # fallback
    if local_redact:
        return local_redact.redact(text, detections, mode=mode)
    # last-resort simple redact
    if not detections:
        return text
    spans = sorted(detections, key=lambda d: d["start"])
    out = []
    last = 0
    for d in spans:
        out.append(text[last:d["start"]])
        out.append("[REDACTED]")
        last = d["end"]
    out.append(text[last:])
    return "".join(out)
