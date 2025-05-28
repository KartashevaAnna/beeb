from typing import Annotated

import fastapi
from fastapi import Depends, Request, status

from app.repositories.payments import PaymentRepo
from app.routers.auth_router import authenticate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import payments_repo

read_payments_router = fastapi.APIRouter()


@read_payments_router.get(SETTINGS.urls.payments)
@authenticate
def read_all(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
    user_id: int | None = None,
):
    try:
        payments = repo.read_all(user_id)
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_payments,
            context={
                "payments": payments,
                "create": SETTINGS.urls.select_food_non_food,
                "update": SETTINGS.urls.update_payment_core,
                "delete": SETTINGS.urls.delete_payment_core,
            },
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_payments,
            context={
                "payments": [],
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
