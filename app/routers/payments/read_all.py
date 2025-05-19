from typing import Annotated

import fastapi
from fastapi import Depends, Request, status

from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import payments_repo

read_payments_router = fastapi.APIRouter()


@read_payments_router.get(SETTINGS.urls.payments)
def read_all(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
):
    try:
        payments = repo.read_all()
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_payments,
            context={
                "payments": payments,
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
