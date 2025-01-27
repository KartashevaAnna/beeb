from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers.ping_router import ping_router
from app.settings import ENGINE, SETTINGS


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # pragma: no cover
    ENGINE.dispose()  # pragma: no cover


def build_app():
    app = FastAPI(debug=SETTINGS.server.debug, lifespan=lifespan)
    app.include_router(ping_router)
    return app
