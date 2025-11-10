"""Presidio-backed detection wrapper with local fallback.

Tries the Presidio Analyzer REST API, falls back to the local detect implementation.
"""
import requests
from typing import List, Dict

# local fallback
try:
    from claude_subagent.skills import detect_credit_cards as local_detect
except Exception:
    local_detect = None

ANALYZER_URLS = [
    "http://presidio-analyzer:3000/analyze",
    "http://localhost:3000/analyze",
]


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


def detect(text: str) -> List[Dict]:
    payload = {"text": text, "entities": ["CREDIT_CARD"]}
    for url in ANALYZER_URLS:
        try:
            resp = requests.post(url, json=payload, timeout=3)
            if resp.status_code == 200:
                body = resp.json()
                # Presidio analyzer returns 'entities' list with start/end/score/entity_type
                entities = body.get("entities") or body.get("results") or []
                detections = []
                for e in entities:
                    start = e.get("start")
                    end = e.get("end")
                    raw = text[start:end] if start is not None and end is not None else e.get("entity_value") or ""
                    number = "".join(ch for ch in raw if ch.isdigit())
                    valid = _luhn(number) if number else False
                    detections.append({
                        "start": start,
                        "end": end,
                        "raw": raw,
                        "number": number,
                        "valid": valid,
                    })
                return detections
        except Exception:
            # try next URL/fallback
            continue

    # fallback to local implementation if available
    if local_detect:
        return local_detect.detect(text)
    return []
