import fastapi

from app.routers.expenses.create import create_expenses_router
from app.routers.expenses.delete import delete_expenses_router
from app.routers.expenses.read import read_expense_router
from app.routers.expenses.read_all import read_expenses_router
from app.routers.expenses.update import update_expenses_router

expenses_router = fastapi.APIRouter(tags=["Expenses"])
expenses_router.include_router(create_expenses_router)
expenses_router.include_router(read_expenses_router)
expenses_router.include_router(read_expense_router)
expenses_router.include_router(update_expenses_router)
expenses_router.include_router(delete_expenses_router)
