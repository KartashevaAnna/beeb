from fastapi import APIRouter

from app.settings import SETTINGS

ping_router = APIRouter(tags=["Ping"])


@ping_router.get(SETTINGS.urls.ping)
def ping():
    return "Pong"
