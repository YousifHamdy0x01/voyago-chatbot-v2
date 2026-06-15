"""
voyago_api.py – Async client for the Voyago backend API
Endpoints:
  GET /hotels/{id}       → hotel details
  GET /Attractions/{id}  → attraction details
  GET /Restaurants/{id}  → restaurant details
  GET /TourGuides/{id}   → tour guide details
  GET /hotels            → list all hotels
  GET /Attractions       → list all attractions
"""

import httpx
from app.config import settings
import logging

logger = logging.getLogger("voyago_api")

BASE = settings.VOYAGO_API_BASE
TIMEOUT = 8.0  # seconds


async def _get(path: str) -> dict | list | None:
    """Generic async GET with full error handling."""
    url = f"{BASE}{path}"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching {url}")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP {e.response.status_code} for {url}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return None


# ── Public helpers ────────────────────────────────────────────────────────────

async def get_hotels() -> list:
    data = await _get(settings.HOTELS_ENDPOINT)
    return data if isinstance(data, list) else []


async def get_hotel(hotel_id: int) -> dict | None:
    return await _get(f"{settings.HOTELS_ENDPOINT}/{hotel_id}")


async def get_attractions() -> list:
    data = await _get(settings.ATTRACTIONS_ENDPOINT)
    return data if isinstance(data, list) else []


async def get_attraction(attr_id: int) -> dict | None:
    return await _get(f"{settings.ATTRACTIONS_ENDPOINT}/{attr_id}")


async def get_restaurants() -> list:
    data = await _get(settings.RESTAURANTS_ENDPOINT)
    return data if isinstance(data, list) else []


async def get_restaurant(rest_id: int) -> dict | None:
    return await _get(f"{settings.RESTAURANTS_ENDPOINT}/{rest_id}")


async def get_tour_guides() -> list:
    data = await _get(settings.TOURGUIDES_ENDPOINT)
    return data if isinstance(data, list) else []


async def get_tour_guide(guide_id: int) -> dict | None:
    return await _get(f"{settings.TOURGUIDES_ENDPOINT}/{guide_id}")
