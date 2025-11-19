"""Redaction utilities.

Two modes:
- redact: replace detected span with `[REDACTED]`
- mask: keep last 4 digits, mask the rest with `*`
"""
from typing import List, Dict


def redact(text: str, detections: List[Dict], mode: str = "redact") -> str:
    if not detections:
        return text
    # Sort by start offset
    spans = sorted(detections, key=lambda d: d["start"])
    out = []
    last = 0
    for d in spans:
        out.append(text[last:d["start"]])
        if mode == "redact":
            out.append("[REDACTED]")
        else:
            num = d.get("number", "")
            if len(num) > 4:
                masked = "*" * (len(num) - 4) + num[-4:]
            else:
                masked = "*" * len(num)
            out.append(masked)
        last = d["end"]
    out.append(text[last:])
    return "".join(out)
