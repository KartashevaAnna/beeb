from datetime import datetime
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends, Request, status

from app.exceptions import BeebError
from app.repositories.income import IncomeRepo
from app.repositories.payments import PaymentRepo
from app.routers.auth_router import authenticate
from app.schemas.dates import DateFilter
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import income_repo, payments_repo
from app.utils.tools.helpers import get_current_year_and_month

payments_dashboard_router = APIRouter()


@payments_dashboard_router.get(SETTINGS.urls.payments_dashboard)
@authenticate
def dashboard_for_all_years(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    repo2: Annotated[IncomeRepo, Depends(income_repo)],
    request: Request,
    user_id: int | None = None,
):
    try:
        current_year, current_month = get_current_year_and_month()

        payments = repo.read_all(user_id)

        dashboard = repo.get_dashboard(
            request=request,
            payments=payments,
            user_id=user_id,
            year=current_year,
            month=current_month,
        )
        dashboard["all_years"] = repo.get_all_years(user_id)
        dashboard["header_text"] = "Расходы за всё время"

        return TEMPLATES.TemplateResponse(
            request, SETTINGS.templates.payments_dashboard, context=dashboard
        )
    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.payments_dashboard_monthly,
            context={
                "exception": exc.detail,
            },
            status_code=exc.status_code,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.payments_dashboard_monthly,
            context={
                "exception": f"Ошибка: {str(exc)}",
                "status_code": status.HTTP_501_NOT_IMPLEMENTED,
            },
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
    try:
        payments = repo.get_payments_per_year(year=year, user_id=user_id)
        dashboard = repo.get_dashboard(
            request=request, payments=payments, year=year, user_id=user_id
        )
        dashboard["header_text"] = f"Расходы за {year} год"

        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.payments_dashboard_yearly,
            context=dashboard,
        )
    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.payments_dashboard_yearly,
            context={
                "exception": exc.detail,
            },
            status_code=exc.status_code,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.payments_dashboard_yearly,
            context={
                "exception": f"Ошибка: {str(exc)}",
                "status_code": status.HTTP_501_NOT_IMPLEMENTED,
            },
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
    try:
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
    except BeebError as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.payments_dashboard_monthly,
            context={
                "exception": exc.detail,
            },
            status_code=exc.status_code,
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            request,
            SETTINGS.templates.payments_dashboard_monthly,
            context={
                "exception": f"Ошибка: {str(exc)}",
                "status_code": status.HTTP_501_NOT_IMPLEMENTED,
            },
        )
