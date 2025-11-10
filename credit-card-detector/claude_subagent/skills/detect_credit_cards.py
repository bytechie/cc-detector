"""Simple detection logic for credit card numbers.

Returns a list of detections: {start, end, raw, number, valid}
"""
import re

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


def detect(text: str):
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


# Export a public alias for Luhn validation so tests can call it
is_valid_luhn = _luhn
