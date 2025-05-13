from typing import Annotated

import fastapi
from fastapi import Depends, Request

from app.repositories.payments import PaymentRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import payments_repo

payments_dashboard_router = fastapi.APIRouter()


@payments_dashboard_router.get(SETTINGS.urls.payments_dashboard)
def dashboard_for_all_years(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
):
    payments = repo.get_all_payments()
    dashboard = repo.get_dashboard(
        request=request,
        payments=payments,
    )
    dashboard["all_years"] = repo.get_all_years()
    dashboard["header_text"] = "Расходы за всё время"

    return TEMPLATES.TemplateResponse(
        request, SETTINGS.templates.payments_dashboard, context=dashboard
    )


@payments_dashboard_router.get(SETTINGS.urls.total_payments_monthly)
def read_monthly_payments_breakdown(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
):
    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.payments_dashboard_yearly,
        context={
            "total_per_month": repo.get_monthly_payments(
                repo.get_all_payments()
            ),
        },
    )


@payments_dashboard_router.get(SETTINGS.urls.payments_dashboard_yearly)
def read_all_payments_per_year(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
    year: int,
):
    payments = repo.get_payments_per_year(year)
    dashboard = repo.get_dashboard(
        request=request, payments=payments, year=year
    )
    dashboard["header_text"] = f"Общие расходы за {year} год"

    return TEMPLATES.TemplateResponse(
        request, SETTINGS.templates.payments_dashboard_yearly, context=dashboard
    )


@payments_dashboard_router.get(SETTINGS.urls.payments_dashboard_monthly)
def read_all_payments_per_month(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
    year: int,
    month: int,
):
    payments = repo.get_payments_per_month(year=year, month=month)
    dashboard = repo.get_dashboard(
        request=request, payments=payments, year=year, month=month
    )

    return TEMPLATES.TemplateResponse(
        request,
        SETTINGS.templates.payments_dashboard_monthly,
        context=dashboard,
    )
