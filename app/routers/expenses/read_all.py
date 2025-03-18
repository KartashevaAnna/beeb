from typing import Annotated

import fastapi
from fastapi import Depends, Request, Response, status

from app.repositories.expenses import ExpensesRepo
from app.settings import SETTINGS, TEMPLATES
from app.utils.dependencies import expenses_repo

read_expenses_router = fastapi.APIRouter()


@read_expenses_router.get(SETTINGS.urls.expenses)
def read_all(
    repo: Annotated[ExpensesRepo, Depends(expenses_repo)],
    request: Request,
    response: Response,
):
    try:
        expenses = repo.read_all()
        total = repo.get_total()
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_expenses,
            context={"request": request, "expenses": expenses, "total": total},
        )
    except Exception as exc:
        return TEMPLATES.TemplateResponse(
            SETTINGS.templates.read_expenses,
            context={
                "request": request,
                "expenses": [],
                "exception": f"There was an error: {str(exc)}",
            },
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
        )
