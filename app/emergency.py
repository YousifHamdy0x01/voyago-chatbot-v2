"""
emergency.py – Fast-path emergency detection (runs BEFORE the NLP model)
Ensures sub-100ms response for critical situations (NFR4)
"""

import re

# ─── Emergency keyword lists ──────────────────────────────────────────────────
EMERGENCY_KEYWORDS_AR = {
    "إسعاف", "اسعاف", "الإسعاف", "مستشفى", "مستشفي", "طوارئ",
    "حادث", "شرطة", "شرطه", "نجدة", "نجده", "النجدة", "مساعدة",
    "مساعده", "بلاغ", "أمن", "امن", "المطافئ", "طبية", "دكتور",
    "صيدلية", "صيدليه", "ورطة", "بسرعة", "سقوط", "غرق", "حريق",
}

EMERGENCY_KEYWORDS_EN = {
    "emergency", "ambulance", "hospital", "police", "accident",
    "fire", "help", "urgent", "911", "doctor", "medical",
    "security", "danger", "injured", "bleeding", "crash",
    "rescue", "sos", "drowning", "pharmacy", "quickly",
}

# Phone numbers to show immediately
EMERGENCY_RESPONSE_AR = {
    "message": (
        "🚨 **طوارئ الفيوم**\n\n"
        "- 🚔 **الشرطة / النجدة:** 122\n"
        "- 🚑 **الإسعاف:** 123\n"
        "- 🚒 **المطافئ:** 180\n"
        "- 🏥 **أقرب مستشفى:** مستشفى الفيوم العام\n\n"
        "اتصل فوراً! مساعدة في الطريق."
    ),
    "type": "emergency",
    "intent": "fayoum_emergency",
    "language": "ar",
    "data": {
        "numbers": {
            "police": "122",
            "ambulance": "123",
            "fire": "180"
        },
        "nearest_hospital": "مستشفى الفيوم العام"
    }
}

EMERGENCY_RESPONSE_EN = {
    "message": (
        "🚨 **Fayoum Emergency Contacts**\n\n"
        "- 🚔 **Police:** 122\n"
        "- 🚑 **Ambulance:** 123\n"
        "- 🚒 **Fire Department:** 180\n"
        "- 🏥 **Nearest Hospital:** Fayoum General Hospital\n\n"
        "Call immediately! Help is on the way."
    ),
    "type": "emergency",
    "intent": "fayoum_emergency",
    "language": "en",
    "data": {
        "numbers": {
            "police": "122",
            "ambulance": "123",
            "fire": "180"
        },
        "nearest_hospital": "Fayoum General Hospital"
    }
}


def detect_emergency(text: str) -> dict | None:
    """
    Returns an emergency response dict immediately if any emergency
    keyword is found. Returns None if no emergency detected.
    This runs BEFORE the NLP model — zero model overhead.
    """
    normalized = text.lower().strip()
    tokens = set(re.split(r"[\s،,\.!؟?]+", normalized))

    # Check Arabic keywords
    if tokens & EMERGENCY_KEYWORDS_AR:
        return EMERGENCY_RESPONSE_AR

    # Check English keywords
    if tokens & EMERGENCY_KEYWORDS_EN:
        return EMERGENCY_RESPONSE_EN

    return None
