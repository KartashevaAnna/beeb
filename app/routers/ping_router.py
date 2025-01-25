import fastapi

from app.settings import SETTINGS

ping_router = fastapi.APIRouter(tags=["Ping"])


@ping_router.get(SETTINGS.urls.ping)
def ping():
    return "Pong"
