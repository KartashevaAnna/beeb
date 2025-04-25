from typing import Annotated

import fastapi
from fastapi import Depends, Request

from app.repositories.payments import PaymentRepo
from app.schemas.dates import DateFilter
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import payments_repo
from app.utils.tools.helpers import get_number_for_db, get_readable_price

payments_dashboard_router = fastapi.APIRouter()


@payments_dashboard_router.get(SETTINGS.urls.payments_dashboard)
def read_all_payments(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
):
    total = repo.get_total(repo.get_all_payments())
    numeric_total = get_number_for_db(total)
    max_date = repo.get_max_date(limit=DateFilter(year=None, month=None))
    min_date = repo.get_min_date(limit=DateFilter(year=None, month=None))
    total_days = repo.get_total_days(max_date, min_date)
    total_per_day = repo.get_total_per_day(
        total=numeric_total, total_days=total_days
    )
    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.payments_dashboard,
        context={
            "request": request,
            "total": total,
            "total_per_month": repo.get_monthly_payments(
                repo.get_all_payments()
            ),
            "total_per_day": get_readable_price(total_per_day)
            if total_per_day
            else None,
            "all_years": repo.get_all_years(),
            "total_shares": list(
                repo.get_total_monthly_payments_shares(
                    repo.get_all_payments()
                ).items()
            ),
            "header_text": "Расходы за всё время наблюдений",
        },
    )


@payments_dashboard_router.get(SETTINGS.urls.total_payments_monthly)
def read_monthly_payments_breakdown(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
):
    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.payments_dashboard_yearly,
        context={
            "request": request,
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
    max_date = repo.get_max_date(limit=DateFilter(year=year))
    min_date = repo.get_min_date(limit=DateFilter(year=year))
    total_days = repo.get_total_days(max_date=max_date, min_date=min_date)
    total = repo.get_total(repo.get_payments_per_year(year))
    numeric_total = get_number_for_db(total)
    total_per_day = repo.get_total_per_day(
        total=numeric_total, total_days=total_days
    )

    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.payments_dashboard_yearly,
        context={
            "request": request,
            "total": total,
            "total_per_month": repo.get_monthly_payments(
                repo.get_payments_per_year(year)
            ),
            "total_per_day": get_readable_price(total_per_day)
            if total_per_day
            else None,
            "total_shares": list(
                repo.get_total_monthly_payments_shares(
                    repo.get_payments_per_year_with_category(year)
                ).items()
            ),
            "header_text": f"Общие расходы за {year} год",
        },
    )
