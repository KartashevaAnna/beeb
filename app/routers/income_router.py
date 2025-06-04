from fastapi import APIRouter

from app.routers.income.create import create_income_router
from app.routers.income.delete import delete_income_router
from app.routers.income.update import update_income_router

income_router = APIRouter(tags=["income"])
income_router.include_router(create_income_router)
income_router.include_router(delete_income_router)
income_router.include_router(update_income_router)
