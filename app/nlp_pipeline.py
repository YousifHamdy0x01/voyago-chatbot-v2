"""
nlp_pipeline.py – The Core Logic (Layer 2)
Orchestrates: Emergency Path → Intent Classification → API Fetch → Response Build
"""

import asyncio
from app.emergency import detect_emergency
from app.intent_classifier import IntentClassifier
from app.context_manager import add_turn, last_intent
from app.language import detect_language
from app.response_builder import (
    build_hotels_response,
    build_attractions_response,
    build_fallback,
)
import app.voyago_api as api

CONFIDENCE_THRESHOLD = 0.45  # below this → fallback


class NLPPipeline:
    """
    3-path processor:
      1. Emergency Fast Path  (keyword-based, no model)
      2. Intent Classification (TF-IDF + LogReg)
      3. Fallback              (smart suggestions)
    """

    def __init__(self):
        print("[NLPPipeline] Loading intent classifier …")
        self.classifier = IntentClassifier()
        print("[NLPPipeline] Ready.")

    async def process(self, message: str, session_id: str, lang_hint: str = "auto") -> dict:
        # ── Detect language ────────────────────────────────────────────────
        lang = detect_language(message, lang_hint)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # PATH 1 – EMERGENCY (fast, synchronous keyword check)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        emergency = detect_emergency(message)
        if emergency:
            add_turn(session_id, message, "fayoum_emergency")
            return emergency

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # PATH 2 – INTENT CLASSIFICATION
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        intent, confidence = self.classifier.predict(message)

        # Context boost: if last intent was hotels and new message is short/vague
        # (e.g. "tell me more"), keep the same intent
        if confidence < CONFIDENCE_THRESHOLD:
            prev = last_intent(session_id)
            if prev and prev != "unknown":
                intent = prev
                confidence = CONFIDENCE_THRESHOLD  # promote with context

        # ── Route by intent ────────────────────────────────────────────────
        if confidence >= CONFIDENCE_THRESHOLD:
            result = await self._route(intent, lang, session_id, message)
            add_turn(session_id, message, intent)
            return result

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # PATH 3 – FALLBACK (smart suggestions, not a blank apology)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        add_turn(session_id, message, "unknown")
        return build_fallback(lang)

    async def _route(self, intent: str, lang: str, session_id: str, message: str) -> dict:
        """Fetch data from Voyago API and build the structured response."""

        if intent == "fayoum_hotels":
            hotels = await api.get_hotels()
            return build_hotels_response(lang, hotels)

        elif intent == "fayoum_attractions":
            attractions = await api.get_attractions()
            return build_attractions_response(lang, attractions)

        elif intent == "fayoum_emergency":
            # Shouldn't reach here (caught in Path 1) but handle gracefully
            from app.emergency import EMERGENCY_RESPONSE_AR, EMERGENCY_RESPONSE_EN
            return EMERGENCY_RESPONSE_AR if lang == "ar" else EMERGENCY_RESPONSE_EN

        else:
            return build_fallback(lang)
