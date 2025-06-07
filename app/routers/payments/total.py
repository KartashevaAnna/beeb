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
from app.utils.tools.helpers import (
    get_current_year_and_month,
    get_max_date_from_year_and_month,
    get_max_date_from_year_and_month_datetime_format,
    get_min_date_from_year_and_month_datetime_format,
)

payments_dashboard_router = APIRouter()


@payments_dashboard_router.get(SETTINGS.urls.payments_dashboard)
@authenticate
def dashboard_for_all_years(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
    user_id: int | None = None,
):
    try:
        max_date = repo.get_max_date_overall(user_id)
        min_date = repo.get_min_date_overall(user_id)

        payments = repo.read_all_between_dates(
            user_id=user_id, max_date=max_date, min_date=min_date
        )

        dashboard = repo.get_dashboard(
            payments=payments,
            user_id=user_id,
            max_date=max_date,
            min_date=min_date,
        )
        dashboard["all_years"] = repo.get_all_years(
            user_id=user_id, payments=payments
        )
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


@payments_dashboard_router.get(SETTINGS.urls.payments_dashboard_yearly)
@authenticate
def read_all_payments_per_year(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
    year: int,
    user_id: int | None = None,
):
    try:
        max_date = get_max_date_from_year_and_month_datetime_format(
            year=year, month=12
        )
        min_date = get_min_date_from_year_and_month_datetime_format(
            year=year, month=1
        )
        payments = repo.read_all_between_dates(
            user_id=user_id, max_date=max_date, min_date=min_date
        )
        dashboard = repo.get_dashboard(
            payments=payments,
            user_id=user_id,
            max_date=max_date,
            min_date=min_date,
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
        max_date = get_max_date_from_year_and_month_datetime_format(
            year=year, month=month
        )
        min_date = get_min_date_from_year_and_month_datetime_format(
            year=year, month=month
        )
        payments = repo.read_all_between_dates(
            user_id=user_id, max_date=max_date, min_date=min_date
        )
        dashboard = repo.get_dashboard(
            payments=payments,
            user_id=user_id,
            max_date=max_date,
            min_date=min_date,
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
