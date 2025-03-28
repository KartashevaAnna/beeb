from typing import Annotated

import fastapi
from fastapi import Depends, Request

from app.repositories.expenses import ExpensesRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import expenses_repo

total_expenses_router = fastapi.APIRouter()


@total_expenses_router.get(SETTINGS.urls.total_expenses)
def read_all(
    repo: Annotated[ExpensesRepo, Depends(expenses_repo)],
    request: Request,
):
    return TEMPLATES.TemplateResponse(
        SETTINGS.templates.total_expenses,
        context={
            "request": request,
            "total": repo.get_total(),
            "total_per_month": repo.get_total_per_month(),
            "total_per_day": repo.get_total_per_day_overall(),
            "total_shares": list(
                repo.get_total_monthly_expenses_shares().items()
            ),
        },
    )
