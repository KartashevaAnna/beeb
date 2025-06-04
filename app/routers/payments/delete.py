from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends, Request, status
from fastapi.responses import RedirectResponse

from app.exceptions import BeebError
from app.repositories.payments import PaymentRepo
from app.routers.auth_router import authenticate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import payments_repo

delete_payments_router = APIRouter()


@delete_payments_router.post(SETTINGS.urls.delete_payment)
@authenticate
def delete_payment(
    payment_id: int,
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
    user_id: int | None = None,
):
    try:
        repo.delete(payment_id=payment_id, user_id=user_id)
        return RedirectResponse(
            url=SETTINGS.urls.payments, status_code=status.HTTP_303_SEE_OTHER
        )
    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.delete_payment,
            context={
                "exception": exc.detail,
            },
            status_code=exc.status_code,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.read_payment,
            context={
                "exception": f"Ошибка: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
