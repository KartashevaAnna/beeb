from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers.dev_router import dev_router
from app.routers.expenses_router import expenses_router
from app.routers.ping_router import ping_router
from app.settings import ENGINE, SETTINGS


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # pragma: no cover
    ENGINE.dispose()  # pragma: no cover


def build_app():
    app = FastAPI(debug=SETTINGS.server.debug, lifespan=lifespan)
    app.include_router(ping_router)
    app.include_router(expenses_router)
    app.include_router(dev_router)
    return app
