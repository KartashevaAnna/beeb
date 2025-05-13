from typing import Annotated

import fastapi
from fastapi import Depends, Request, status
from fastapi.responses import RedirectResponse

from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import payments_repo

delete_payments_router = fastapi.APIRouter()


@delete_payments_router.get(SETTINGS.urls.delete_payment)
def delete_template(
    request: Request,
):
    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.delete_payment,
    )


@delete_payments_router.post(SETTINGS.urls.delete_payment)
def delete_payment(
    payment_id: int,
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
):
    try:
        repo.delete(payment_id)
        return RedirectResponse(
            url=SETTINGS.urls.payments, status_code=status.HTTP_303_SEE_OTHER
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_payment,
            context={
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
