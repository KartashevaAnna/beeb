import fastapi

from app.routers.categories.create import create_categories_router
from app.routers.categories.read_all import read_categories_router
from app.routers.categories.read_one import read_category_router
from app.routers.categories.update import update_category_router

categories_router = fastapi.APIRouter(tags=["Categories"])
categories_router.include_router(create_categories_router)
categories_router.include_router(update_category_router)
categories_router.include_router(read_categories_router)
categories_router.include_router(read_category_router)
