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
    # try:
    payments = repo.get_all_payments(user_id)
    return payments
    # payments = repo.read_all(user_id)

    #     return TEMPLATES.TemplateResponse(
    #         request,
    #         SETTINGS.templates.read_payments,
    #         context={
    #             "payments": payments,
    #             "create": SETTINGS.urls.select_income_expense,
    #             "update_payment": SETTINGS.urls.update_payment_core,
    #             "delete_payment": SETTINGS.urls.delete_payment_core,
    #             "delete_income": SETTINGS.urls.delete_income_core,
    #         },
    #     )
    # except Exception as exc:
    #     return TEMPLATES.TemplateResponse(
    #         request,
    #         SETTINGS.templates.read_payments,
    #         context={
    #             "payments": [],
    #             "exception": f"Ошибка: {str(exc)}",
    #         },
    #         status_code=status.HTTP_501_NOT_IMPLEMENTED,
    #     )
