"""
language.py – Detect whether the message is Arabic or English
Fast regex approach — no external library needed.
"""

import re

ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF]")


def detect_language(text: str, hint: str = "auto") -> str:
    """Returns 'ar' or 'en'."""
    if hint in ("ar", "en"):
        return hint
    ar_chars = len(ARABIC_PATTERN.findall(text))
    return "ar" if ar_chars > len(text) * 0.2 else "en"
