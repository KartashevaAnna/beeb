import datetime
from typing import Annotated

import fastapi
from fastapi import Depends, Request

from app.repositories.payments import PaymentRepo
from app.schemas.dates import DateFilter
from app.settings import SETTINGS, TEMPLATES
from app.utils.constants import INT_TO_MONTHES
from app.utils.dependencies import payments_repo
from app.utils.tools.helpers import get_number_for_db, get_readable_price

default_page_router = fastapi.APIRouter()


@default_page_router.get(SETTINGS.urls.start_page)
def read_all_payments_per_month(
    repo: Annotated[PaymentRepo, Depends(payments_repo)],
    request: Request,
):
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    max_date = repo.get_max_date(limit=DateFilter(year=year, month=month))
    min_date = repo.get_min_date(limit=DateFilter(year=year, month=month))
    total_days = repo.get_total_days(max_date=max_date, min_date=min_date)
    total = repo.get_total(repo.get_payments_per_month(year=year, month=month))
    numeric_total = get_number_for_db(total)
    total_per_day = repo.get_total_per_day(
        total=numeric_total, total_days=total_days
    )

    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.payments_dashboard_monthly,
        context={
            "request": request,
            "total": total,
            "total_per_month": repo.get_monthly_payments(
                year=year,
                payments=repo.get_payments_per_month(year=year, month=month),
            ),
            "total_per_day": get_readable_price(total_per_day)
            if total_per_day
            else None,
            "total_shares": list(
                repo.get_total_monthly_payments_shares(
                    repo.get_payments_per_month(year=year, month=month)
                ).items()
            ),
            "header_text": f"За {INT_TO_MONTHES[month]} {year} года: {total}",
        },
    )
