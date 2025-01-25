from fastapi import FastAPI

from app.routers.ping_router import ping_router


def build_app():
    app = FastAPI()
    app.include_router(ping_router)
    return app
