from typing import Annotated

import fastapi
from fastapi import Depends, HTTPException, Request, status

from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import payments_repo

read_payment_router = fastapi.APIRouter()


@read_payment_router.get(SETTINGS.urls.payment)
def read_payment(
    payment_id: int,
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
):
    try:
        if not (payment := repo.read(payment_id)):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "payment not found")
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_payment,
            context={
                "request": request,
                "payment": payment,
                "form_disabled": True,
            },
        )
    except HTTPException as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_payment,
            context={
                "request": request,
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_payment,
            context={
                "request": request,
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
