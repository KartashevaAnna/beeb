import locale
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.exceptions import beeb_exception_handler
from app.routers.categories_router import categories_router
from app.routers.default_page_router import default_page_router
from app.routers.dev_router import dev_router
from app.routers.payments_router import payments_router
from app.routers.ping_router import ping_router
from app.settings import ENGINE


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield  # pragma: no cover
    ENGINE.dispose()  # pragma: no cover


def build_app():
    app = FastAPI(lifespan=lifespan)
    app.add_exception_handler(Exception, beeb_exception_handler)
    app.include_router(default_page_router)
    app.include_router(ping_router)
    app.include_router(payments_router)
    app.include_router(categories_router)
    app.include_router(dev_router)

    app.mount("/static", StaticFiles(directory="./app/static/"), name="static")
    app.mount("/css", StaticFiles(directory="./app/static/css"), name="css")
    app.mount("/js", StaticFiles(directory="./app/static/js"), name="js")
    app.mount("/img", StaticFiles(directory="./app/static/images"), name="img")
    locale.setlocale(locale.LC_ALL, "ru_RU.utf8")
    return app
