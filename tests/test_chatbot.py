"""
tests/test_chatbot.py – Quality & Readiness Checklist Tests
Run: pytest tests/ -v
"""

import pytest
import asyncio
from app.emergency import detect_emergency
from app.language import detect_language
from app.intent_classifier import IntentClassifier
from app.response_builder import build_fallback, build_hotels_response, build_attractions_response


# ── 1. Emergency Detection Tests (NFR4) ───────────────────────────────────────
class TestEmergency:
    def test_arabic_emergency_ambulance(self):
        result = detect_emergency("محتاج إسعاف الآن")
        assert result is not None
        assert result["type"] == "emergency"
        assert "123" in result["message"]

    def test_arabic_emergency_police(self):
        result = detect_emergency("عايز شرطة بسرعة")
        assert result is not None
        assert result["type"] == "emergency"

    def test_english_emergency(self):
        result = detect_emergency("I need an ambulance now!")
        assert result is not None
        assert result["type"] == "emergency"
        assert result["language"] == "en"

    def test_no_emergency_normal_text(self):
        result = detect_emergency("أريد حجز فندق في الفيوم")
        assert result is None

    def test_emergency_data_has_numbers(self):
        result = detect_emergency("fire in the building help")
        assert "numbers" in result["data"]
        assert result["data"]["numbers"]["police"] == "122"
        assert result["data"]["numbers"]["ambulance"] == "123"


# ── 2. Language Detection Tests ───────────────────────────────────────────────
class TestLanguage:
    def test_arabic_detected(self):
        assert detect_language("أريد حجز فندق") == "ar"

    def test_english_detected(self):
        assert detect_language("I want to book a hotel") == "en"

    def test_mixed_defaults_to_ar(self):
        # More Arabic chars → Arabic
        assert detect_language("أريد hotel in الفيوم") == "ar"

    def test_hint_overrides(self):
        assert detect_language("hello", hint="ar") == "ar"
        assert detect_language("مرحبا", hint="en") == "en"


# ── 3. Intent Classifier Tests ───────────────────────────────────────────────
class TestIntentClassifier:
    @pytest.fixture(scope="class")
    def clf(self):
        return IntentClassifier()

    def test_hotel_intent_arabic(self, clf):
        intent, conf = clf.predict("عايز فندق في الفيوم")
        assert intent == "fayoum_hotels"
        assert conf > 0.4

    def test_hotel_intent_english(self, clf):
        intent, conf = clf.predict("Fayoum hotels kindly")
        assert intent == "fayoum_hotels"

    def test_attraction_intent_arabic(self, clf):
        intent, conf = clf.predict("عايز أزور وادي الريان")
        assert intent == "fayoum_attractions"

    def test_attraction_intent_english(self, clf):
        intent, conf = clf.predict("قصر قارون activities help")
        assert intent == "fayoum_attractions"

    def test_emergency_intent(self, clf):
        intent, conf = clf.predict("حادث طريق مساعدة")
        assert intent == "fayoum_emergency"


# ── 4. Response Structure Tests ───────────────────────────────────────────────
class TestResponseStructure:
    """
    Ensure every response has `message`, `type`, `data`, `intent`, `language`
    so the frontend can always render correctly.
    """

    REQUIRED_KEYS = {"message", "type", "data", "intent", "language"}

    def test_fallback_ar_has_all_keys(self):
        resp = build_fallback("ar")
        assert self.REQUIRED_KEYS.issubset(resp.keys())

    def test_fallback_en_has_all_keys(self):
        resp = build_fallback("en")
        assert self.REQUIRED_KEYS.issubset(resp.keys())

    def test_hotels_response_has_all_keys(self):
        mock_hotels = [{"id": 13, "name": "أوبرج الفيوم", "rating": 4.5}]
        resp = build_hotels_response("ar", mock_hotels)
        assert self.REQUIRED_KEYS.issubset(resp.keys())
        assert resp["type"] == "card"
        assert len(resp["data"]["items"]) == 1

    def test_attractions_response_has_all_keys(self):
        mock_attrs = [{"id": 16, "name": "وادي الريان"}]
        resp = build_attractions_response("en", mock_attrs)
        assert self.REQUIRED_KEYS.issubset(resp.keys())
        assert resp["type"] == "card"

    def test_hotels_link_format(self):
        mock_hotels = [{"id": 13, "name": "Test Hotel"}]
        resp = build_hotels_response("en", mock_hotels)
        assert "voyagoo.runasp.net/hotels/13" in resp["data"]["items"][0]["link"]

    def test_fallback_has_suggestions(self):
        resp = build_fallback("ar")
        assert "suggestions" in resp["data"]
        assert len(resp["data"]["suggestions"]) > 0


# ── 5. Fallback Intelligence Test ─────────────────────────────────────────────
class TestFallback:
    def test_fallback_not_just_apology(self):
        resp = build_fallback("ar")
        # Must have actionable suggestions, not just "sorry"
        assert "فنادق" in resp["message"] or "معالم" in resp["message"]

    def test_fallback_type_is_fallback(self):
        resp = build_fallback("en")
        assert resp["type"] == "fallback"
