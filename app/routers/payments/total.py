from typing import Annotated

import fastapi
from fastapi import Depends, Request

from app.repositories.payments import PaymentRepo
from app.routers.auth_router import authenticate
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import payments_repo

payments_dashboard_router = fastapi.APIRouter()


@payments_dashboard_router.get(SETTINGS.urls.payments_dashboard)
@authenticate
def dashboard_for_all_years(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
    user_id: int | None = None,
):
    payments = repo.get_all_payments(user_id)
    dashboard = repo.get_dashboard(
        request=request,
        payments=payments,
        user_id=user_id,
    )
    dashboard["all_years"] = repo.get_all_years(user_id)
    dashboard["header_text"] = "Расходы за всё время"

    return TEMPLATES.TemplateResponse(
        request, SETTINGS.templates.payments_dashboard, context=dashboard
    )


@payments_dashboard_router.get(SETTINGS.urls.total_payments_monthly)
@authenticate
def read_monthly_payments_breakdown(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
    user_id: int | None = None,
):
    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.payments_dashboard_yearly,
        context={
            "total_per_month": repo.get_monthly_payments(
                repo.get_all_payments(user_id)
            ),
        },
    )


@payments_dashboard_router.get(SETTINGS.urls.payments_dashboard_yearly)
@authenticate
def read_all_payments_per_year(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
    year: int,
    user_id: int | None = None,
):
    payments = repo.get_payments_per_year(year=year, user_id=user_id)
    dashboard = repo.get_dashboard(
        request=request, payments=payments, year=year, user_id=user_id
    )
    dashboard["header_text"] = f"Общие расходы за {year} год"

    return TEMPLATES.TemplateResponse(
        request, SETTINGS.templates.payments_dashboard_yearly, context=dashboard
    )


@payments_dashboard_router.get(SETTINGS.urls.payments_dashboard_monthly)
@authenticate
def read_all_payments_per_month(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
    year: int,
    month: int,
    user_id: int | None = None,
):
    payments = repo.get_payments_per_month(
        year=year, month=month, user_id=user_id
    )
    dashboard = repo.get_dashboard(
        request=request,
        payments=payments,
        year=year,
        month=month,
        user_id=user_id,
    )

    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.payments_dashboard_monthly,
        context=dashboard,
    )
