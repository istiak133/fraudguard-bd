from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import APP_VERSION
from app.services import whatsapp

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Is the server running?")
def health_check():
    return {
        "status": "ok",
        "version": APP_VERSION,
        "whatsapp_mode": "live" if whatsapp.is_live() else "mock",
        "time": datetime.now(timezone.utc).isoformat(),
    }
