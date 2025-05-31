import fastapi

from app.routers.income.create import create_income_router
from app.routers.income.delete import delete_income_router

income_router = fastapi.APIRouter(tags=["income"])
income_router.include_router(create_income_router)
income_router.include_router(delete_income_router)
