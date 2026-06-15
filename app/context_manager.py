"""
context_manager.py – Short-term session memory (in-memory, per session_id)
Stores last N turns so the chatbot can follow multi-turn conversations.
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from app.config import settings


@dataclass
class Turn:
    user: str
    bot_intent: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ── In-memory store ────────────────────────────────────────────────────────────
_sessions: dict[str, deque] = {}


def add_turn(session_id: str, user_message: str, bot_intent: str):
    if session_id not in _sessions:
        _sessions[session_id] = deque(maxlen=settings.CONTEXT_MAX_TURNS)
    _sessions[session_id].append(Turn(user=user_message, bot_intent=bot_intent))


def get_context(session_id: str) -> list[Turn]:
    return list(_sessions.get(session_id, []))


def last_intent(session_id: str) -> str | None:
    ctx = get_context(session_id)
    if ctx:
        return ctx[-1].bot_intent
    return None
