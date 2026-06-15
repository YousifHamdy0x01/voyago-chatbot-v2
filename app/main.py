"""
Voyago Chatbot - FastAPI Backend
Supports Arabic & English | 3-Layer Architecture
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from app.nlp_pipeline import NLPPipeline
from app.config import settings

app = FastAPI(
    title="Voyago Chatbot API",
    description="AI-powered tourism chatbot for Fayoum - Egypt",
    version="1.0.0"
)

# ─── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── NLP Engine (loaded once at startup) ─────────────────────────────────────
nlp = NLPPipeline()


# ─── Schemas ─────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    language: str = "auto"   # auto | ar | en


class ChatResponse(BaseModel):
    message: str
    type: str          # text | card | emergency | fallback
    data: dict         # extra payload for frontend
    intent: str
    language: str


# ─── Endpoint ────────────────────────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Handles Arabic & English, emergency detection, intent classification,
    context memory, API fetching, and fallback logic.
    """
    try:
        result = await nlp.process(
            message=request.message,
            session_id=request.session_id,
            lang_hint=request.language,
        )
        return ChatResponse(**result)

    except Exception as e:
        # ── Global error guard: chatbot never crashes ──────────────────────
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@app.get("/health")
async def health():
    return {"status": "ok", "model": "voyago-v1"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
