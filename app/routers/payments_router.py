import fastapi

from app.routers.payments.create import create_payments_router
from app.routers.payments.delete import delete_payments_router
from app.routers.payments.read_all import read_payments_router
from app.routers.payments.total import payments_dashboard_router
from app.routers.payments.update import update_payment_router

payments_router = fastapi.APIRouter(tags=["payments"])
payments_router.include_router(create_payments_router)
payments_router.include_router(read_payments_router)
payments_router.include_router(update_payment_router)
payments_router.include_router(delete_payments_router)
payments_router.include_router(payments_dashboard_router)
