from typing import Annotated

import fastapi
from fastapi import Depends, Request

from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import payments_repo

total_payments_router = fastapi.APIRouter()


@total_payments_router.get(SETTINGS.urls.total_payments)
def read_all_payments(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
):
    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.total_payments,
        context={
            "request": request,
            "total": repo.get_total(),
            "total_per_month": repo.get_total_per_month(),
            "total_per_day": repo.get_total_per_day_overall(),
            "total_shares": list(
                repo.get_total_monthly_payments_shares().items()
            ),
        },
    )


@total_payments_router.get(SETTINGS.urls.total_payments_monthly)
def read_monthly_payments_breakdown(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
):
    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.total_payments_monthly,
        context={
            "request": request,
            "total_per_month": repo.get_total_per_month(),
        },
    )
